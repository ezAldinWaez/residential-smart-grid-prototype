"""Power management strategy selector."""

from enum import Enum
from .solutions.solution_interface import PowerManagementSolution
from .solutions.solution_0 import DoNothingSolution


class PowerManagementStrategy(Enum):
    DO_NOTHING = 0
    STATIC_EQUAL = 1
    DYNAMIC_EQUAL = 2
    PREDICTIVE_ALLOCATION = 3
    POOL_BASED = 4
    REINFORCEMENT_LEARNING = 5


def get_solution(strategy: PowerManagementStrategy) -> PowerManagementSolution:
    if strategy == PowerManagementStrategy.DO_NOTHING:
        return DoNothingSolution()

    if strategy == PowerManagementStrategy.STATIC_EQUAL:
        raise NotImplementedError("Not implemented yet.")

    if strategy == PowerManagementStrategy.DYNAMIC_EQUAL:
        raise NotImplementedError("Not implemented yet.")

    if strategy == PowerManagementStrategy.PREDICTIVE_ALLOCATION:
        raise NotImplementedError("Not implemented yet.")

    if strategy == PowerManagementStrategy.POOL_BASED:
        raise NotImplementedError("Not implemented yet.")

    if strategy == PowerManagementStrategy.REINFORCEMENT_LEARNING:
        raise NotImplementedError("Not implemented yet.")

    raise ValueError("Unsupported power management strategy")
