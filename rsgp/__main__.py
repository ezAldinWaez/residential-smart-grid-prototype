"""RSGP main."""

from .houses_sim.simulator import HousesSimulator
from .solar_system_sim.simulator import SolarSystemSimulator
from .power_mng.manager import PowerManager
from .utils.remote_object import RemoteObjectServer

houses_sim = HousesSimulator()
houses_sim.start(dt=200)

solar_system_sim = SolarSystemSimulator()
solar_system_sim.start(dt=200)

power_manager = PowerManager(houses_sim, solar_system_sim)
power_manager.start(dt=200)

remote_object_server = RemoteObjectServer(houses_sim, solar_system_sim, power_manager)
remote_object_server.start()

try:
    remote_object_server.thread.join()
except KeyboardInterrupt:
    remote_object_server.stop()
