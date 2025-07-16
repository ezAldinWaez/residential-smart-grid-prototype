"""Solar system simulation data."""

from dataclasses import dataclass
from enum import Enum

@dataclass
class PanelsConf:
    """Panels configuration data type."""
    num_panels: int  #: int: Panels count
    panel_area: float  #: float: Panel area [m^2]
    panel_efficiency: float  #: float: Panel efficiency multiplier

    def __str__(self):
        return (
            "Panels Configuration:\n"
            f"- Panels Count: {self.num_panels}\n"
            f"- Panel Area: {self.panel_area}\n"
            f"- Panel Efficiency: {self.panel_efficiency}\n"
        )

    def __post_init__(self):
        assert self.num_panels > 0
        assert self.panel_area > 0
        assert 0 < self.panel_efficiency <= 1


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
            "Battery Configuration:\n"
            f"- Capacity: {self.capacity}\n"
            f"- Charge Efficiency: {self.charge_efficiency}\n"
            f"- Max Charge Power: {self.max_charge_power}\n"
            f"- Max Discharge Power: {self.max_discharge_power}\n"
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
    paco: float  #: AC Power rating of the inverter [Watt]
    pdco: float  # : DC Power rating of the inverter [Watt]
    pnt: float  #: AC power consumed by the inverter at night [Watt]
    eta_inv_nom: float  #: ...
    eta_inv_ref: float  #: ...
    eta_inv_ovr: float  #: ...
    mode: InverterMode #: ...
    charge_priority: ChargePriority

    def __post_init__(self):
        assert self.paco > self.pnt >= 0
        assert self.pdco > 0
        assert 0 < self.eta_inv_nom <= 1
        assert 0 < self.eta_inv_ref <= 1
        assert 0 < self.eta_inv_ovr <= 1

    def __str__(self):
        return (
            "Inverter Configuration:\n"
            f"- Inverter Mode: {self.mode}\n"
            f"- Battery Charge Priority: {self.charge_priority}\n"
            f"- AC Power Rating: {self.paco}\n"
            f"- DC Power Rating: {self.pdco}\n"
            f"- Night Consumption: {self.pnt}\n"
            f"- Nominal Efficiency: {self.eta_inv_nom}\n"
            f"- Reference Efficiency: {self.eta_inv_ref}\n"
            f"- Overall Efficiency: {self.eta_inv_ovr}\n"
        )