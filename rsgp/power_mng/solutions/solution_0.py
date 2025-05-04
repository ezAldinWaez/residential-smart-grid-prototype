"""Power management solution 00."""

from .solution_interface import PowerManagementSolution
from ...config.settings import settings


class DoNothingSolution(PowerManagementSolution):
    """
    Power management solution that do nothing.
    """

    def implement(self, update_delta_time, houses, houses_loads, solar_power):
        return houses_loads, solar_power, 0.0

    def tuning(self, update_delta_time, houses, houses_loads, solar_power, init_houses_loads, init_solar_power, init_grid_power, diff_batt_exchange_power):
        return init_houses_loads, init_solar_power - diff_batt_exchange_power, init_grid_power
