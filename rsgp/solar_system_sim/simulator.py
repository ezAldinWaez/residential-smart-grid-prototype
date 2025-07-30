"""Solar system simulator."""

# TODO: Document this module.

from threading import Thread
import time

from .panels import Panels
from .battery import Battery
from .inverter import Inverter
from ..config.settings import settings
from ..utils.decorators import log_start_end_error
from ..utils.helpers import log_record_into_csv
from ..utils.time_sim import time_sim
from ..remote_object import expose


@expose
class SolarSystemSimulator:
    panels: Panels  #: Panels: ...
    battery: Battery  #: Battery: ...
    inverter: Inverter  #: Inverter: ...

    def __init__(self):

        self.panels = Panels()
        self.battery = Battery()

        self.inverter = Inverter(
            battery=self.battery,
            panels=self.panels,
        )

        self._running = False

    def is_running(self) -> bool:
        return self._running

    def start(self, dt: int) -> None:
        self._running = True
        self._dt = dt

        Thread(
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
        timestamp = time_sim.get_timestamp()

        dt_seconds = (self._dt / 1000.0) * settings.TIME_FACTOR

        self.inverter.operate(timestamp, dt_seconds)

        # TODO: re-connect the load line after a set interval

        if settings.CSV_LOGGING:
            log_record_into_csv(
                settings.CSV_SSS_LOG_PATH,
                timestamp=f"{timestamp}",
                panels_total_power=f"{self.panels.total_power:.3f}",
                battery_charge_level=f"{self.battery.charge_level:.3f}",
                inverter_panels_power=f"{self.inverter.panels_power:.3f}",
                inverter_battery_exchange_power=f"{self.inverter.battery_exchange_power:.3f}",
                inverter_load_line=f"{self.inverter.load_line:d}",
                inverter_load_power=f"{self.inverter.load_power:.3f}",
                inverter_utility_line=f"{self.inverter.utility_line:d}",
                inverter_utility_exchange_power=f"{self.inverter.utility_exchange_power:.3f}",
            )

    def summary(self) -> str:
        return str((
            f"{self.inverter}\n"
            f"{self.panels}\n"
            f"{self.battery}\n"
        ))
