"""Solar system simulator."""

from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime
import threading
import time

from .nsrdb_data import nsrdb_data, nsrdb_location, nsrdb_start_point
from .data import PVConf
from .battery import Battery
from .inverter import Inverter
from ..config.settings import settings
from ..utils.logger import logger
from ..utils.helpers import find_nearest_timestamp_row
from ..utils.remote_interface import remote_interface_expose
if TYPE_CHECKING:
    from ..time_sim.simulator import TimeSimulator
    from ..houses_loads_sim.simulator import HousesLoadsSimulator


import pandas as pd
import pvlib


@remote_interface_expose
class SolarSystemSimulator:
    """Solar system simulator.

    Args:
        time_sim (TimeSimulator): The time simulator.
        houses_loads_sim (HousesLoadsSimulator): The houses loads simulator instance.
    """
    pv_conf: PVConf
    pv_loc: pvlib.location.Location
    battery: Battery
    inverter: Inverter
    power: float = .0  # Current total DC power given by the panels.
    nsrdb_data_row: pd.Series

    _houses_loads_sim: HousesLoadsSimulator # To store the instance

    # Power flow tracking variables for the current step
    pv_dc_total_generated: float
    ac_load_demand_total: float 
    inverter_night_consumption_ac: float
    ac_supplied_to_load_from_pv: float
    ac_supplied_to_load_from_battery: float
    ac_supplied_to_load_from_grid: float
    dc_power_to_battery_from_pv: float 
    dc_power_from_battery_for_load: float 
    ac_power_exported_to_grid: float
    pv_dc_power_curtailed: float
    unmet_ac_load: float
    battery_soc_percentage: float


    def __init__(self, time_sim: TimeSimulator, houses_loads_sim: HousesLoadsSimulator): # Added houses_loads_sim
        self._time_sim = time_sim
        self._houses_loads_sim = houses_loads_sim # Store the instance

        self.pv_conf = PVConf(
            num_panels=settings.PV_NUM_PANELS,
            panel_area=settings.PV_PANEL_AREA,
            panel_efficiency=settings.PV_EFFICIENCY,
        )

        self.pv_loc = pvlib.location.Location(
            latitude=nsrdb_location['latitude'],
            longitude=nsrdb_location['longitude'],
            tz=nsrdb_location['timezone'],
        )
        self.battery = Battery(init_charge_level=.5)
        
        self.inverter = Inverter(
            paco=settings.INVERTER_NOMINAL_AC_POWER,
            pdco=settings.INVERTER_PDCO,
            eta_inv_nom=settings.INVERTER_ETA_INV_NOM,
            eta_inv_ref=settings.INVERTER_ETA_INV_REF,
            pnt=settings.INVERTER_PNT,
            effective_nominal_efficiency=settings.EFFECTIVE_INVERTER_NOMINAL_EFFICIENCY,
            initial_grid_status=True 
        )
        
        # self.current_ac_load_demand = settings.DEFAULT_AC_LOAD_DEMAND # REMOVED - Load will be live

        self._running = False
        self._dt = 1000 
        
        if settings.CSV_LOGGING:
            csv_header = (
                "Timestamp,"
                "Time of Day,"
                "PV DC Total Generated (W),"
                "AC Load Demand (W),"
                "Inverter Night Consumption AC (W),"
                "AC to Load from PV (W),"
                "AC to Load from Battery (W),"
                "AC to Load from Grid (W),"
                "DC to Battery from PV (W),"
                "DC from Battery for Load (W),"
                "AC Exported to Grid (W),"
                "PV DC Curtailed (W),"
                "Unmet AC Load (W),"
                "Battery Charge Level (Wh),"
                "Battery SOC (%)\n"
            )
            with open(settings.CSV_SSS_LOG_PATH, mode="w", encoding="utf-8") as f:
                f.write(csv_header)
                f.close()

    def start(self, dt: int = None):
        self._running = True
        if not dt:
            dt = self._dt 
        else:
            self._dt = dt

        threading.Thread(
            target=self.update_loop, 
            daemon=True
        ).start()
        logger.info("Solar system simulation started.")

    def pause(self):
        if self._running:
            self._running = False
        logger.info("Solar system simulation paused.")

    def resume(self):
        if not self._running:
            self.start(self._dt)

    def update_loop(self): 
        """Continuously updates the simulation state."""
        while self._running:
            self.perform_update_step()
            time.sleep(self._dt / 1000.0)


    def perform_update_step(self):
        """Performs a single update step of the simulation."""
        elapsed = self._time_sim.get_elapsed()
        timestamp = self._time_sim.get_timestamp(nsrdb_start_point, elapsed)
        self.nsrdb_data_row = find_nearest_timestamp_row(nsrdb_data, timestamp)
        solar_pos = self.pv_loc.get_solarposition(timestamp)

        if self.nsrdb_data_row['Solar Zenith Angle'] > 90:
            poa_irradiance = 0
        else:
            poa_irradiance = pvlib.irradiance.get_total_irradiance(
                surface_tilt=35,
                surface_azimuth=180,
                solar_zenith=self.nsrdb_data_row['Solar Zenith Angle'],
                solar_azimuth=solar_pos['azimuth'],
                dni=self.nsrdb_data_row['DNI'],
                ghi=self.nsrdb_data_row['GHI'],
                dhi=self.nsrdb_data_row['DHI'],
            )['poa_global'].iloc[0]
        
        self.power = poa_irradiance * self.pv_conf.panel_area * \
            self.pv_conf.panel_efficiency * self.pv_conf.num_panels
        self.pv_dc_total_generated = self.power

        dt_seconds = (self._dt / 1000.0) * settings.TIME_FACTOR

        self.inverter_night_consumption_ac = 0.0
        self.ac_supplied_to_load_from_pv = 0.0
        self.ac_supplied_to_load_from_battery = 0.0
        self.ac_supplied_to_load_from_grid = 0.0
        self.dc_power_to_battery_from_pv = 0.0
        self.dc_power_from_battery_for_load = 0.0
        self.ac_power_exported_to_grid = 0.0
        self.pv_dc_power_curtailed = 0.0
        self.unmet_ac_load = 0.0

        pv_dc_available = self.pv_dc_total_generated
        
        # Get live AC load from HousesLoadsSimulator
        current_total_ac_load_from_houses = self._houses_loads_sim.get_system_load() #
        
        current_ac_load_to_meet = current_total_ac_load_from_houses # Base load for this step

        if pv_dc_available <= 0: 
            self.inverter_night_consumption_ac = self.inverter.get_night_consumption()
            current_ac_load_to_meet += self.inverter_night_consumption_ac # Add inverter standby load
        
        self.ac_load_demand_total = current_ac_load_to_meet # For logging
        ac_load_remaining = current_ac_load_to_meet

        if ac_load_remaining > 0 and pv_dc_available > 0:
            dc_power_for_load_from_pv_ideal = self.inverter.get_dc_input_for_ac_output(ac_load_remaining)
            dc_to_inverter_for_load = min(pv_dc_available, dc_power_for_load_from_pv_ideal)
            
            self.ac_supplied_to_load_from_pv = self.inverter.get_ac_output(dc_to_inverter_for_load) 
            
            dc_actually_used_for_load_pv = self.inverter.get_dc_input_for_ac_output(self.ac_supplied_to_load_from_pv)
            pv_dc_available -= dc_actually_used_for_load_pv 
            ac_load_remaining -= self.ac_supplied_to_load_from_pv
            ac_load_remaining = max(0, ac_load_remaining)

        if pv_dc_available > 0 and dt_seconds > 0:
            self.dc_power_to_battery_from_pv = self.battery.charge(pv_dc_available, dt_seconds)
            pv_dc_available -= self.dc_power_to_battery_from_pv
            pv_dc_available = max(0, pv_dc_available)

        if ac_load_remaining > 0 and dt_seconds > 0:
            dc_power_for_load_from_batt_ideal = self.inverter.get_dc_input_for_ac_output(ac_load_remaining)
            self.dc_power_from_battery_for_load = self.battery.discharge(dc_power_for_load_from_batt_ideal, dt_seconds)
            
            if self.dc_power_from_battery_for_load > 0:
                ac_from_battery = self.inverter.get_ac_output(self.dc_power_from_battery_for_load)
                self.ac_supplied_to_load_from_battery = ac_from_battery
                ac_load_remaining -= ac_from_battery
                ac_load_remaining = max(0, ac_load_remaining)

        if pv_dc_available > 0:
            if self.inverter.is_grid_connected:
                self.ac_power_exported_to_grid = self.inverter.get_ac_output(pv_dc_available)
                dc_actually_converted_for_export = self.inverter.get_dc_input_for_ac_output(self.ac_power_exported_to_grid)
                self.pv_dc_power_curtailed = pv_dc_available - dc_actually_converted_for_export
            else: 
                self.pv_dc_power_curtailed = pv_dc_available
        self.pv_dc_power_curtailed = max(0, self.pv_dc_power_curtailed)

        if ac_load_remaining > 0:
            if self.inverter.is_grid_connected:
                self.ac_supplied_to_load_from_grid = ac_load_remaining
                ac_load_remaining = 0
            else: 
                self.unmet_ac_load = ac_load_remaining
                ac_load_remaining = 0
        
        if self.battery.conf.capacity > 0:
            self.battery_soc_percentage = (self.battery.charge_level / self.battery.conf.capacity) * 100
        else:
            self.battery_soc_percentage = 0.0

        if settings.CSV_LOGGING:
            log_data = (
                f"{timestamp},"
                f"{self.nsrdb_data_row['Time of Day']},"
                f"{self.pv_dc_total_generated:.2f},"
                f"{self.ac_load_demand_total:.2f}," # Now reflects live load + inverter night use
                f"{self.inverter_night_consumption_ac:.2f},"
                f"{self.ac_supplied_to_load_from_pv:.2f},"
                f"{self.ac_supplied_to_load_from_battery:.2f},"
                f"{self.ac_supplied_to_load_from_grid:.2f},"
                f"{self.dc_power_to_battery_from_pv:.2f},"
                f"{self.dc_power_from_battery_for_load:.2f},"
                f"{self.ac_power_exported_to_grid:.2f},"
                f"{self.pv_dc_power_curtailed:.2f},"
                f"{self.unmet_ac_load:.2f},"
                f"{self.battery.charge_level:.2f},"
                f"{self.battery_soc_percentage:.2f}\n"
            )
            with open(settings.CSV_SSS_LOG_PATH, mode="a", encoding="utf-8") as f:
                f.write(log_data)
                f.close()

    # Removed set_ac_load_demand method as load is now live

    def set_inverter_grid_status(self, is_connected: bool):
        self.inverter.set_grid_status(is_connected)
        status = "connected" if is_connected else "disconnected"
        logger.info(f"Inverter grid status set to: {status}")
        
    def summary(self) -> str:
        # Fetch live load for summary display
        live_load = self._houses_loads_sim.get_system_load() if self._houses_loads_sim else 0.0 #
        
        return str((
            f"{self.pv_loc}\n"
            f"{self.pv_conf}\n" #
            f"{self.battery.conf}\n" #
            f"{self.battery}\n" #
            f"{self.inverter}\n"
            f"Current Live AC Load from Houses: {live_load:.2f} W\n"
            f"Total AC Load Demand this Step (incl. inverter): {self.ac_load_demand_total:.2f} W\n"
            f"PV DC Power Generated: {self.pv_dc_total_generated:.2f} W\n"
            f"AC Supplied to Load from PV: {self.ac_supplied_to_load_from_pv:.2f} W\n"
            f"AC Supplied to Load from Battery: {self.ac_supplied_to_load_from_battery:.2f} W\n"
            f"AC Supplied to Load from Grid: {self.ac_supplied_to_load_from_grid:.2f} W\n"
            f"AC Exported to Grid: {self.ac_power_exported_to_grid:.2f} W\n"
            f"Unmet AC Load: {self.unmet_ac_load:.2f} W\n"
            f"PV Curtailed: {self.pv_dc_power_curtailed:.2f} W\n"
        ))

    def get_nsrdb_start_point(self) -> datetime:
        return nsrdb_start_point

    def is_running(self) -> bool:
        return self._running