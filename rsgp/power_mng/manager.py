"""Power manager."""

from ..config import settings
from ..utils import logger
from ..time_sim import TimeSimulator
from ..houses_loads_sim import HousesLoadsSimulator
from ..solar_system_sim import SolarSystemSimulator, nsrdb_start_point

import threading
import time

import Pyro5.api


@Pyro5.api.expose
class PowerManager:
    """Power manager.

    Args:
        time_sim (TimeSimulator): Time simulator.
        houses_loads_sim (HousesLoadsSimulator): Houses loads simulator.
        solar_system_sim (SolarSystemSimulator): Solar system simulator.

    Todo:
        * Deal with houses grid line.
    """

    #: float: Battery exchange power. [W]
    batt_exchange_power: float = 0

    def __init__(self, time_sim: TimeSimulator, houses_loads_sim: HousesLoadsSimulator, solar_system_sim: SolarSystemSimulator):
        self._time_sim = time_sim
        self._houses_loads_sim = houses_loads_sim
        self._solar_system_sim = solar_system_sim

        self._running = False
        if settings.CSV_LOGGING:
            with open(settings.CSV_PM_LOG_PATH, mode="w", encoding="utf-8") as f:
                f.write((
                    "Timestamp,"
                    "Time of Day,"
                    "Battery Exchange Power\n"
                ))
                f.close()

    def start(self, dt: int = None):
        """Start the power management.

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

        logger.info("Power management started.")

    def pause(self):
        """Pause the power management."""
        if self._running:
            self._running = False

        logger.info("Power management paused.")

    def resume(self):
        """Resume the power management."""
        if not self._running:
            self.start()

    def update(self, dt: int):
        """Update the power management every `dt` milliseconds.

        Args:
            dt (int): The number of milliseconds to update.
        """
        while self._running:
            houses_load = self._houses_loads_sim.system_load
            solar_power = self._solar_system_sim.power

            if solar_power >= houses_load:
                # Excess power, charge the battery
                excess_power = solar_power - houses_load
                batt_consumed_power = self._solar_system_sim.battery.charge(
                    power=excess_power,
                    time=(dt / 1000) * settings.TIME_FACTOR
                )
                self.batt_exchange_power = - batt_consumed_power
            else:
                # Insufficient power, discharge the battery
                deficit_power = houses_load - solar_power
                batt_provided_power = self._solar_system_sim.battery.discharge(
                    power=deficit_power,
                    time=(dt / 1000) * settings.TIME_FACTOR,
                )
                self.batt_exchange_power = + batt_provided_power

            # ...

            if settings.CSV_LOGGING:
                with open(settings.CSV_PM_LOG_PATH, mode="a", encoding="utf-8") as f:
                    f.write((
                        f"{self._time_sim.get_timestamp(nsrdb_start_point)},"
                        f"{self._solar_system_sim.nsrdb_data_row['Time of Day']},"
                        f"{self.batt_exchange_power:.2f}\n"
                    ))
                    f.close()

            time.sleep(dt/1000)

    def summery(self) -> str:
        """Generate a summery string for the current status of the manager.

        Returns:
            str: Power manager summery string.
        """
        return str((
            f"Battery exchange power: {self.batt_exchange_power:.2f} W\n"
        ))

    def is_running(self) -> bool:
        return self._running
