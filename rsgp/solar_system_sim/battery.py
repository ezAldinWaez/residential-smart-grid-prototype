from .data import BatteryConf
from ..utils.remote_object import expose
from ..config.constants import SECONDS_IN_HOUR
from ..config.settings import settings


@expose
class Battery:
    conf: BatteryConf  #: BattConf: The battery configuration
    charge_level: float  #: float: Current charge level of the battery [Wh]

    def __init__(self):

        self.conf = BatteryConf(
            capacity=settings.BATTERY_CAPACITY,
            charge_efficiency=settings.BATTERY_CHARGE_EFFICIENCY,
            max_charge_power=settings.BATTERY_MAX_CHARGE_POWER,
            max_discharge_power=settings.BATTERY_MAX_DISCHARGE_POWER,
        )

        self.charge_level = self.conf.capacity * settings.BATTERY_INIT_CHARGE_LEVEL

    def charge(self, power: float, time_interval: float) -> float:
        charge_power = min(power, self.conf.max_charge_power)
        charge_power *= self.conf.charge_efficiency
        charge_energy = charge_power * (time_interval / SECONDS_IN_HOUR)

        energy_to_full = self.conf.capacity - self.charge_level
        actual_charge_energy = min(charge_energy, energy_to_full)
        self.charge_level += actual_charge_energy

        actual_charge_power = actual_charge_energy * (SECONDS_IN_HOUR / time_interval)
        actual_charge_power /= self.conf.charge_efficiency
        return actual_charge_power

    def discharge(self, power: float, time_interval: float) -> float:
        discharge_power = min(power, self.conf.max_discharge_power)
        discharge_power /= self.conf.charge_efficiency
        discharge_energy = discharge_power * (time_interval / SECONDS_IN_HOUR)

        actual_discharge_energy = min(discharge_energy, self.charge_level)
        self.charge_level -= actual_discharge_energy

        actual_discharge_power = actual_discharge_energy * (SECONDS_IN_HOUR / time_interval)
        actual_discharge_power *= self.conf.charge_efficiency
        return actual_discharge_power

    def __str__(self):
        return f"Battery(charge_level={self.charge_level/self.conf.capacity:.2%})"
