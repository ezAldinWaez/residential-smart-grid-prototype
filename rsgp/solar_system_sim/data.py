"""Solar system simulation data types."""

from dataclasses import dataclass
from enum import Enum


@dataclass
class PanelsConf:
    """Panels configuration data type."""

    num_panels: int  #: int: Panels count.
    panel_area: float  #: float: Panel area [m^2].
    panel_efficiency: float  #: float: Panel efficiency multiplier.

    def __post_init__(self) -> None:
        assert self.num_panels > 0
        assert self.panel_area > 0
        assert 0 < self.panel_efficiency <= 1

    def __str__(self) -> str:
        return f"PanelsConf(num_panels={self.num_panels}, panel_area={self.panel_area}, panel_efficiency={self.panel_efficiency})"


@dataclass
class BatteryConf:
    """Battery configuration data type."""
    total_capacity: float  #: float: Total capacity of the battery [Wh].
    charge_efficiency: float  #: float: Efficiency of charging [%].
    max_charge_power: float  #: float: Maximum charge rate [Watt].
    max_discharge_power: float  #: float: Maximum discharge rate [Watt].

    def __post_init__(self) -> None:
        assert self.total_capacity > 0
        assert 0 < self.charge_efficiency <= 1
        assert self.max_charge_power > 0
        assert self.max_discharge_power > 0

    def __str__(self) -> str:
        return f"BatteryConf(capacity={self.total_capacity}, charge_efficiency={self.charge_efficiency}, max_charge_power={self.max_charge_power}, max_discharge_power={self.max_discharge_power})"


class InverterMode(Enum):
    """Inverter operating modes."""

    SBU = "SBU"
    SUB = "SUB"
    USB = "USB"


class ChargePriority(Enum):
    """Inverter charge priority."""

    SOLAR_ONLY = "Solar Only"
    SOLAR_FIRST = "Solar First"
    UTILITY_AND_SOLAR = "Utility + Solar"


@dataclass
class InverterConf:
    """Inverter configuration data type."""

    paco: float  #: float: AC Power rating of the inverter [Watt].
    pdco: float  # float: DC Power rating of the inverter [Watt].
    pnt: float  #: float: AC power consumed by the inverter at night [Watt].
    eta_inv_nom: float  #: float: Nominal efficiency of the inverter [%].
    eta_inv_ref: float  #: float: Reference efficiency of the inverter [%].
    eta_inv_ovr: float  #: float: Overall efficiency of the inverter [%].
    mode: InverterMode  #: InverterMode: The current operating mode of the inverter.
    charge_priority: ChargePriority  #: ChargePriority: The current charge priority of the inverter.

    def __post_init__(self) -> None:
        assert self.paco > self.pnt >= 0
        assert self.pdco > 0
        assert 0 < self.eta_inv_nom <= 1
        assert 0 < self.eta_inv_ref <= 1
        assert 0 < self.eta_inv_ovr <= 1

    def __str__(self) -> str:
        return f"InverterConf(mode={self.mode}, charge_priority={self.charge_priority}, paco={self.paco}, pdco={self.pdco}, pnt={self.pnt}, eta_inv_nom={self.eta_inv_nom}, eta_inv_ref={self.eta_inv_ref}, eta_inv_ovr={self.eta_inv_ovr})"
