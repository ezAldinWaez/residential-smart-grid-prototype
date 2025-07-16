"""Solar system simulated utility."""
from ..utils.remote_interface import remote_interface_expose


@remote_interface_expose
class Utility:
    is_connected: bool  #: bool: ...
    exchange_power_ac: float  #: float: ...

    def __init__(self, init_connection_status: bool):
        self.is_connected = init_connection_status
        self.exchange_power_ac = 0.0

    def get_connection_status(self) -> bool:
        return self.is_connected

    def set_connection_status(self, new_status: bool):
        self.is_connected = new_status

    #TODO: do something with the exported and imported power; maybe to log and track it
    def export_power(self, power_ac: float) -> None:
        self.exchange_power_ac += power_ac

    def import_power(self, power_ac: float) -> None:
        self.exchange_power_ac -= power_ac
    
    def clear_exchange_power(self) -> None:
        self.exchange_power_ac = 0.0

    def __str__(self):
        return (
            f"Utility State:\n"
            f"- Connection Status: {self.is_connected}\n"
            f"- Exchange Power AC: {self.exchange_power_ac}\n"
        )
