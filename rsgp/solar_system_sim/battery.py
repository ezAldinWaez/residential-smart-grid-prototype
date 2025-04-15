"""Solar system simulated battery."""

from .data import BattConf

from ..config import settings


class Battery:
    """Solar system simulated battery.

    Args:
        init_charge_level (float): The initialized charge level for the battery. [%]
    """
    conf: BattConf  #: BattConf: The battery configuration.
    charge_level: float  #: float: Current charge level of the battery. [Wh]

    def __init__(self, init_charge_level: float):
        assert 0 <= init_charge_level <= 1

        self.conf = BattConf(
            capacity=settings.BATTERY_CAPACITY,
            charge_efficiency=settings.BATTERY_CHARGE_EFFICIENCY,
            max_charge_power=settings.BATTERY_MAX_CHARGE_POWER,
            max_discharge_power=settings.BATTERY_MAX_DISCHARGE_POWER,
        )
        self.charge_level = self.conf.capacity * init_charge_level

    def charge(self, power: float, time: float) -> float:
        """Simulate the battery charging.

        Args:
            power (float): The power available for charging. [W]
            time (float): The time interval. [sim_sec]

        Returns:
            float: The power actually used for charging. [W]
        """
        charge_power = min(power, self.conf.max_charge_power)
        charge_power *= self.conf.charge_efficiency
        charge_energy = charge_power * (time / 3600)

        energy_to_full = self.conf.capacity - self.charge_level
        actual_charge_energy = min(charge_energy, energy_to_full)
        self.charge_level += actual_charge_energy

        actual_charge_power = actual_charge_energy * (3600 / time)
        actual_charge_power /= self.conf.charge_efficiency
        return actual_charge_power

    def discharge(self, power: float, time: float) -> float:
        """Simulate the battery discharging.

        Args:
            power (float): The power required. [W]
            time (float): The time interval. [sim_sec]

        Returns:
            float: The power actually provided by the battery.

        """
        discharge_power = min(power, self.conf.max_discharge_power)
        discharge_power /= self.conf.charge_efficiency
        discharge_energy = discharge_power * (time / 3600)

        actual_discharge_energy = min(discharge_energy, self.charge_level)
        self.charge_level -= actual_discharge_energy

        actual_discharge_power = actual_discharge_energy * (3600 / time)
        actual_discharge_power *= self.conf.charge_efficiency
        return actual_discharge_power

    def __str__(self):
        return (
            f"Battery State: {self.charge_level:.2f} / {self.conf.capacity:.2f} Wh "
            f"({self.charge_level / self.conf.capacity:.2%})"
        )
