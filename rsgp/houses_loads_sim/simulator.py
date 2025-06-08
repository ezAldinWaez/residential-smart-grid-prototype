"""Houses loads simulator."""

from __future__ import annotations
from typing import TYPE_CHECKING
import threading
import time

from .house import House
from ..config.settings import settings
from ..utils.logger import logger
from ..utils.remote_interface import remote_interface_expose
from ..solar_system_sim.nsrdb_data import nsrdb_start_point
if TYPE_CHECKING:
    from ..time_sim.simulator import TimeSimulator


@remote_interface_expose
class HousesLoadsSimulator:
    """Houses loads simulator.

    Args:
        time_sim (TimeSimulator): Time simulator instance.
    """
    num_houses: int   #: int: Number of houses in the system.
    system_load: float = .0  #: float: The current system total load.
    #: list[HouseState]: House state for each house in the system.
    houses: list[House]

    def __init__(self, time_sim: TimeSimulator):
        self._time_sim = time_sim
        self.num_houses = settings.HOUSES_NUM
        self.houses = [House(idx) for idx in range(self.num_houses)]

        self._running = False
        if settings.CSV_LOGGING:
            with open(settings.CSV_HLS_LOG_PATH, mode="w", encoding="utf-8") as f:
                f.write((
                    "Timestamp,"
                    "Time of Day,"
                    "System Load\n"
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

        logger.info("Houses loads simulation started.")

    def pause(self):
        """Pause the simulation."""
        if self._running:
            self._running = False

        logger.info("Houses loads simulation paused.")

    def resume(self):
        """Resume the simulation."""
        if not self._running:
            self.start()

    def update(self, dt: int):
        """Update the simulation every `dt` milliseconds.

        Args:
            dt (int): The number of milliseconds to update.

        """
        while self._running:
            elapsed = self._time_sim.get_elapsed()
            timestamp = self._time_sim.get_timestamp(
                nsrdb_start_point, elapsed)

            sl = .0
            for house in self.houses:
                hl = .0
                if house.load_line:
                    for device in house.devices.values():
                        hl += device.calc_load(elapsed)
                else:
                    house.load = .0
                    for device in house.devices.values():
                        device.load = .0
                        device.envelopes = [
                            (elapsed, .0, False)
                            for _ in range(device.conf.max_count)
                        ]
                house.load = hl
                sl += hl
            self.system_load = sl

            if settings.CSV_LOGGING:
                with open(settings.CSV_HLS_LOG_PATH, mode="a", encoding="utf-8") as f:
                    f.write((
                        f"{timestamp},"
                        f"Unknown,"
                        f"{self.system_load:.2f}\n"
                    ))
                    f.close()

            time.sleep(dt/1000)

    def get_num_houses(self) -> int:
        return self.num_houses

    def get_system_load(self) -> float:
        return float(self.system_load)

    def is_running(self) -> bool:
        return self._running

    def get_houses(self) -> list[House]:
        return self.houses

    def get_house(self, idx: int) -> House:
        return self.houses[idx]

    def get_time_sim_elapsed(self) -> float:
        return self._time_sim.get_elapsed()
