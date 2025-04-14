"""Houses loads simulator."""

from datetime import datetime
import threading
import time
import os

from ..config import settings
from ..time_sim import TimeSimulator

from .house import House


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
        self.num_houses = settings.NUM_HOUSES
        self.houses = [House(idx) for idx in range(self.num_houses)]

        if settings.CSV_LOGGING:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self._log_fp = f"data/logs/{timestamp}/log_houses_loads_sim_{timestamp}.csv"
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

        self._dt = dt

        if settings.CSV_LOGGING:
            with open(self._log_fp, mode="w", encoding="utf-8") as f:
                f.write("elapsed,system_load\n")
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

    def get_time_sim_elapsed(self):
        """Get current elapsed time from time simulator."""
        return self._time_sim.get_elapsed()

    def update(self, dt: int):
        """Update the simulation every ``dt`` milliseconds.

        Args:
            dt (int): The number of milliseconds to update.

        """
        while self.running:
            elapsed = self._time_sim.get_elapsed()

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
                with open(self._log_fp, mode="a", encoding="utf-8") as f:
                    f.write(f"{elapsed:.2f},{self.system_load:.2f}\n")
                    f.close()

            time.sleep(dt/1000)
