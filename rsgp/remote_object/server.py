"""RSGP remote interface."""

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
    """Remote interface server using Pyro5."""

    daemon: Daemon  #: Daemon: ...
    thread: Thread  #: Thread: ...

    def __init__(self, houses_sim: HousesSimulator, solar_system_sim: SolarSystemSimulator,
                 power_manager: PowerManager):
        """Initialize the remote interface with simulation objects.

        Args:
            time_sim (TimeSimulator): Time simulator.
            houses_sim (HousesSimulator): Houses simulator.
            solar_system_sim (SolarSystemSimulator): Solar system simulator.
            power_manager (PowerManager): Power manager.
        """
        self._houses_sim = houses_sim
        self._solar_system_sim = solar_system_sim
        self._power_manager = power_manager

    def start(self) -> None:
        """Start the remote object server."""
        logger.info("Starting remote object server.")

        # Create and configure daemon
        self.daemon = Daemon(
            host=settings.REMOTE_OBJECT_HOST,
            port=settings.REMOTE_OBJECT_PORT,
        )

        # Register time simulator
        self.daemon.register(time_sim, "time_sim")

        # Register houses simulator and its components
        self.daemon.register(self._houses_sim, "houses_sim")
        for house in self._houses_sim.houses:
            self.daemon.register(house, f"houses_sim.house_{house.idx}")
            for device in house.devices.values():
                self.daemon.register(device, f"houses_sim.house_{house.idx}.device_{device.name}")

        # Register solar system simulator and its components
        self.daemon.register(self._solar_system_sim, "solar_system_sim")
        self.daemon.register(self._solar_system_sim.inverter, "solar_system_sim.inverter")
        self.daemon.register(self._solar_system_sim.inverter._battery, "solar_system_sim.inverter.battery")
        self.daemon.register(self._solar_system_sim.inverter._panels, "solar_system_sim.inverter.panels")

        # Register power manager
        self.daemon.register(self._power_manager, "power_manager")
        for vb in self._power_manager.virtual_batteries:
            self.daemon.register(vb, f"power_manager.virtual_battery_{vb.idx}")

        # Start daemon in a separate thread
        self.thread = Thread(
            target=self.daemon.requestLoop,
            daemon=True
        )

        self.thread.start()

    def stop(self) -> None:
        logger.info("Stoping remote interface server.")

        """Stop the remote interface server."""
        if self.daemon:
            self.daemon.shutdown()

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

    def is_running(self) -> bool:
        """Check if the remote interface is running.

        Returns:
            bool: True if the remote interface is running, False otherwise.
        """
        return self.thread is not None and self.thread.is_alive()
