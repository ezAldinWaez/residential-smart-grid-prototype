"""Houses loads simulator."""

from .house import House

from ..config import settings
from ..utils import logger
from ..time_sim import TimeSimulator
from ..solar_system_sim import nsrdb_start_point

import threading
import time


class HousesLoadsSimulator:
    """Houses loads simulator.

    Args:
        time_sim (TimeSimulator): Time simulator instance.
    """
    num_houses: int   #: int: Number of houses in the system.
    #: list[HouseState]: House state for each house in the system.
    houses: list[House]
    running: bool = False   #: Whether the simulation is running or paused.
    system_load: float = .0  #: float: The current system total load.

    def __init__(self, time_sim: TimeSimulator):
        self._time_sim = time_sim
        self.num_houses = settings.HOUSES_NUM
        self.houses = [House(idx) for idx in range(self.num_houses)]

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
        self.running = True

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
        if self.running:
            self.running = False

        logger.info("Houses loads simulation paused.")

    def resume(self):
        """Resume the simulation."""
        if not self.running:
            self.start()

    def update(self, dt: int):
        """Update the simulation every `dt` milliseconds.

        Args:
            dt (int): The number of milliseconds to update.

        """
        while self.running:
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
