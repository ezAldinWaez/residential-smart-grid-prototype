"""House."""

from .data import RegularDevices
from .device import Device
from ..utils.remote_interface import remote_interface_expose


@remote_interface_expose
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
        """Get the house index.

        Returns:
            int: the house index.
        """
        return int(self.idx)

    def get_devices(self) -> dict[str, Device]:
        """Get all devices as a dictionary.

        Returns:
            dict[str, Device]: all devices dictionary (device_name -> device instance).
        """
        return self.devices

    def get_device(self, dn: str) -> Device:
        """Get the device instance by it's name.

        Args:
            dn (str): device name.

        Returns:
            Device: the device instance.
        """
        return self.devices[dn]

    def get_load(self) -> float:
        """Get the house current load.

        Returns:
            float: the house load. [Watt]
        """
        return float(self.load)

    def get_grid_line(self) -> bool:
        """Get grid line value.

        Returns:
            bool: grid line value.
        """
        return bool(self.grid_line)

    def get_load_line(self) -> bool:
        """Get load line value.

        Returns:
            bool: load line value.
        """
        return bool(self.load_line)

    def set_grid_line(self, new_value: bool) -> None:
        """Set grid line.

        Args:
            new_value (bool): the grid line new value.
        """
        self.grid_line = new_value

    def set_load_line(self, new_value: bool) -> None:
        """Set load line.

        Args:
            new_value (bool): the load line new value.
        """
        self.load_line = new_value
