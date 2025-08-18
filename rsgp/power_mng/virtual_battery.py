from ..remote_object import expose
from ..config.settings import settings
from ..config.constants import SECONDS_IN_HOUR

@expose
class VirtualBattery:
    def __init__(self, idx: int, init_capacity, init_charge_level, charge_efficiency, time_interval):
        self.idx = idx
        self.initial_capacity = init_capacity
        self.weight = 1.0
        self.capacity = self.initial_capacity * self.weight
        self.charge_level = init_charge_level
        self.charge_efficiency = charge_efficiency
        self.time_interval = time_interval

    def charge(self, power) -> float:
        power *= self.charge_efficiency
        charge_energy = power * (self.time_interval / SECONDS_IN_HOUR)

        energy_to_full = self.capacity - self.charge_level
        actual_charge_energy = min(charge_energy, energy_to_full)
        self.charge_level += actual_charge_energy

        actual_charge_power = actual_charge_energy * (SECONDS_IN_HOUR / self.time_interval)
        actual_charge_power /= self.charge_efficiency
        return actual_charge_power

    def discharge(self, power) -> float:
        power /= self.charge_efficiency
        discharge_energy = power * (self.time_interval / SECONDS_IN_HOUR)

        actual_discharge_energy = min(discharge_energy, self.charge_level)
        self.charge_level -= actual_discharge_energy

        actual_discharge_power = actual_discharge_energy * (SECONDS_IN_HOUR / self.time_interval)
        actual_discharge_power *= self.charge_efficiency
        return actual_discharge_power
    
    def adjust_weight(self, amount):
        self.weight += amount
        self.weight = max(settings.GUARANTEED_MINIMUM_WEIGHT, self.weight)
        self.capacity = self.initial_capacity * self.weight
        self.charge_level = min(self.charge_level, self.capacity)

    def __str__(self):
        return f"VirtualBattery(idx={self.idx}, weight={self.weight:.3f}, capacity={self.capacity:.3f}, charge_level={self.charge_level:.3f})"
