from ..config.settings import settings
from ..config.constants import SECONDS_IN_HOUR

from Pyro5.api import expose


@expose
class VirtualBattery:
    """Virtual battery.

    Args:
        idx (int): The index of the virtual battery.
        init_total_capacity (float): The initial total capacity of the virtual battery [Wh].
        init_residual_capacity (float): The initial residual capacity of the virtual battery [Wh].

    """

    total_capacity: float  #: float: ...
    residual_capacity: float  #: float: ...
    charge_efficiency: float  #: float: ...
    weight: float  #: float: ...

    def __init__(self, idx: int, init_total_capacity: float, init_residual_capacity: float, charge_efficiency: float, min_weight: float, max_weight: float) -> None:
        self.idx = idx
        self._init_total_capacity = init_total_capacity
        self.total_capacity = self._init_total_capacity
        self.residual_capacity = init_residual_capacity
        self.charge_efficiency = charge_efficiency
        self._min_weight = min_weight
        self._max_weight = max_weight
        self.weight = 1.0

    def charge(self, power: float, time_interval: float) -> float:
        """Charge the virtual battery with a given power for a given time interval.

        Args:
            power (float): The power to charge with [Watt].
            time_interval (float): The time interval in seconds.

        Returns:
            float: The actual power used for charging [Watt].

        """
        charge_power = power
        charge_power *= self.charge_efficiency
        charge_energy = charge_power * (time_interval / SECONDS_IN_HOUR)

        energy_to_full = self.total_capacity - self.residual_capacity
        actual_charge_energy = min(charge_energy, energy_to_full)
        self.residual_capacity += actual_charge_energy

        actual_charge_power = actual_charge_energy * (SECONDS_IN_HOUR / time_interval)
        actual_charge_power /= self.charge_efficiency
        return actual_charge_power

    def discharge(self, power: float, time_interval: float) -> float:
        """Discharge the virtual battery with a given power for a given time interval.

        Args:
            power (float): The power to discharge with [Watt].
            time_interval (float): The time interval in seconds.

        Returns:
            float: The actual power discharged [Watt].

        """
        discharge_power = power
        discharge_power /= self.charge_efficiency
        discharge_energy = discharge_power * (time_interval / SECONDS_IN_HOUR)

        actual_discharge_energy = min(discharge_energy, self.residual_capacity)
        self.residual_capacity -= actual_discharge_energy

        actual_discharge_power = actual_discharge_energy * (SECONDS_IN_HOUR / time_interval)
        actual_discharge_power *= self.charge_efficiency
        return actual_discharge_power

    def adjust(self, amount: float) -> float:
        """..."""
        self.weight += amount
        self.weight = max(self.weight, self._min_weight)
        self.weight = min(self.weight, self._max_weight)

        self.total_capacity = self._init_total_capacity * self.weight
        new_residual_capacity = min(self.residual_capacity, self.total_capacity)
        excess_capacity = self.residual_capacity - new_residual_capacity
        self.residual_capacity = new_residual_capacity

        return excess_capacity

    def __str__(self) -> str:
        return f"VirtualBattery(idx={self.idx}, weight={self.weight:.3f}, total_capacity={self.total_capacity:.3f}, residual_capacity={self.residual_capacity:.3f})"
