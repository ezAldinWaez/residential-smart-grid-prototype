"""Power manager with abstract solution integration."""

from ..config.settings import settings
from ..utils.logger import logger
from ..time_sim.simulator import TimeSimulator
from ..houses_loads_sim.simulator import HousesLoadsSimulator
from ..solar_system_sim.simulator import SolarSystemSimulator
from ..solar_system_sim.nsrdb_data import nsrdb_start_point

import threading
import time

from Pyro5.api import expose as remote_interface_expose


@remote_interface_expose
class PowerManager:
    """Power manager integrated with abstract power management solutions.

    Args:
        time_sim (TimeSimulator): Time simulator.
        houses_loads_sim (HousesLoadsSimulator): Houses loads simulator.
        solar_system_sim (SolarSystemSimulator): Solar system simulator.
        solution (PowerManagementSolution): Power management solution.

    Todo:
        * Deal with houses grid line.
    """

    #: float: Battery exchange power. [W]
    batt_exchange_power: float = 0

    def __init__(
            self,
            time_sim: TimeSimulator,
            houses_loads_sim: HousesLoadsSimulator,
            solar_system_sim: SolarSystemSimulator):
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
            
            # TODO: integragte solutions with inverter APIs.

            if settings.CSV_LOGGING:
                with open(settings.CSV_PM_LOG_PATH, mode="a", encoding="utf-8") as f:
                    f.write((
                        f"{self._time_sim.get_timestamp(nsrdb_start_point)},"
                        f"{self._solar_system_sim.nsrdb_data_row['Time of Day']},"
                    ))

            time.sleep(dt/1000)

    def summary(self) -> str:
        """Generate a summary string for the current status of the manager.

        Returns:
            str: Power manager summary string.
        """
        return str((
            f"Battery exchange power: {self.batt_exchange_power:.2f} W\n"
        ))

    def is_running(self) -> bool:
        return self._running
