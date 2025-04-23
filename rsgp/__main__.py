"""RSGP main."""

from .time_sim import TimeSimulator
from .houses_loads_sim import HousesLoadsSimulator
from .solar_system_sim import SolarSystemSimulator
from .power_mng import PowerManager
from .utils.remote_interface import start_pyro5_server

time_sim = TimeSimulator()
time_sim.start()

houses_loads_sim = HousesLoadsSimulator(time_sim)
houses_loads_sim.start(dt=100)

solar_system_sim = SolarSystemSimulator(time_sim)
solar_system_sim.start(dt=100)

power_manager = PowerManager(time_sim, houses_loads_sim, solar_system_sim)
power_manager.start(dt=100)

start_pyro5_server(time_sim, houses_loads_sim, solar_system_sim, power_manager)
