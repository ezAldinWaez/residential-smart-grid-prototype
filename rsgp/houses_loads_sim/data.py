"""Houses loads simulation data types."""

from dataclasses import dataclass
from enum import Enum
from typing import Literal


@dataclass
class ADSRConf:
    """ADSR (Attack, Decay, Sustain, and Release) model configuration."""
    a: float  #: float: Attack time [sec]
    d: float  #: float: Decay time [sec]
    s: float  #: float: Sustain level multiplier
    r: float  #: float: Release time [sec]
    #: Literal['none', 'sine', 'square', 'random']: Wave type
    wt: Literal['none', 'sine', 'square', 'random'] = 'none'
    wp: float = 1  #: float: Wave period [sec]
    wa: float = 0  #: float: Wave amplitude multiplier

    def __post_init__(self):
        assert self.a > 0
        assert self.d > 0
        assert 1 >= self.s >= 0
        assert self.r > 0
        assert self.wt in ['none', 'sine', 'square', 'random']
        assert self.wp > 0
        assert 1 >= self.wa >= 0


@dataclass
class DeviceConf:
    """Device configuration."""
    #: float: Maximum wattage that device can reach (maximum amplitude)
    base_watt: float  #: float: Device base wattage [Watt]
    max_count: int  #: int: Device maximum count a regular house could have
    adsr: ADSRConf  #: ADSRConf: Device ADSR configuration

    def __str__(self):
        return (
            "Device Configruation:\n"
            f"- base watt: {self.base_watt}\n"
            f"- max count: {self.max_count}\n"
            f"- adsr: {self.adsr}"
        )

    def __post_init__(self):
        assert self.base_watt >= 0
        assert self.max_count >= 0
        assert self.adsr is not None


class RegularDevices(Enum):
    """Some important regular house devices static configuration.

    Note:
        All members are from type :class:`DeviceConf`.
    """
    TEST = DeviceConf(
        base_watt=1000,
        max_count=10,
        adsr=ADSRConf(a=3600, d=7200, s=.8, r=1800),
    )

    LED_LIGHT = DeviceConf(
        base_watt=10,
        max_count=10,
        adsr=ADSRConf(a=.01, d=2, s=.8, r=.01),
    )

    TV = DeviceConf(
        base_watt=120,
        max_count=4,
        adsr=ADSRConf(a=1, d=1, s=.8, r=1.5, wt="sine", wp=.5, wa=.1),
    )

    REFRIGERATOR = DeviceConf(
        base_watt=150,
        max_count=2,
        adsr=ADSRConf(a=1, d=1, s=.3, r=2, wt="square", wp=3, wa=.06),
    )

    HVAC = DeviceConf(
        base_watt=3500,
        max_count=1,
        adsr=ADSRConf(a=3, d=2, s=.8, r=.5, wt="sine", wp=2, wa=.07),
    )

    WASHING_MACHINE = DeviceConf(
        base_watt=500,
        max_count=1,
        adsr=ADSRConf(a=2, d=2, s=.7, r=.5, wt="sine", wp=.5, wa=.04),
    )

    DRYER = DeviceConf(
        base_watt=3000,
        max_count=1,
        adsr=ADSRConf(a=2, d=1, s=.9, r=2, wt="sine", wp=2, wa=.03),
    )

    DISHWASHER = DeviceConf(
        base_watt=1800,
        max_count=1,
        adsr=ADSRConf(a=3, d=1.5, s=.6, r=2, wt="sine", wp=1, wa=.05),
    )

    WATER_HEATER = DeviceConf(
        base_watt=4500,
        max_count=1,
        adsr=ADSRConf(a=1, d=.5, s=.9, r=1, wt="square", wp=5, wa=.1),
    )

    MICROWAVE = DeviceConf(
        base_watt=1100,
        max_count=1,
        adsr=ADSRConf(a=.5, d=.2, s=1, r=.5),
    )
