from __future__ import annotations
from threading import Thread
from typing import TYPE_CHECKING

from Pyro5.api import Daemon

from ..config.settings import settings
from ..utils.logger import logger
from ..utils.time_sim import time_sim
if TYPE_CHECKING:
    from ..houses_sim.simulator import HousesSimulator
    from ..solar_system_sim.simulator import SolarSystemSimulator
    from ..power_mng.manager import PowerManager


class RemoteObjectServer:

    daemon: Daemon  #: Daemon: ...
    thread: Thread  #: Thread: ...

    def __init__(self, houses_sim: HousesSimulator, solar_system_sim: SolarSystemSimulator,
                 power_manager: PowerManager):
        self._houses_sim = houses_sim
        self._solar_system_sim = solar_system_sim
        self._power_manager = power_manager

    def start(self) -> None:
        logger.info("Starting remote object server.")

        self.daemon = Daemon(
            host=settings.REMOTE_OBJECT_HOST,
            port=settings.REMOTE_OBJECT_PORT,
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
        logger.info("Stoping remote interface server.")

        if self.daemon:
            self.daemon.shutdown()

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

    def is_running(self) -> bool:
        return self.thread is not None and self.thread.is_alive()
