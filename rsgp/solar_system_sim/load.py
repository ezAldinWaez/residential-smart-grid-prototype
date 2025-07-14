"""Solar system simulated load."""

from ..utils.remote_interface import remote_interface_expose


@remote_interface_expose
class Load:
    is_connected: bool  #: bool: ...
    system_load: float  #: float: ...

    def __init__(self, init_connection_status: bool):
        self.is_connected = init_connection_status

    def get_system_load(self) -> float:
        return self.system_load

    def set_system_load(self, system_load):
        self.system_load = system_load

    def get_connection_status(self) -> bool:
        return self.is_connected

    def set_connection_status(self, new_status: bool):
        self.is_connected = new_status

    def __str__(self):
        return (
            f"Load State:\n"
            f"- Connection Status: {self.is_connected}\n"
            f"- System Load: {self.system_load}\n"
        )
