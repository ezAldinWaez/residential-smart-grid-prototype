"""Houses loads simulator."""

# TODO: Document this module.

from __future__ import annotations
from typing import TYPE_CHECKING
import threading
import time

from rsgp.utils.helpers import log_record_into_csv

from .house import House
from ..config.settings import settings
from ..utils.decorators import log_start_end_error
from ..utils.remote_interface import remote_interface_expose

if TYPE_CHECKING:
    from ..time_sim.simulator import TimeSimulator


@remote_interface_expose
class HousesLoadsSimulator:
    num_houses: int  #: int: Number of houses in the system
    load: float  #: float: Total load for the system
    houses: list[House]  #: list[House]: Houses in the system

    def __init__(self, time_sim: TimeSimulator):
        self._time_sim = time_sim
        self.num_houses = settings.HOUSES_NUM
        self.load = 0.0
        self.houses = [House(idx) for idx in range(self.num_houses)]

        self._running = False

    def get_num_houses(self) -> int:
        return self.num_houses

    def get_system_load(self) -> float:
        return float(self.load)

    def is_running(self) -> bool:
        return self._running

    def get_houses(self) -> list[House]:
        return self.houses

    def get_house(self, idx: int) -> House:
        return self.houses[idx]

    def get_time_sim_elapsed(self) -> float:
        return self._time_sim.get_elapsed()

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

    @log_start_end_error("Starting houses loads simulation.", "Stoping houses loads simulation.")
    def _update_loop(self) -> None:
        while self._running:
            self._update_step()
            time.sleep(self._dt/1000)

    def _update_step(self) -> None:
        elapsed = self._time_sim.get_elapsed()
        timestamp = self._time_sim.get_timestamp(elapsed)

        sl = 0.0
        for house in self.houses:
            hl = 0.0
            if house.load_line:
                for device in house.devices.values():
                    hl += device.calc_load(elapsed)
            else:
                house.load = 0.0
                for device in house.devices.values():
                    device.load = 0.0
                    device.envelopes = [
                        (elapsed, 0.0, False)
                        for _ in range(device.conf.max_count)
                    ]
            house.load = hl
            sl += hl
        self.load = sl

        if settings.CSV_LOGGING:
            log_record_into_csv(
                settings.CSV_HLS_LOG_PATH,
                timestamp=f"{timestamp}",
                system_load=f"{self.load:.3f}",
            )

    def summary(self) -> str:
        return str((
            f"Houses Loads Status: ..."
        ))
