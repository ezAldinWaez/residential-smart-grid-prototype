"""Solar system simulator."""

# TODO: Document this module.

from __future__ import annotations
from typing import TYPE_CHECKING
import threading
import time



from .panels import Panels
from .battery import Battery
from .utility import Utility
from .load import Load
from .inverter import Inverter
from ..config.settings import settings
from ..utils.decorators import log_start_end_error
from ..utils.helpers import log_record_into_csv
from ..utils.remote_interface import remote_interface_expose
if TYPE_CHECKING:
    from ..time_sim.simulator import TimeSimulator


@remote_interface_expose
class SolarSystemSimulator:
    panels: Panels
    battery: Battery
    inverter: Inverter

    def __init__(self, time_sim: TimeSimulator):
        self._time_sim = time_sim

        self.inverter = Inverter(
            battery=Battery(init_charge_level=.5),
            panels=Panels(),
            utility=Utility(init_connection_status=True),
            load=Load(init_connection_status=True)
        )

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

        dt_seconds = (self._dt / 1000.0) * settings.TIME_FACTOR
        self.inverter.work(timestamp, dt_seconds)
        
        # TODO: re-connect the load line after a set interval

        if settings.CSV_LOGGING:
            log_record_into_csv(
                settings.CSV_SSS_LOG_PATH,
                timestamp=f"{timestamp}",
                batt_charge_level=f"{self.inverter.battery.charge_level:.2f}",
            )

    def summary(self) -> str:
        return str((
            f"{self.inverter}\n"
            f"{self.inverter.conf}\n"
            f"{self.inverter.panels.conf}\n"
            f"{self.inverter.panels}\n"
            f"{self.inverter.battery.conf}\n"
            f"{self.inverter.battery}\n"
            f"{self.inverter.utility}\n"
            f"{self.inverter.load}\n"
        ))
