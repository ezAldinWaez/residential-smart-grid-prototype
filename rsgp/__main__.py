"""RSGP main with Strategy Selector."""

from .time_sim.simulator import TimeSimulator
from .houses_loads_sim.simulator import HousesLoadsSimulator
from .solar_system_sim.simulator import SolarSystemSimulator
from .power_mng.manager import PowerManager
from .power_mng.strategy_selector import PowerManagementStrategy, get_solution
from .utils.remote_interface import start_remote_interface

time_sim = TimeSimulator()
time_sim.start()

houses_loads_sim = HousesLoadsSimulator(time_sim)
houses_loads_sim.start(dt=100)

solar_system_sim = SolarSystemSimulator(time_sim)
solar_system_sim.start(dt=100)

selected_strategy = PowerManagementStrategy.DO_NOTHING
solution = get_solution(selected_strategy)

power_manager = PowerManager(time_sim, houses_loads_sim, solar_system_sim, solution)
power_manager.start(dt=100)

start_remote_interface(
    time_sim,
    houses_loads_sim,
    solar_system_sim,
    power_manager,
)
