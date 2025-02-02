"""Simulation for the solar system."""

from dataclasses import dataclass
import threading
import time
import os

import pvlib
from pvlib import irradiance

from .sim_time_loc import SimulationOfTimeLocation


@dataclass
class PVConf:
    """PV Configuration.

    Todo:
        * Implement __post_init__ method to assert correct data.

    """

    panels_count: int  #: int: Panels count.
    panel_area: float  #: float: Panel area [m^2].
    panel_efficiency: float  #: float: Panel efficiency multiplier.

    def __post_init__(self):
        pass


class SimulationOfSolarSystem:
    """Simulation for the solar system.

    Args:
        stl (SimulationOfTimeLocation): The :class:`SimulationOfTimeLocation` object.
        pv_conf (PVConf): The :class:`PVConf` for the system.
        log (bool): If True, an csv file will be created and record the system status.

    """

    pv_conf: PVConf  #: PVConf: The :class:`PVConf` for the system.

    #: bool: Whether the simulation is running or paused.
    running: bool = False

    #: float: The current zenith angle for the sun.
    zenith_angle: float = .0

    #: float: The current power given by one panel.
    panel_power: float = .0

    #: float: The current total power given by the panels.
    total_power: float = .0

    #: pvlib.location.Location: The pvlib location object.
    pvloc: pvlib.location.Location

    def __init__(self, stl: SimulationOfTimeLocation, pv_conf: PVConf, log=False):
        self._stl = stl
        self.pv_conf = pv_conf

        self.pvloc = pvlib.location.Location(
            latitude=self._stl.loc_info.lat,
            longitude=self._stl.loc_info.lng,
            tz=self._stl.loc_info.tz_name,
            altitude=self._stl.loc_info.alt,
            name=self._stl.loc_name,
        )

        self._log = log
        if self._log:
            timestamp = self._stl.get_time().strftime("%Y-%m-%d_%H-%M-%S")
            self._log_file_name = f"log_sss_{timestamp}.csv"

    def start(self):
        """Start the simulation."""
        self.running = True

        if self._log:
            if not os.path.exists("logs"):
                os.mkdir("logs")

            if not os.path.exists("logs/sim_solar_system"):
                os.mkdir("logs/sim_solar_system")

            with open(f"logs/sim_solar_system/{self._log_file_name}",
                      mode="w", encoding="utf-8") as log_file:
                columns_line = "elapsed,total_power\n"
                log_file.write(columns_line)
                log_file.close()

        threading.Thread(
            target=self._update,
            kwargs={'dt': 100},
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

    def _update(self, dt: int):
        """Update the simulation every ``dt`` milliseconds.

        Args:
            dt (int): The number of milliseconds to update.

        """
        while self.running:
            curr_elapsed = self._stl.get_elapsed()
            curr_time = self._stl.get_time(curr_elapsed)

            # Get solar position (elevation and azimuth)
            solar_pos = self.pvloc.get_solarposition(curr_time)

            # Calculate the solar zenith angle
            self.zenith_angle = solar_pos['zenith'].iloc[0]

            if self.zenith_angle > 90:
                poa_irradiance = 0
            else:
                # Use a simplified clear-sky model for daytime irradiance
                poa_irradiance = irradiance.get_total_irradiance(
                    surface_tilt=30,  # Assumed fixed tilt for simplicity
                    surface_azimuth=180,  # Facing south
                    solar_zenith=self.zenith_angle,  # Zenith angle from solar position
                    dni=1000,  # Direct normal irradiance (clear sky)
                    ghi=1000,  # Global horizontal irradiance (clear sky)
                    dhi=100,  # Diffuse horizontal irradiance
                    # Azimuth angle from solar position
                    solar_azimuth=solar_pos['azimuth'],
                    dni_extra=1367  # Extra-terrestrial irradiance
                )['poa_global'].iloc[0]

            # Calculate the wattage output of each panel
            self.panel_power = poa_irradiance * self.pv_conf.panel_area * \
                self.pv_conf.panel_efficiency
            self.total_power = self.panel_power * self.pv_conf.panels_count

            if self._log:
                with open(f"logs/sim_solar_system/{self._log_file_name}",
                          mode="a", encoding="utf-8") as log_file:
                    record = f"{curr_elapsed:.2f},{self.total_power:.2f}\n"
                    log_file.write(record)
                    log_file.close()

            time.sleep(dt/1000)
