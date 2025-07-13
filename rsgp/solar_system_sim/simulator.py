"""Solar system simulator."""

# TODO: Document this module.

from __future__ import annotations
from typing import TYPE_CHECKING
import threading
import time

import pandas as pd


from .panels import Panels
from .battery import Battery
from .inverter import Inverter
from ..config.settings import settings
from ..utils.decorators import log_start_end_error
from ..utils.helpers import log_record_into_csv
from ..utils.logger import logger
from ..utils.remote_interface import remote_interface_expose
if TYPE_CHECKING:
    from ..time_sim.simulator import TimeSimulator
    from ..houses_loads_sim.simulator import HousesLoadsSimulator


@remote_interface_expose
class SolarSystemSimulator:
    panels: Panels
    battery: Battery
    inverter: Inverter

    def __init__(self, time_sim: TimeSimulator, houses_loads_sim: HousesLoadsSimulator):
        self._time_sim = time_sim
        self._houses_loads_sim = houses_loads_sim

        self.panels = Panels()
        self.battery = Battery(init_charge_level=.5)
        self.inverter = Inverter(self.battery, self.panels, initial_grid_status=True)

        self._running = False

    def is_running(self) -> bool:
        return self._running

    def start(self, dt: int) -> None:
        self._running = True
        self._dt = dt

        threading.Thread(
            target=self._update_loop,
            daemon=True
        ).start()

    def pause(self) -> None:
        if self._running:
            self._running = False

    def resume(self) -> None:
        if not self._running:
            self.start(self._dt)

    @log_start_end_error("Starting solar system simulation.", "Stoping solar system simulation.")
    def _update_loop(self) -> None:
        while self._running:
            self._update_step()
            time.sleep(self._dt / 1000.0)

    def _update_step(self) -> None:
        timestamp = self._time_sim.get_timestamp()

        system_load = self._houses_loads_sim.get_system_load()
        dt_seconds = (self._dt / 1000.0) * settings.TIME_FACTOR
        self.inverter.work(timestamp, dt_seconds, system_load)

        if settings.CSV_LOGGING:
            log_record_into_csv(
                settings.CSV_SSS_LOG_PATH,
                timestamp=f"{timestamp}",
                batt_charge_level=f"{self.battery.charge_level:.2f}",
            )

    def summary(self) -> str:
        return str((
            f"{self.panels.conf}\n"
            f"{self.panels}\n"
            f"{self.battery.conf}\n"
            f"{self.battery}\n"
            f"{self.inverter.conf}\n"
            f"{self.inverter}\n"
        ))
