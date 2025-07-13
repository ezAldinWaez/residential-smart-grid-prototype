"""House."""

# TODO: Document this module.

from .data import RegularDevices
from .device import Device
from ..utils.remote_interface import remote_interface_expose


@remote_interface_expose
class House:
    idx: int  #: int: House index.
    devices: dict[str, Device]  #: dict[str, Device]: Devices in the house
    load: float  #: float: Total load for the house
    grid_line: bool = True  #: bool: Flag for grid line state (connected=1, disconnected=0)
    load_line: bool = True  #: bool: Flag for load line state (connected=1, disconnected=0)

    def __init__(self, idx: int):
        self.idx = idx
        self.load = 0.0
        self.devices = {
            device_name: Device(device_name)
            for device_name in RegularDevices.__members__
        }

    def toggle_grid_line(self):
        self.grid_line = not self.grid_line

    def toggle_load_line(self):
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
