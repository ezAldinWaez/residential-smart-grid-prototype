"""Power management."""

from datetime import datetime
import os
import random
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

        if self._log:
            with open(self._log_fp, mode="w", encoding="utf-8") as f:
                f.write("elapsed,total_power,battery_charge,load_power\n")
                f.close()

        threading.Thread(
            target=self._update,
            kwargs={'dt': 1000},
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
        """Update the power management every ``dt`` milliseconds.

        Args:
            dt (int): The number of milliseconds to update.

        """
        while self.running:
            elapsed = self._sss._tls.get_elapsed()

            total_load = self._hls.system_load
            solar_power = self._sss.total_power

            if solar_power > total_load:
                # Excess power, charge the battery
                excess_power = solar_power - total_load
                self._sss.battery.charge(excess_power, dt / 1000)
                battery_provided_power = 0
            else:
                # Insufficient power, discharge the battery
                deficit_power = total_load - solar_power
                battery_provided_power = self._sss.battery.discharge(
                    deficit_power, dt / 1000)

            self.total_provided_power = solar_power + battery_provided_power

            while self._hls.system_load > self.total_provided_power:
                random.choice(self._hls.houses).load_line = False

            if self._log:
                with open(self._log_fp, mode="a", encoding="utf-8") as f:
                    f.write(f"{elapsed:.2f}," +
                            "{solar_power:.2f}," +
                            "{self._sss.battery.charge_level:.2f}," +
                            "{total_load:.2f}\n")
                    f.close()

            time.sleep(dt/1000)
