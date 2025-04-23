"""House."""

from .data import RegularDevices
from .device import Device

import Pyro5


@Pyro5.api.expose
class House:
    """House state that holds a house status.

    Args:
        idx (int): House index.
    """
    idx: int  #: int: House index.
    #: dict[str, DeviceState]: Device state for each device in the house.
    devices: dict[str, Device]
    load: float = .0  #: float: Total load for the whole house.
    grid_line: bool = True  #: bool: Whether the grid line is connected.
    load_line: bool = True  #: bool: Whether the load line is connected.

    def __init__(self, idx: int):
        self.idx = idx
        self.devices = {
            device_name: Device(device_name)
            for device_name in RegularDevices.__members__
        }

    def toggle_grid_line(self):
        """Toggle the grid line status."""
        self.grid_line = not self.grid_line

    def toggle_load_line(self):
        """Toggle the load line status."""
        self.load_line = not self.load_line

    def get_idx(self) -> int:
        return int(self.idx)

    def get_devices(self) -> dict[str, Device]:
        return self.devices

    def get_device(self, dn: str) -> Device:
        return self.devices[dn]

    def get_load(self) -> float:
        return float(self.load)

    def get_grid_line(self) -> bool:
        return bool(self.grid_line)

    def get_load_line(self) -> bool:
        return bool(self.load_line)

    def set_grid_line(self, new_value: bool) -> None:
        self.grid_line = new_value

    def set_load_line(self, new_value: bool) -> None:
        self.load_line = new_value
