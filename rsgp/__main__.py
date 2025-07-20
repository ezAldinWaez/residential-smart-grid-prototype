"""RSGP main."""

from .time_sim.simulator import TimeSimulator
from .houses_loads_sim.simulator import HousesLoadsSimulator
from .solar_system_sim.simulator import SolarSystemSimulator
from .power_mng.manager import PowerManager
from .remote_object.server import RemoteObjectServer

time_sim = TimeSimulator()
time_sim.start()

houses_loads_sim = HousesLoadsSimulator(time_sim)
houses_loads_sim.start(dt=100)

solar_system_sim = SolarSystemSimulator(time_sim)
solar_system_sim.start(dt=100)

power_manager = PowerManager(time_sim, houses_loads_sim, solar_system_sim)
power_manager.start(dt=100)

remote_object_server = RemoteObjectServer(time_sim, houses_loads_sim, solar_system_sim, power_manager)
remote_object_server.start()

try:
    remote_object_server.thread.join()
except KeyboardInterrupt:
    time_sim.pause()
    solar_system_sim.pause()
    houses_loads_sim.pause()
    power_manager.pause()
    remote_object_server.stop()
