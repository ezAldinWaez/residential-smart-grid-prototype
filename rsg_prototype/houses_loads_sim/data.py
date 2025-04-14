"""Houses loads simulation data."""

from dataclasses import dataclass
from enum import Enum
from typing import Literal


@dataclass
class SettingsConf:
    """Settings configuration."""

    #: dict[str, list[str]]: list of all options for each device setting.
    #:  (Setting Name -> List of Options)
    options: dict[str, list[str]]
    #: dict[str, dict[str, float]]: power multiplier for each option for each device
    #:  setting. (Setting Name -> (Option Name -> Power Multiplier))
    power_factors: dict[str, dict[str, float]]

    def __post_init__(self):
        for setting, options in self.power_factors.items():
            for option, multiplier in options.items():
                assert option in self.options.get(setting)
                assert multiplier > 0


@dataclass
class ADSRConf:
    """ADSR (Attack, Decay, Sustain, and Release) model configuration."""

    a: float  #: float: Attack Time. [sec]
    d: float  #: float: Decay Time. [sec]
    s: float  #: float: Sustain Level Multiplier.
    r: float  #: float: Release Time. [sec]
    #: Literal['none', 'sine', 'square', 'random']: Wave Type.
    wt: Literal['none', 'sine', 'square', 'random'] = 'none'
    wp: float = 1  #: float: Wave Period. [sec]
    wa: float = 0  #: float: Wave Amplitude Multiplier.

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

    #: float: Maximum wattage that device can reach (maximum amplitude).
    base_watt: float
    max_count: int  #: int: Device maximum count a regular house could have.
    adsr: ADSRConf  #: ADSRConf: Device ADSR configuration.
    #: SettingsConf: Device settings configuration.
    settings: SettingsConf = None

    def __str__(self):
        return (
            "\n"
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
        settings=SettingsConf(
            options={
                "program": ["Quick Wash", "Normal", "Heavy Duty", "Delicate"],
                "temperature": ["Cold", "Warm", "Hot"],
                "spin_speed": ["Low", "Medium", "High"],
            },
            power_factors={
                "program": {
                    "Quick Wash": .7,
                    "Normal": 1,
                    "Heavy Duty": 1.3,
                    "Delicate": .8
                },
                "temperature": {
                    "Cold": .6,
                    "Warm": 1,
                    "Hot": 1.4
                },
                "spin_speed": {
                    "Low": .8,
                    "Medium": 1,
                    "High": 1.2
                },
            },
        ),
    )

    DRYER = DeviceConf(
        base_watt=3000,
        max_count=1,
        adsr=ADSRConf(a=2, d=1, s=.9, r=2, wt="sine", wp=2, wa=.03),
        settings=SettingsConf(
            options={
                "program": ["Quick Dry", "Normal", "Heavy Duty", "Delicate"],
                "temperature": ["Low", "Medium", "High"],
                "time": ["30 min", "60 min", "90 min"],
            },
            power_factors={
                "program": {
                    "Quick Dry": .8,
                    "Normal": 1,
                    "Heavy Duty": 1.2,
                    "Delicate": .7
                },
                "temperature": {
                    "Low": .7,
                    "Medium": 1,
                    "High": 1.3
                },
                "time": {
                    "30 min": 1,
                    "60 min": 1,
                    "90 min": 1
                },
            },
        ),
    )

    DISHWASHER = DeviceConf(
        base_watt=1800,
        max_count=1,
        adsr=ADSRConf(a=3, d=1.5, s=.6, r=2, wt="sine", wp=1, wa=.05),
        settings=SettingsConf(
            options={
                "program": ["Quick", "Eco", "Normal", "Intensive"],
                "temperature": ["Low", "Medium", "High"],
                "dry": ["No Heat", "Heat Dry"],
            },
            power_factors={
                "program": {
                    "Quick": .8,
                    "Eco": .6,
                    "Normal": 1,
                    "Intensive": 1.4
                },
                "temperature": {
                    "Low": .7,
                    "Medium": 1,
                    "High": 1.3
                },
                "dry": {
                    "No Heat": .7,
                    "Heat Dry": 1.2
                },
            },
        ),
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
