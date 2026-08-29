"""Houses simulator."""

from threading import Thread
import time

from .house import House
from ..config.settings import settings
from ..utils.decorators import log_start_end_error
from ..utils.helpers import log_record_into_csv
from ..utils.time_sim import time_sim

from Pyro5.api import expose

@expose
class HousesSimulator:
    """Houses simulator."""

    houses: list[House]  #: list[House]: Houses in the system.
    system_load: float  #: float: Total load for the system.

    def __init__(self) -> None:
        self.houses = [House(idx) for idx in range(settings.HOUSES_NUM)]
        self.system_load = 0.0

        self._running = False

    def get_num_houses(self) -> int:
        """Get number of houses in the system.

        Returns:
            int: Number of houses in the system.

        """
        return len(self.houses)

    def get_system_load(self) -> float:
        """Get total load for the system.

        Returns:
            float: Total load for the system.

        """
        return float(self.system_load)

    def is_running(self) -> bool:
        """Check if the houses simulation is running.

        Returns:
            bool: True if the houses simulation is running, False otherwise.

        """
        return self._running

    def get_houses(self) -> list[House]:
        """Get houses in the system.

        Returns:
            list[House]: Houses in the system.

        """
        return self.houses

    def get_house(self, idx: int) -> House:
        """Get a specific house in the system.

        Args:
            idx (int): House index.

        Returns:
            House: House object.

        """
        return self.houses[idx]

    def get_time_sim_elapsed(self) -> float:
        """Get elapsed time in the simulation.

        Returns:
            float: Elapsed time in the simulation.

        """
        return time_sim.get_elapsed()

    def get_dashboard_metrics(self) -> dict:
        """Return one serializable snapshot for dashboard refreshes."""
        return {
            "system_load": float(self.system_load),
            "running": self._running,
            "houses": [
                {
                    "idx": house.idx,
                    "load": float(house.load_power),
                    "utility_line": bool(house.utility_line),
                    "load_line": bool(house.load_line),
                }
                for house in self.houses
            ],
        }

    def set_all_utility_lines(self, state: bool) -> None:
        """Set every house utility line with one remote call."""
        for house in self.houses:
            house.set_utility_line(state)

    def set_all_load_lines(self, state: bool) -> None:
        """Set every house load line with one remote call."""
        for house in self.houses:
            house.set_load_line(state)

    def toggle_house_utility_line(self, idx: int) -> bool:
        """Toggle one house utility line and return its new state."""
        house = self.houses[idx]
        house.toggle_utility_line()
        return bool(house.utility_line)

    def toggle_house_load_line(self, idx: int) -> bool:
        """Toggle one house load line and return its new state."""
        house = self.houses[idx]
        house.toggle_load_line()
        return bool(house.load_line)

    def get_house_devices_metrics(self, idx: int) -> dict:
        """Return a serializable device-control snapshot for one house."""
        house = self.houses[idx]
        return {
            "house_idx": house.idx,
            "load": float(house.load_power),
            "utility_line": bool(house.utility_line),
            "load_line": bool(house.load_line),
            "running": self._running,
            "devices": [
                {
                    "name": name,
                    "load": float(device.get_load()),
                    "summary": device.get_conf_summary(),
                    "envelopes": [
                        {"idx": envelope_idx, "active": bool(envelope[2])}
                        for envelope_idx, envelope in enumerate(device.get_envelopes())
                    ],
                }
                for name, device in house.devices.items()
            ],
        }

    def toggle_house_device(self, house_idx: int, device_name: str, envelope_idx: int) -> bool:
        """Toggle one appliance envelope and return its new state."""
        device = self.houses[house_idx].devices[device_name]
        if envelope_idx < 0 or envelope_idx >= len(device.get_envelopes()):
            raise IndexError(envelope_idx)
        device.toggle_envelope_state(envelope_idx, time_sim.get_elapsed())
        return bool(device.get_envelopes()[envelope_idx][2])

    def start(self, dt: int) -> None:
        """Start the houses simulation.

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
        """Pause the houses simulation."""
        if self._running:
            self._running = False

    def resume(self) -> None:
        """Resume the houses simulation."""
        if not self._running:
            self.start(self._dt)

    @log_start_end_error("Starting houses simulation.", "Stoping houses simulation.")
    def _update_loop(self) -> None:
        while self._running:
            self._update_step()
            time.sleep(self._dt/1000)

    def _update_step(self, elapsed: float = None) -> None:
        if not elapsed:
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
        """Get a summary of the houses simulation.

        Returns:
            str: Summary of the houses simulation.

        """
        return str('\n\n'.join(f"{house}" for house in self.houses))
