"""Solar system simulation data."""

from dataclasses import dataclass


@dataclass
class PVConf:
    """PV configuration data type."""
    num_panels: int  #: int: Panels count.
    panel_area: float  #: float: Panel area. [m^2]
    panel_efficiency: float  #: float: Panel efficiency multiplier.

    def __str__(self):
        return (
            "\n"
            "PV Configuration:\n"
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

    capacity: float  #: float: Total capacity of the battery. [Wh]
    charge_efficiency: float  #: float: Efficiency of charging. [%]
    max_charge_power: float  #: float: Maximum charge rate. [W]
    max_discharge_power: float  #: float: Maximum discharge rate. [W]

    def __post_init__(self):
        assert self.capacity > 0
        assert 0 < self.charge_efficiency <= 1
        assert self.max_charge_power > 0
        assert self.max_discharge_power > 0

    def __str__(self):
        return (
            "\n"
            "Battery Configuration:\n"
            f"- Capacity: {self.capacity}\n"
            f"- Charge Efficiency: {self.charge_efficiency}\n"
            f"- Max Charge Power: {self.max_charge_power}\n"
            f"- Max Discharge Power: {self.max_discharge_power}\n"
        )
