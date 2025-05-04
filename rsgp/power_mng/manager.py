"""Power manager with abstract solution integration."""

from .solutions.solution_interface import PowerManagementSolution
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
            solar_system_sim: SolarSystemSimulator,
            solution: PowerManagementSolution):
        self._time_sim = time_sim
        self._houses_loads_sim = houses_loads_sim
        self._solar_system_sim = solar_system_sim
        self.solution = solution

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
            update_delta_time = (dt / 1000) * settings.TIME_FACTOR

            houses = self._houses_loads_sim.houses
            system_load = self._houses_loads_sim.system_load
            solar_power = self._solar_system_sim.power

            init_system_load, init_solar_power, init_grid_power = self.solution.implement(
                update_delta_time,
                houses,
                system_load,
                solar_power,
            )

            init_batt_exchange_power = (
                init_system_load - init_solar_power - init_grid_power
            )

            if init_batt_exchange_power < 0:
                batt_consumed_power = self._solar_system_sim.battery.charge(
                    power=abs(init_batt_exchange_power),
                    time=update_delta_time,
                )
                actual_batt_exchange_power = - batt_consumed_power

            elif init_batt_exchange_power > 0:
                batt_provided_power = self._solar_system_sim.battery.discharge(
                    power=abs(init_batt_exchange_power),
                    time=update_delta_time
                )
                actual_batt_exchange_power = + batt_provided_power

            else:
                actual_batt_exchange_power = 0

            actual_system_load, actual_solar_power, actual_grid_power = self.solution.tuning(
                update_delta_time,
                houses,
                system_load,
                solar_power,
                init_system_load,
                init_solar_power,
                init_grid_power,
                (actual_batt_exchange_power - init_batt_exchange_power),
            )

            self.batt_exchange_power = actual_batt_exchange_power
            self.houses_loads = actual_system_load
            self.solar_power = actual_solar_power
            self.grid_power = actual_grid_power

            if settings.CSV_LOGGING:
                with open(settings.CSV_PM_LOG_PATH, mode="a", encoding="utf-8") as f:
                    f.write((
                        f"{self._time_sim.get_timestamp(nsrdb_start_point)},"
                        f"{self._solar_system_sim.nsrdb_data_row['Time of Day']},"
                        f"{self.batt_exchange_power:.2f}\n"
                        f"{self.houses_loads:.2f}\n"
                        f"{self.solar_power:.2f}\n"
                        f"{self.grid_power:.2f}\n"
                    ))

            time.sleep(dt/1000)

    def summery(self) -> str:
        """Generate a summary string for the current status of the manager.

        Returns:
            str: Power manager summary string.
        """
        return str((
            f"Battery exchange power: {self.batt_exchange_power:.2f} W\n"
            f"Houses loads: {self.houses_loads:.2f} W\n"
            f"Solar power: {self.solar_power:.2f} W\n"
            f"Grid power: {self.grid_power:.2f} W\n"
        ))

    def is_running(self) -> bool:
        return self._running
