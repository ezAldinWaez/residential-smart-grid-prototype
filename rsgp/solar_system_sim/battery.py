"""Solar system simulation battery."""

from .data import BatteryConf
from ..config.constants import SECONDS_IN_HOUR
from ..config.settings import settings

from Pyro5.api import expose


@expose
class Battery:
    """Battery."""

    conf: BatteryConf  #: BattConf: The battery configuration.
    residual_capacity: float  #: float: Current charge level of the battery [Wh].

    def __init__(self) -> None:
        self.conf = BatteryConf(
            total_capacity=settings.BATTERY_TOTAL_CAPACITY,
            charge_efficiency=settings.BATTERY_CHARGE_EFFICIENCY,
            max_charge_power=settings.BATTERY_MAX_CHARGE_POWER,
            max_discharge_power=settings.BATTERY_MAX_DISCHARGE_POWER,
        )

        self.residual_capacity = settings.BATTERY_INIT_RESIDUAL_CAPACITY

    def charge(self, power: float, time_interval: float) -> float:
        """Charge the battery with a given power for a given time interval.

        Args:
            power (float): The power to charge with [Watt].
            time_interval (float): The time interval in seconds.

        Returns:
            float: The actual power used for charging [Watt].
        """
        charge_power = min(power, self.conf.max_charge_power)
        charge_power *= self.conf.charge_efficiency
        charge_energy = charge_power * (time_interval / SECONDS_IN_HOUR)

        energy_to_full = self.conf.total_capacity - self.residual_capacity
        actual_charge_energy = min(charge_energy, energy_to_full)
        self.residual_capacity += actual_charge_energy

        actual_charge_power = actual_charge_energy * (SECONDS_IN_HOUR / time_interval)
        actual_charge_power /= self.conf.charge_efficiency
        return actual_charge_power

    def discharge(self, power: float, time_interval: float) -> float:
        """Discharge the battery with a given power for a given time interval.

        Args:
            power (float): The power to discharge with [Watt].
            time_interval (float): The time interval in seconds.

        Returns:
            float: The actual power discharged [Watt].
        """
        discharge_power = min(power, self.conf.max_discharge_power)
        discharge_power /= self.conf.charge_efficiency
        discharge_energy = discharge_power * (time_interval / SECONDS_IN_HOUR)

        actual_discharge_energy = min(discharge_energy, self.residual_capacity)
        self.residual_capacity -= actual_discharge_energy

        actual_discharge_power = actual_discharge_energy * (SECONDS_IN_HOUR / time_interval)
        actual_discharge_power *= self.conf.charge_efficiency
        return actual_discharge_power

    def __str__(self) -> str:
        return f"Battery(SoC={self.residual_capacity/self.conf.total_capacity:.2%})"
