"""Power manager."""

from __future__ import annotations
from typing import TYPE_CHECKING
import threading
import time

from ..config.settings import settings
from ..utils.decorators import log_start_end_error
from ..utils.helpers import log_record_into_csv
from ..utils.remote_interface import remote_interface_expose
if TYPE_CHECKING:
    from ..time_sim.simulator import TimeSimulator
    from ..houses_loads_sim.simulator import HousesLoadsSimulator
    from ..solar_system_sim.simulator import SolarSystemSimulator


@remote_interface_expose
class PowerManager:
    def __init__(self, time_sim: TimeSimulator, houses_loads_sim: HousesLoadsSimulator, solar_system_sim: SolarSystemSimulator):
        self._time_sim = time_sim
        self._houses_loads_sim = houses_loads_sim
        self._solar_system_sim = solar_system_sim
        self._running = False

    def is_running(self) -> bool:
        return self._running

    def start(self, dt: int = None) -> None:
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

    @log_start_end_error("Starting power manager.", "Stoping power manager.")
    def _update_loop(self) -> None:
        while self._running:
            self._update_step()
            time.sleep(self._dt/1000)

    def _update_step(self) -> None:
        elapsed = self._time_sim.get_elapsed()
        timestamp = self._time_sim.get_timestamp(elapsed)

        system_load = self._houses_loads_sim.get_system_load()
        
        # TODO: Integragte solutions with inverter APIs.

        # Set inverter utility line connection status
        are_all_utility_lines_off = True
        list_of_utility_lines_state = [house.utility_line for house in self._houses_loads_sim.houses]
        for utility in list_of_utility_lines_state: 
            if utility:
                are_all_utility_lines_off = False
                break
        self._solar_system_sim.inverter.utility.set_connection_status(not are_all_utility_lines_off)

        self._solar_system_sim.inverter.load.set_system_load(system_load)

        if settings.CSV_LOGGING:
            log_record_into_csv(
                settings.CSV_PM_LOG_PATH,
                timestamp=f"{timestamp}",
            )

    def summary(self) -> str:
        return str((
            f"Power Manager Status: ..."
        ))
