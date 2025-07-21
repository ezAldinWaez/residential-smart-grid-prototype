"""Solar system simulation data."""

from dataclasses import dataclass
from enum import Enum


@dataclass
class PanelsConf:
    """Panels configuration data type."""
    num_panels: int  #: int: Panels count
    panel_area: float  #: float: Panel area [m^2]
    panel_efficiency: float  #: float: Panel efficiency multiplier

    def __post_init__(self):
        assert self.num_panels > 0
        assert self.panel_area > 0
        assert 0 < self.panel_efficiency <= 1

    def __str__(self):
        return (
            "\n"
            f"\t\t- Panels Count: {self.num_panels}\n"
            f"\t\t- Panel Area: {self.panel_area}\n"
            f"\t\t- Panel Efficiency: {self.panel_efficiency}"
        )


@dataclass
class BattConf:
    """Battery configuration data type."""
    capacity: float  #: float: Total capacity of the battery [Wh]
    charge_efficiency: float  #: float: Efficiency of charging [%]
    max_charge_power: float  #: float: Maximum charge rate [Watt]
    max_discharge_power: float  #: float: Maximum discharge rate [Watt]

    def __post_init__(self):
        assert self.capacity > 0
        assert 0 < self.charge_efficiency <= 1
        assert self.max_charge_power > 0
        assert self.max_discharge_power > 0

    def __str__(self):
        return (
            "\n"
            f"\t\t- Capacity: {self.capacity}\n"
            f"\t\t- Charge Efficiency: {self.charge_efficiency}\n"
            f"\t\t- Max Charge Power: {self.max_charge_power}\n"
            f"\t\t- Max Discharge Power: {self.max_discharge_power}"
        )


class InverterMode(Enum):
    SBU = "SBU"
    SUB = "SUB"
    USB = "USB"


class ChargePriority(Enum):
    SOLAR_ONLY = "Solar Only"
    SOLAR_FIRST = "Solar First"
    UTILITY_AND_SOLAR = "Utility + Solar"


@dataclass
class InverterConf:
    """Inverter configuration data type."""
    paco: float  #: float: AC Power rating of the inverter [Watt]
    pdco: float  # float: DC Power rating of the inverter [Watt]
    pnt: float  #: float: AC power consumed by the inverter at night [Watt]
    eta_inv_nom: float  #: float: Nominal efficiency of the inverter [%]
    eta_inv_ref: float  #: float: Reference efficiency of the inverter [%]
    eta_inv_ovr: float  #: float: Overall efficiency of the inverter [%]
    mode: InverterMode  #: InverterMode: The current operating mode of the inverter
    charge_priority: ChargePriority  #: ChargePriority: The current charge priority of the inverter

    def __post_init__(self):
        assert self.paco > self.pnt >= 0
        assert self.pdco > 0
        assert 0 < self.eta_inv_nom <= 1
        assert 0 < self.eta_inv_ref <= 1
        assert 0 < self.eta_inv_ovr <= 1

    def __str__(self):
        return (
            "\n"
            f"\t\t- Inverter Mode: {self.mode}\n"
            f"\t\t- Battery Charge Priority: {self.charge_priority}\n"
            f"\t\t- AC Power Rating: {self.paco}\n"
            f"\t\t- DC Power Rating: {self.pdco}\n"
            f"\t\t- Night Consumption: {self.pnt}\n"
            f"\t\t- Nominal Efficiency: {self.eta_inv_nom}\n"
            f"\t\t- Reference Efficiency: {self.eta_inv_ref}\n"
            f"\t\t- Overall Efficiency: {self.eta_inv_ovr}"
        )
