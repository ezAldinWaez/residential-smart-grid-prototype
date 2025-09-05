"""Solar system simulator."""
from threading import Thread
import time

from .panels import Panels
from .battery import Battery
from .inverter import Inverter
from ..config.settings import settings
from ..utils.decorators import log_start_end_error
from ..utils.helpers import log_record_into_csv
from ..utils.time_sim import time_sim

from Pyro5.api import expose


@expose
class SolarSystemSimulator:
    """Solar system simulator."""

    panels: Panels  #: Panels: The solar panels.
    battery: Battery  #: Battery: The battery.
    inverter: Inverter  #: Inverter: The inverter.

    def __init__(self) -> None:

        self.panels = Panels()
        self.battery = Battery()

        self.inverter = Inverter(
            battery=self.battery,
            panels=self.panels,
        )

        self._running = False

    def is_running(self) -> bool:
        """Check if the solar system simulation is running.

        Returns:
            bool: True if the solar system simulation is running, False otherwise.

        """
        return self._running

    def start(self, dt: int) -> None:
        """Start the solar system simulation.

        Args:
            dt (int): Simulation time step in milliseconds.

        """
        self._running = True
        self._dt = dt

        Thread(
            target=self._update_loop,
            daemon=True
        ).start()

    def pause(self) -> None:
        """Pause the solar system simulation."""
        if self._running:
            self._running = False

    def resume(self) -> None:
        """Resume the solar system simulation."""
        if not self._running:
            self.start(self._dt)

    @log_start_end_error("Starting solar system simulation.", "Stoping solar system simulation.")
    def _update_loop(self) -> None:
        while self._running:
            self._update_step()
            time.sleep(self._dt / 1000.0)

    def _update_step(self, elapsed: float = None) -> None:
        if not elapsed:
            elapsed = time_sim.get_elapsed()
        timestamp = time_sim.get_timestamp(elapsed)

        dt_seconds = (self._dt / 1000.0) * settings.TIME_FACTOR

        self.inverter.operate(timestamp, dt_seconds)

        if settings.CSV_LOGGING:
            log_record_into_csv(
                settings.CSV_SSS_LOG_PATH,
                timestamp=f"{timestamp}",
                panels_total_power=f"{self.panels.total_power:.3f}",
                battery_residual_capacity=f"{self.battery.residual_capacity:.3f}",
                inverter_panels_power=f"{self.inverter.panels_power:.3f}",
                inverter_battery_exchange_power=f"{self.inverter.battery_exchange_power:.3f}",
                inverter_load_line=f"{self.inverter.load_line:d}",
                inverter_load_power=f"{self.inverter.load_power:.3f}",
                inverter_utility_line=f"{self.inverter.utility_line:d}",
                inverter_utility_exchange_power=f"{self.inverter.utility_exchange_power:.3f}",
            )

    def summary(self) -> str:
        """Get a summary of the solar system simulation.

        Returns:
            str: Summary of the solar system simulation.

        """
        return str((
            f"{self.inverter.conf}\n\n"
            f"{self.inverter}\n\n"
            f"{self.panels.conf}\n\n"
            f"{self.panels}\n\n"
            f"{self.battery.conf}\n\n"
            f"{self.battery}\n\n"
        ))
