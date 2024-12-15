from dataclasses import dataclass


@dataclass
class ApplianceSettings:
    """
    Attributes
    ----------
    - options : (Setting Name -> List of Options).
    - power_factors : (Setting Name -> (Option Name -> Multiplier)).
    """
    options: dict[str, list[str]]
    power_factors: dict[str, dict[str, float]]

    def __post_init__(self):
        for setting, options in self.power_factors.items():
            for option, multiplier in options.items():
                assert (option in self.options.get(setting))
                assert (multiplier > 0)


@dataclass
class ADSRParams:
    """
    Attributes
    ----------
    - a : Attack Time (in sec).
    - d : Decay Time (in sec).
    - s : Sustain Level (between 0 and 1).
    - r : Release Time (in sec).
    - wt : Wave Type ("none" | "sine" | "square" | "random").
    - wp : Wave Period (in sec).
    - wa : Wave Amplitude (between 0 and 1).
    """
    a: float
    d: float
    s: float
    r: float
    wt: str = "none"
    wp: float = 1
    wa: float = 0

    def __post_init__(self):
        assert (self.a > 0)
        assert (self.d > 0)
        assert (1 >= self.s >= 0)
        assert (self.r > 0)
        assert (self.wt in ["none", "sine", "square", "random"])
        assert (self.wp > 0)
        assert (1 >= self.wa >= 0)


#: Devices Configuration contains some regular house devices with some static info for each device.
#: Shape: Device Name -> (wattage -> float, max_count -> int, adsr -> ADSRParams, settings: ApplianceSettings)
#: where:
#: - `wattage` : Maximum wattage that device can reach. (you can call it Maximum Amplitude)
#: - `max_count` : Maximum count a regular house could contains from that device.
#: - `adsr` : ADSRParams for the device.
#: - `settings` (optional) : ApplianceSettings for the device.
DEVICES_CONFIG = {
    "Test Device": {
        "wattage": 1000,
        "max_count": 10,
        "adsr": ADSRParams(a=360, d=200, s=0.8, r=10, wt="random", wp=1, wa=.050),
    },
    "LED Light": {
        "wattage": 10,
        "max_count": 20,
        "adsr": ADSRParams(a=0.01, d=2, s=0.8, r=0.01),
    },
    "TV/Entertainment": {
        "wattage": 120,
        "max_count": 4,
        "adsr": ADSRParams(a=1.0, d=1.0, s=0.8, r=1.5, wt="sine", wp=.5, wa=0.1),
    },
    "Refrigerator": {
        "wattage": 150,
        "max_count": 2,
        "adsr": ADSRParams(a=1.0, d=1.0, s=0.3, r=2.0, wt="square", wp=3, wa=0.06),
    },
    "HVAC": {
        "wattage": 3500,
        "max_count": 1,
        "adsr": ADSRParams(a=3.0, d=2.0, s=0.8, r=0.5, wt="sine", wp=2, wa=0.07),
    },
    "Washing Machine": {
        "wattage": 500,
        "max_count": 1,
        "adsr": ADSRParams(a=2.0, d=2.0, s=0.7, r=0.5, wt="sine", wp=.5, wa=0.04),
        "settings": ApplianceSettings(
            options={
                "program": ["Quick Wash", "Normal", "Heavy Duty", "Delicate"],
                "temperature": ["Cold", "Warm", "Hot"],
                "spin_speed": ["Low", "Medium", "High"]
            },
            power_factors={
                "program": {
                    "Quick Wash": 0.7,
                    "Normal": 1.0,
                    "Heavy Duty": 1.3,
                    "Delicate": 0.8
                },
                "temperature": {
                    "Cold": 0.6,
                    "Warm": 1.0,
                    "Hot": 1.4
                },
                "spin_speed": {
                    "Low": 0.8,
                    "Medium": 1.0,
                    "High": 1.2
                }
            }
        )
    },
    "Dryer": {
        "wattage": 3000,
        "max_count": 1,
        "adsr": ADSRParams(a=2.0, d=1.0, s=0.9, r=2.0, wt="sine", wp=2, wa=0.03),
        "settings": ApplianceSettings(
            options={
                "program": ["Quick Dry", "Normal", "Heavy Duty", "Delicate"],
                "temperature": ["Low", "Medium", "High"],
                "time": ["30 min", "60 min", "90 min"]
            },
            power_factors={
                "program": {
                    "Quick Dry": 0.8,
                    "Normal": 1.0,
                    "Heavy Duty": 1.2,
                    "Delicate": 0.7
                },
                "temperature": {
                    "Low": 0.7,
                    "Medium": 1.0,
                    "High": 1.3
                },
                "time": {
                    "30 min": 1.0,
                    "60 min": 1.0,
                    "90 min": 1.0
                }
            }
        )
    },
    "Dishwasher": {
        "wattage": 1800,
        "max_count": 1,
        "adsr": ADSRParams(a=3.0, d=1.5, s=0.6, r=2.0, wt="sine", wp=1, wa=0.05),
        "settings": ApplianceSettings(
            options={
                "program": ["Quick", "Eco", "Normal", "Intensive"],
                "temperature": ["Low", "Medium", "High"],
                "dry": ["No Heat", "Heat Dry"]
            },
            power_factors={
                "program": {
                    "Quick": 0.8,
                    "Eco": 0.6,
                    "Normal": 1.0,
                    "Intensive": 1.4
                },
                "temperature": {
                    "Low": 0.7,
                    "Medium": 1.0,
                    "High": 1.3
                },
                "dry": {
                    "No Heat": 0.7,
                    "Heat Dry": 1.2
                }
            }
        )
    },
    "Water Heater": {
        "wattage": 4500,
        "max_count": 1,
        "adsr": ADSRParams(a=1.0, d=0.5, s=0.9, r=1.0, wt="square", wp=5, wa=0.1),
    },
    "Microwave": {
        "wattage": 1100,
        "max_count": 1,
        "adsr": ADSRParams(a=0.5, d=0.2, s=1.0, r=0.5),
    }
}
