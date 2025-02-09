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

    Todo:
        * Deal with houses grid line.

    """

    #: bool: Whether the simulation is running or paused.
    running: bool = False
    #: float: Battery exchange power. [W]
    batt_exchange_power: float = 0

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

    def start(self, dt: int=None):
        """Start the power management.

        Args:
            dt (int): Update time. [millisecond] 

        """
        self.running = True

        if not dt:
            dt = self._dt

        self._dt = dt

        if self._log:
            with open(self._log_fp, mode="w", encoding="utf-8") as f:
                f.write("elapsed,total_power,battery_charge,load_power\n")
                f.close()

        threading.Thread(
            target=self.update,
            kwargs={'dt': dt},
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

    def update(self, dt: int):
        """Update the power management every ``dt`` milliseconds.

        Args:
            dt (int): The number of milliseconds to update.

        """
        while self.running:
            elapsed = self._sss._tls.get_elapsed()

            houses_load = self._hls.system_load
            solar_power = self._sss.total_power

            if solar_power >= houses_load:
                # Excess power, charge the battery
                excess_power = solar_power - houses_load
                batt_consumed_power = self._sss.batt.charge(
                    power=excess_power,
                    time=(dt / 1000) * self._sss._tls.time_factor
                )
                self.batt_exchange_power = - batt_consumed_power
            else:
                # Insufficient power, discharge the battery
                deficit_power = houses_load - solar_power
                batt_provided_power = self._sss.batt.discharge(
                    power=deficit_power,
                    time=(dt / 1000) * self._sss._tls.time_factor,
                )
                self.batt_exchange_power = + batt_provided_power

            # Todo: why it crashs when uncomment that?
            # total_provided_power = solar_power + self.batt_exchange_power
            # while self._hls.system_load > total_provided_power:
            #     random.choice(self._hls.houses).load_line = False

            if self._log:
                with open(self._log_fp, mode="a", encoding="utf-8") as f:
                    f.write(f"{elapsed:.2f}," +
                            f"{self._sss.batt.charge_level:.2f}\n")
                    f.close()

            time.sleep(dt/1000)
