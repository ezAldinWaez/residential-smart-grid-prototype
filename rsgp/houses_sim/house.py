from .data import RegularDevices
from .device import DeviceClass
from ..remote_object import expose


@expose
class House:
    idx: int  #: int: House index.
    devices: dict[str, DeviceClass]  #: dict[str, Device]: Devices in the house
    load_line: bool = True  #: bool: Flag for load line state (connected=1, disconnected=0)
    load_power: float  #: float: Total load for the house
    utility_line: bool = True  #: bool: Flag for utility line state (connected=1, disconnected=0)
    utility_exchange_power: float  #: float: Total power from/to the utility for the house
    utility_exchange_power_aggregated: float  #: float: Aggregated total power from/to the utility for the house

    def __init__(self, idx: int):
        self.idx = idx
        self.load_power = 0.0
        self.utility_exchange_power = 0.0
        self.utility_exchange_power_aggregated = 0.0

        self.devices = {
            device_name: DeviceClass(device_name)
            for device_name in RegularDevices.__members__
        }

    def toggle_utility_line(self):
        self.utility_line = not self.utility_line

    def toggle_load_line(self):
        self.load_line = not self.load_line

    def get_idx(self) -> int:
        return int(self.idx)

    def get_devices(self) -> dict[str, DeviceClass]:
        return self.devices

    def get_device(self, dn: str) -> DeviceClass:
        return self.devices[dn]

    def get_load(self) -> float:
        return float(self.load_power)

    def get_utility_line(self) -> bool:
        return bool(self.utility_line)

    def get_load_line(self) -> bool:
        return bool(self.load_line)

    def set_utility_line(self, new_value: bool) -> None:
        self.utility_line = new_value

    def set_load_line(self, new_value: bool) -> None:
        self.load_line = new_value

    def __str__(self):
        return f"House(idx={self.idx}, load_power={self.load_power:.2f}, load_line={self.load_line}, utility_power={self.utility_exchange_power:.2f}, utility_line={self.utility_line})"
