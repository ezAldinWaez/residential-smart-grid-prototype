"""Power management."""

from datetime import datetime
import os
import threading
import time

from .houses_loads_sim import HousesLoadsSimulator
from .solar_system_sim import SolarSystemSimulator


class PowerManager:
    """Power manager.

    Args:
        hls (HousesLoadsSimulator): Houses loads simulator instance.
        sss (SolarSystemSimulator): Solar system simulator instance.
        log (bool): If True, an csv file will be created and record the system status.

    """

    #: bool: Whether the simulation is running or paused.
    running: bool = False

    def __init__(self, hls: HousesLoadsSimulator, sss: SolarSystemSimulator, log: bool):
        self._hls = hls
        self._sss = sss

        self._log = log
        if self._log:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self._log_fp = f"logs/{timestamp}/log_power_management_{timestamp}.csv"
            if not os.path.exists("logs"):
                os.mkdir("logs")
            if not os.path.exists(f"logs/{timestamp}"):
                os.mkdir(f"logs/{timestamp}")

    def start(self):
        """Start the power management."""
        self.running = True

        # if self._log:
        #     with open(self._log_fp, mode="w", encoding="utf-8") as f:
        #         f.write("\n")
        #         f.close()

        threading.Thread(
            target=self._update,
            kwargs={'dt': 100},
            daemon=True
        ).start()

    def pause(self):
        """Pause the power management."""
        if self.running:
            self.running = False

    def resume(self):
        """Resume the power management."""
        if not self.running:
            self.start()

    def _update(self, dt: int):
        """Update the power mangement every ``dt`` milliseconds.

        Args:
            dt (int): The number of milliseconds to update.

        """
        while self.running:

            for house in self._hls.houses:
                if house.load > self._sss.total_power / self._hls.num_houses:
                    house.load_line = False

            # if self._log:
            #     with open(self._log_fp, mode="a", encoding="utf-8") as f:
            #         f.write("\n")
            #         f.close()

            time.sleep(dt/1000)
