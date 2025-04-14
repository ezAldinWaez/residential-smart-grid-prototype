"""Solar system simulator."""

from datetime import datetime
import threading
import time
import os

import pandas as pd
import pvlib

from ..config import settings
from ..time_sim import TimeSimulator

from .nsrdb_data import nsrdb_data, nsrdb_location, nsrdb_start_point, find_nearest_timestamp_row
from .data import PVConf
from .battery import Battery


class SolarSystemSimulator:
    """Solar system simulator.

    Args:
        time_sim (TimeSimulator): The time simulator.
    """
    pv_conf: PVConf  #: PVConf: The PV configuration for the system.
    pv_loc: pvlib.location.Location  #: Location: The pvlib location instance.
    battery: Battery  #: Battery: The simulated battery for the system.
    power: float = .0  #: float: The current total power given by the panels.
    nsrdb_data_row: pd.Series  #: Series: The current nsrdb data row.
    #: bool: Whether the simulation is running or paused.
    running: bool = False

    def __init__(self, time_sim: TimeSimulator):
        self._time_sim = time_sim

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

        if settings.CSV_LOGGING:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self._log_fp = f"data/logs/{timestamp}/log_solar_system_sim_{timestamp}.csv"
            if not os.path.exists(f"data/logs/{timestamp}"):
                os.mkdir(f"data/logs/{timestamp}")

    def start(self, dt: int = None):
        """Start the simulation.

        Args:
            dt (int): Update time. [millisecond]
        """
        self.running = True

        if not dt:
            dt = self._dt
        else:
            self._dt = dt

        if settings.CSV_LOGGING:
            with open(self._log_fp, mode="w", encoding="utf-8") as f:
                f.write("elapsed,total_power\n")
                f.close()

        threading.Thread(
            target=self.update,
            kwargs={'dt': dt},
            daemon=True
        ).start()

    def pause(self):
        """Pause the simulation."""
        if self.running:
            self.running = False

    def resume(self):
        """Resume the simulation."""
        if not self.running:
            self.start()

    def update(self, dt: int):
        """Update the simulation every `dt` milliseconds.

        Args:
            dt (int): Update time. [millisecond]
        """
        while self.running:
            elapsed = self._time_sim.get_elapsed()
            curr_datetime = self._time_sim.get_time(nsrdb_start_point, elapsed)

            self.nsrdb_data_row = find_nearest_timestamp_row(
                nsrdb_data, curr_datetime)

            solar_pos = self.pv_loc.get_solarposition(curr_datetime)

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

            if settings.CSV_LOGGING:
                with open(self._log_fp, mode="a", encoding="utf-8") as f:
                    f.write(f"{elapsed:.2f},{self.power:.2f}\n")
                    f.close()

            time.sleep(dt/1000)
