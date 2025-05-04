"""Power management solutions interface."""

from ...houses_loads_sim.house import House

from abc import ABC, abstractmethod


class PowerManagementSolution(ABC):
    """Abstract interface for power management solutions."""

    @abstractmethod
    def implement(self, update_delta_time: float, houses: list[House], houses_loads: float, solar_power: float) -> tuple[float, float, float]:
        """Manage the power flow, and adjust the states, and calculate the init houses loads, solar power, and grid power.

        It could turn off some load lines, and could get power from gird on disconnect it.

        Args:
            ...

        Returns:
            ...
        """

    @abstractmethod
    def tuning(self, update_delta_time: float, houses: list[House], houses_loads: float, solar_power: float, init_houses_loads: float, init_solar_power: float, init_grid_power: float, diff_batt_exchange_power: float) -> tuple[float, float, float]:
        """Tune the init houses loads, solar power, and grid power to the actual values.

        Args:
            ...

        Returns:
            ...
        """
