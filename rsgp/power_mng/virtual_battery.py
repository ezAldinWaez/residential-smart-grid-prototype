from ..remote_object import expose
from ..config.settings import settings

@expose
class VirtualBattery:
    def __init__(self, idx: int, capacity, init_charge_level):
        self.idx = idx
        self.initial_capacity = capacity
        self.weight = 1.0
        self.capacity = self.initial_capacity * self.weight
        self.charge_level = init_charge_level

    def charge(self, power) -> float:
        new_level = self.charge_level + power
        new_level = min(new_level, self.capacity)
        charged_power = new_level - self.charge_level
        self.charge_level = new_level
        return charged_power

    def discharge(self, power) -> float:
        new_level = self.charge_level - power
        new_level = min(new_level, 0.0)
        discharged_power = self.charge_level - new_level
        self.charge_level = new_level
        return discharged_power
    
    def adjust_weight(self, amount):
        self.weight += amount
        self.weight = max(settings.GUARANTEED_MINIMUM_WEIGHT, self.weight)
        self.capacity = self.initial_capacity * self.weight
        self.charge_level = min(self.charge_level, self.capacity)

    def __str__(self):
        return f"VirtualBattery(idx={self.idx}, weight={self.weight:.3f}, capacity={self.capacity:.3f}, charge_level={self.charge_level:.3f})"
