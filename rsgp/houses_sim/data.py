"""Houses simulation data and data types."""

from dataclasses import dataclass
from enum import Enum
from typing import Literal


@dataclass
class ADSRConf:
    """ADSR (Attack-Decay-Sustain-Release) envelope configuration."""

    a: float  #: float: Attack time [sec].
    d: float  #: float: Decay time [sec].
    s: float  #: float: Sustain level multiplier.
    r: float  #: float: Release time [sec].
    wt: Literal['none', 'sine', 'square', 'random'] = 'none'  #: Literal['none', 'sine', 'square', 'random']: Wave type.
    wp: float = 1  #: float: Wave period [sec].
    wa: float = 0  #: float: Wave amplitude multiplier.

    def __post_init__(self) -> None:
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

    base_watt: float  #: float: Device base wattage (maximum amplitude) [Watt].
    max_count: int  #: int: Device maximum count a regular house could have.
    adsr: ADSRConf  #: ADSRConf: Device ADSR configuration.

    def __post_init__(self) -> None:
        assert self.base_watt >= 0
        assert self.max_count >= 0
        assert self.adsr is not None

    def __str__(self) -> str:
        return f"DeviceConf(base_watt={self.base_watt}, max_count={self.max_count}, adsr={self.adsr})"


class RegularDevices(Enum):
    """Regular household devices with their configurations."""

    TEST = DeviceConf(
        base_watt=1000,
        max_count=10,
        adsr=ADSRConf(a=3600, d=7200, s=.8, r=1800),
    )  #: DeviceConf: Test Device.

    LED_LIGHT = DeviceConf(
        base_watt=10,
        max_count=10,
        adsr=ADSRConf(a=.01, d=2, s=.8, r=.01),
    )  #: DeviceConf: LED Light.

    TV = DeviceConf(
        base_watt=120,
        max_count=4,
        adsr=ADSRConf(a=1, d=1, s=.8, r=1.5, wt="sine", wp=.5, wa=.1),
    )  #: DeviceConf: TV.

    REFRIGERATOR = DeviceConf(
        base_watt=50,
        max_count=2,
        adsr=ADSRConf(a=0.5, d=0.5, s=.9, r=1, wt="square", wp=5, wa=.02),
    )  #: DeviceConf: Refrigerator.

    HVAC = DeviceConf(
        base_watt=3500,
        max_count=1,
        adsr=ADSRConf(a=3, d=2, s=.8, r=.5, wt="sine", wp=2, wa=.07),
    )  #: DeviceConf:   #: DeviceConf: HVAC (Heating, Ventilation, and Air Conditioning).

    WASHING_MACHINE = DeviceConf(
        base_watt=500,
        max_count=1,
        adsr=ADSRConf(a=2, d=2, s=.7, r=.5, wt="sine", wp=.5, wa=.04),
    )  #: DeviceConf: Washing machine.

    DRYER = DeviceConf(
        base_watt=3000,
        max_count=1,
        adsr=ADSRConf(a=2, d=1, s=.9, r=2, wt="sine", wp=2, wa=.03),
    )  #: DeviceConf: Dryer.

    DISHWASHER = DeviceConf(
        base_watt=1800,
        max_count=1,
        adsr=ADSRConf(a=3, d=1.5, s=.6, r=2, wt="sine", wp=1, wa=.05),
    )  #: DeviceConf: Dish washer.

    WATER_HEATER = DeviceConf(
        base_watt=4500,
        max_count=1,
        adsr=ADSRConf(a=1, d=.5, s=.9, r=1, wt="square", wp=5, wa=.1),
    )  #: DeviceConf: Water Heater.

    MICROWAVE = DeviceConf(
        base_watt=1100,
        max_count=1,
        adsr=ADSRConf(a=.5, d=.2, s=1, r=.5, wt='random', wp=.5, wa=.05),
    )  #: DeviceConf: Micro-wave.
