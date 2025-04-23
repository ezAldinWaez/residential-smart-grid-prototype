"""Solar system simulator."""

from datetime import datetime
from .nsrdb_data import nsrdb_data, nsrdb_location, nsrdb_start_point
from .data import PVConf
from .battery import Battery

from ..config import settings
from ..utils import logger, find_nearest_timestamp_row
from ..time_sim import TimeSimulator

import threading
import time

import pandas as pd
import pvlib
import Pyro5.api


@Pyro5.api.expose
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

        self._running = False
        if settings.CSV_LOGGING:
            with open(settings.CSV_SSS_LOG_PATH, mode="w", encoding="utf-8") as f:
                f.write((
                    "Timestamp,"
                    "Time of Day,"
                    "Power\n"
                ))
                f.close()

    def start(self, dt: int = None):
        """Start the simulation.

        Args:
            dt (int): Update time. [millisecond]
        """
        self._running = True

        if not dt:
            dt = self._dt
        else:
            self._dt = dt

        threading.Thread(
            target=self.update,
            kwargs={'dt': dt},
            daemon=True
        ).start()

        logger.info("Solar system simulation started.")

    def pause(self):
        """Pause the simulation."""
        if self._running:
            self._running = False

        logger.info("Solar system simulation paused.")

    def resume(self):
        """Resume the simulation."""
        if not self._running:
            self.start()

    def update(self, dt: int):
        """Update the simulation every `dt` milliseconds.

        Args:
            dt (int): Update time. [millisecond]
        """
        while self._running:
            elapsed = self._time_sim.get_elapsed()

            timestamp = self._time_sim.get_timestamp(
                nsrdb_start_point, elapsed)

            self.nsrdb_data_row = find_nearest_timestamp_row(
                nsrdb_data, timestamp)

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

            if settings.CSV_LOGGING:
                with open(settings.CSV_SSS_LOG_PATH, mode="a", encoding="utf-8") as f:
                    f.write((
                        f"{timestamp},"
                        f"{self.nsrdb_data_row['Time of Day']},"
                        f"{self.power:.2f}\n"
                    ))
                    f.close()

            time.sleep(dt/1000)

    def summery(self) -> str:
        """Generate a summery string for the current status of the simulation.

        Returns:
            str: Simulation summery string.
        """
        return str((
            f"{self.pv_loc}\n"
            f"{self.pv_conf}\n"
            f"{self.battery.conf}\n"
            f"{self.battery}\n"
            f"Total Power: {self.power/1000:.3f} KW\n"
        ))

    def get_nsrdb_start_point(self) -> datetime:
        return nsrdb_start_point

    def is_running(self) -> bool:
        return self._running
