"""Remote object interface for RSGP via Pyro5."""

from __future__ import annotations
from threading import Thread
from typing import TYPE_CHECKING

from ..config.settings import settings
from .logger import logger
from .time_sim import time_sim
if TYPE_CHECKING:
    from ..houses_sim.simulator import HousesSimulator
    from ..solar_system_sim.simulator import SolarSystemSimulator
    from ..power_mng.manager import PowerManager

from Pyro5.api import Daemon


class RemoteObjectServer:
    """Remote object server for RSGP via Pyro5.

    Args:
        houses_sim (HousesSimulator): `HousesSimulator` instance.
        solar_system_sim (SolarSystemSimulator): `SolarSystemSimulator` instance.
        power_manager (PowerManager): `PowerManager` instance.

    """

    daemon: Daemon  #: Daemon: The Pyro5 daemon.
    thread: Thread  #: Thread: The thread for the daemon.

    def __init__(self, houses_sim: HousesSimulator, solar_system_sim: SolarSystemSimulator,
                 power_manager: PowerManager) -> None:
        self._houses_sim = houses_sim
        self._solar_system_sim = solar_system_sim
        self._power_manager = power_manager

    def start(self) -> None:
        """Start the remote object server."""
        logger.info("Starting remote object server.")

        self.daemon = Daemon(
            host=settings.RSGP_REMOTE_OBJECT_HOST,
            port=settings.RSGP_REMOTE_OBJECT_PORT,
        )

        self.daemon.register(settings, "settings")
        self.daemon.register(time_sim, "time_sim")

        self.daemon.register(self._houses_sim, "houses_sim")
        for house in self._houses_sim.houses:
            self.daemon.register(house, f"houses_sim.house_{house.idx+1}")
            for device in house.devices.values():
                self.daemon.register(device, f"houses_sim.house_{house.idx+1}.device_{device.name}")

        self.daemon.register(self._solar_system_sim, "solar_system_sim")
        self.daemon.register(self._solar_system_sim.battery, "solar_system_sim.battery")
        self.daemon.register(self._solar_system_sim.panels, "solar_system_sim.panels")
        self.daemon.register(self._solar_system_sim.inverter, "solar_system_sim.inverter")

        self.daemon.register(self._power_manager, "power_manager")
        for vb in self._power_manager.virtual_batteries:
            self.daemon.register(vb, f"power_manager.virtual_battery_{vb.idx+1}")

        self.thread = Thread(
            target=self.daemon.requestLoop,
            daemon=True
        )

        self.thread.start()

    def stop(self) -> None:
        """Stop the remote object server."""
        logger.info("Stoping remote interface server.")

        if self.daemon:
            self.daemon.shutdown()

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

    def is_running(self) -> bool:
        """Check if the remote object server is running.

        Returns:
            bool: True if the server is running, False otherwise.

        """

        return self.thread is not None and self.thread.is_alive()
