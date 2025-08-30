"""Houses simulation house."""

from .data import RegularDevices
from .device import DeviceClass

from Pyro5.api import expose


@expose
class House:
    """House.

    Args:
        idx (int): House index.

    """

    idx: int  #: int: House index.
    devices: dict[str, DeviceClass]  #: dict[str, Device]: Devices in the house.
    load_line: bool = True  #: bool: Flag for load line state (connected=1, disconnected=0).
    load_power: float  #: float: Total load for the house.
    utility_line: bool = True  #: bool: Flag for utility line state (connected=1, disconnected=0).
    utility_exchange_power: float  #: float: Total power from/to the utility for the house (+ === export, - === import)

    def __init__(self, idx: int) -> None:
        self.idx = idx
        self.load_power = 0.0
        self.utility_exchange_power = 0.0

        self.devices = {
            device_name: DeviceClass(device_name)
            for device_name in RegularDevices.__members__
        }

    def toggle_utility_line(self) -> None:
        """Toggle the utility line state."""
        self.utility_line = not self.utility_line

    def toggle_load_line(self) -> None:
        """Toggle the load line state."""
        self.load_line = not self.load_line

    def get_idx(self) -> int:
        """Get house index.

        Returns:
            int: House index.

        """
        return int(self.idx)

    def get_devices(self) -> dict[str, DeviceClass]:
        """Get devices in the house.

        Returns:
            dict[str, Device]: Devices in the house.

        """
        return self.devices

    def get_device(self, dn: str) -> DeviceClass:
        """Get a specific device in the house.

        Args:
            dn (str): Device name.

        Returns:
            Device: Device object.

        """
        return self.devices[dn]

    def get_load(self) -> float:
        """Get total load for the house.

        Returns:
            float: Total load for the house.

        """
        return float(self.load_power)

    def get_utility_line(self) -> bool:
        """Get utility line state.

        Returns:
            bool: Utility line state (connected=1, disconnected=0).

        """
        return bool(self.utility_line)

    def get_load_line(self) -> bool:
        """Get load line state.

        Returns:
            bool: Load line state (connected=1, disconnected=0).

        """
        return bool(self.load_line)

    def set_utility_line(self, new_value: bool) -> None:
        """Set utility line state.

        Args:
            new_value (bool): New utility line state.

        """
        self.utility_line = new_value

    def set_load_line(self, new_value: bool) -> None:
        """Set load line state.

        Args:
            new_value (bool): New load line state.

        """
        self.load_line = new_value

    def __str__(self) -> str:
        return f"House(idx={self.idx}, load_power={self.load_power:.2f}, load_line={self.load_line}, utility_power={self.utility_exchange_power:.2f}, utility_line={self.utility_line})"
