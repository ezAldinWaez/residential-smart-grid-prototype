"""Virtual Battery to be used for each house."""

from ..remote_object import expose


@expose
class VirtualBattery:
    def __init__(self, idx: int, capacity, init_charge_level):
        self.idx = idx
        self.capacity = capacity
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
