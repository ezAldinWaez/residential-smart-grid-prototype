"""Houses simulator."""

# TODO: Document this module.

from threading import Thread
import time

from rsgp.utils.helpers import log_record_into_csv

from .house import House
from ..config.settings import settings
from ..utils.decorators import log_start_end_error
from ..utils.time_sim import time_sim
from ..remote_object import expose


@expose
class HousesSimulator:
    houses: list[House]  #: list[House]: Houses in the system

    system_load: float  #: float: Total load for the system

    def __init__(self):
        self.houses = [House(idx) for idx in range(settings.HOUSES_NUM)]
        self.system_load = 0.0

        self._running = False

    def get_num_houses(self) -> int:
        return len(self.houses)

    def get_system_load(self) -> float:
        return float(self.system_load)

    def is_running(self) -> bool:
        return self._running

    def get_houses(self) -> list[House]:
        return self.houses

    def get_house(self, idx: int) -> House:
        return self.houses[idx]

    def get_time_sim_elapsed(self) -> float:
        return time_sim.get_elapsed()

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

    @log_start_end_error("Starting houses simulation.", "Stoping houses simulation.")
    def _update_loop(self) -> None:
        while self._running:
            self._update_step()
            time.sleep(self._dt/1000)

    def _update_step(self) -> None:
        elapsed = time_sim.get_elapsed()
        timestamp = time_sim.get_timestamp(elapsed)

        sl = 0.0
        for house in self.houses:
            hl = 0.0
            if house.load_line:
                for device in house.devices.values():
                    hl += device.calc_load(elapsed)
            else:
                house.load_power = 0.0
                for device in house.devices.values():
                    device.load = 0.0
                    device.set_envelopes([
                        (elapsed, 0.0, False)
                        for _ in range(device.conf.max_count)
                    ])
            house.load_power = hl
            sl += hl
        self.system_load = sl

        if settings.CSV_LOGGING:
            log_record_into_csv(
                settings.CSV_HS_LOG_PATH,
                timestamp=f"{timestamp}",
                system_load=f"{self.system_load:.3f}",
                **{
                    ** {f"house_{h.idx+1}_load_line": f"{h.load_line:d}" for h in self.houses},
                    ** {f"house_{h.idx+1}_load_power": f"{h.load_power}" for h in self.houses},
                    ** {f"house_{h.idx+1}_utility_line": f"{h.utility_line:d}" for h in self.houses},
                    ** {f"house_{h.idx+1}_utility_power": f"{h.utility_exchange_power}" for h in self.houses},
                }
            )

    def summary(self) -> str:
        return str((
            f"Houses Loads Status: ..."
        ))

    def __str__(self):
        return f"HousesSimulator(houses={len(self.houses)}, system_load={self.system_load:.3f})"
