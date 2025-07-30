"""RSGP main."""

from .houses_loads_sim.simulator import HousesLoadsSimulator
from .solar_system_sim.simulator import SolarSystemSimulator
from .power_mng.manager import PowerManager
from .remote_object.server import RemoteObjectServer

houses_loads_sim = HousesLoadsSimulator()
houses_loads_sim.start(dt=100)

solar_system_sim = SolarSystemSimulator()
solar_system_sim.start(dt=100)

power_manager = PowerManager(houses_loads_sim, solar_system_sim)
power_manager.start(dt=100)

remote_object_server = RemoteObjectServer(houses_loads_sim, solar_system_sim, power_manager)
remote_object_server.start()

try:
    remote_object_server.thread.join()
except KeyboardInterrupt:
    remote_object_server.stop()
