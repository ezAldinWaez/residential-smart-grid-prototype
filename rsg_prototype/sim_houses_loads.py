"""Simulation for the houses loads."""

from dataclasses import dataclass
from enum import Enum
import random
import threading
import time
import os

import numpy as np

from .sim_time_loc import SimulationOfTimeLocation


@dataclass
class DeviceSettingsConf:
    """Device settings configuration."""

    #: dict[str, list[str]]: list of all options for each device setting.
    #:  (Setting Name -> List of Options)
    options: dict[str, list[str]]

    #: dict[str, dict[str, float]]: power multiplier for each option for
    #:  each device setting.
    #:  (Setting Name -> (Option Name -> Power Multiplier))
    power_factors: dict[str, dict[str, float]]

    def __post_init__(self):
        for setting, options in self.power_factors.items():
            for option, multiplier in options.items():
                assert option in self.options.get(setting)
                assert multiplier > 0


@dataclass
class ADSRParams:
    """ADSR (Attack, Decay, Sustain, and Release) model parameters."""
    a: float  #: float: Attack Time [sec].
    d: float  #: float: Decay Time [sec].
    s: float  #: float: Sustain Level Multiplier.
    r: float  #: float: Release Time [sec].
    #: str: Wave Type ["none" | "sine" | "square" | "random"].
    wt: str = "none"
    wp: float = 1  #: float: Wave Period [sec].
    wa: float = 0  #: float: Wave Amplitude Multiplier.

    def __post_init__(self):
        assert self.a > 0
        assert self.d > 0
        assert 1 >= self.s >= 0
        assert self.r > 0
        assert self.wt in ["none", "sine", "square", "random"]
        assert self.wp > 0
        assert 1 >= self.wa >= 0


@dataclass
class DeviceInfo:
    """Device information.

    """
    max_watt: float  #: float: Maximum wattage that device can reach (maximum amplitude).
    max_count: int  #: int: Device maximum count a regular house could have.
    adsr_model: ADSRParams  #: ADSRParams: Device ADSR parmeters.
    settings: DeviceSettingsConf = None  #: DeviceSettings: Device settings.

    def __post_init__(self):
        pass


class Device(Enum):
    """Some important regular house devices static info."""

    TEST_DEVICE = DeviceInfo(
        max_watt=1000,
        max_count=10,
        adsr_model=ADSRParams(
            a=360, d=200, s=.8, r=10,
            wt="random", wp=1, wa=.050,
        ),
    )

    LED_LIGHT = DeviceInfo(
        max_watt=10,
        max_count=20,
        adsr_model=ADSRParams(
            a=.01, d=2, s=.8, r=.01,
        ),
    )

    TV = DeviceInfo(
        max_watt=120,
        max_count=4,
        adsr_model=ADSRParams(
            a=1, d=1, s=.8, r=1.5,
            wt="sine", wp=.5, wa=.1,
        ),
    )

    REFRIGERATOR = DeviceInfo(
        max_watt=150,
        max_count=2,
        adsr_model=ADSRParams(
            a=1, d=1, s=.3, r=2,
            wt="square", wp=3, wa=.06,
        ),
    )

    HVAC = DeviceInfo(
        max_watt=3500,
        max_count=1,
        adsr_model=ADSRParams(
            a=3, d=2, s=.8, r=.5,
            wt="sine", wp=2, wa=.07,
        ),
    )

    WASHING_MACHINE = DeviceInfo(
        max_watt=500,
        max_count=1,
        adsr_model=ADSRParams(
            a=2, d=2, s=.7, r=.5,
            wt="sine", wp=.5, wa=.04,
        ),
        settings=DeviceSettingsConf(
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

    DRYER = DeviceInfo(
        max_watt=3000,
        max_count=1,
        adsr_model=ADSRParams(
            a=2, d=1, s=.9, r=2,
            wt="sine", wp=2, wa=.03,
        ),
        settings=DeviceSettingsConf(
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

    DISHWASHER = DeviceInfo(
        max_watt=1800,
        max_count=1,
        adsr_model=ADSRParams(
            a=3, d=1.5, s=.6, r=2,
            wt="sine", wp=1, wa=.05,
        ),
        settings=DeviceSettingsConf(
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

    WATER_HEATER = DeviceInfo(
        max_watt=4500,
        max_count=1,
        adsr_model=ADSRParams(
            a=1, d=.5, s=.9, r=1,
            wt="square", wp=5, wa=.1,
        ),
    )

    MICROWAVE = DeviceInfo(
        max_watt=1100,
        max_count=1,
        adsr_model=ADSRParams(
            a=.5, d=.2, s=1, r=.5,
        ),
    )

    @property
    def name_formated(self) -> str:
        """str: The formated device name."""
        return self.name.replace('_', ' ').title()


class DeviceState:
    """Hold **a device** status for **a house**.

    Args:
        device (Device): Device static info.

    """

    device_name: str  #: str: Device name.
    device_info: DeviceInfo  #: DeviceInfo: Device static info.
    count: int = 0  #: int: Number of **active** device instances.
    total_load: float = .0  #: float: Total load for all device instances.

    #: list[tuple[float, float, bool]]: Active Envelopes, each tuple
    #:  represent an envelope, and it contains three elements:
    #:  - float: time elapsed at last state toggle for the envelope;
    #:  - float: time total load at last state toggle for the envelope;
    #:  - bool: envelope state toggle.
    active_envelopes: list[tuple[float, float, bool]] = []

    #: dict[str, str]: Current settings for all instances.
    current_settings: dict[str, str] = {}

    #: float: Setting multiplier for current settings.
    settings_multiplier: float = 1

    def __init__(self, device: Device):
        self.device_name = device.name_formated
        self.device_info = device.value

        # Initialize current settings for each option if appliance settings exist
        if self.device_info.settings:
            for setting, options in self.device_info.settings.options.items():
                # Default to first option
                self.current_settings[setting] = options[0]

    def update_count(self, elapsed: float, value: str):
        """Update device instances count and edit envelopes indead.

        Args:
            elapsed (float): Current elapsed time [sec].
            value (int): The new count.

        """
        new_count = int(float(value)) if value.strip() else 0

        if new_count > self.count:
            for _ in range(new_count - self.count):
                self.active_envelopes.append((elapsed, self.total_load, True))

        elif new_count < self.count:
            excess = self.count - new_count
            for idx, (_, _, is_active) in enumerate(self.active_envelopes):
                if is_active and excess > 0:
                    self.active_envelopes[idx] = (
                        elapsed, self.total_load, False)
                    excess -= 1

        self.count = new_count

    def update_setting(self, setting_name: str, value: str):
        """Update a specific setting for the device.

        Notice that it will applies for all instances.

        Args:
            setting_name (str): Updated setting name.
            value (str): The new setting option.

        """
        if self.device_info.settings and setting_name in self.device_info.settings.options:
            self.current_settings[setting_name] = value

            self.settings_multiplier = np.prod(np.array([
                self.device_info.settings.power_factors[setting].get(option, 1)
                for setting, option in self.current_settings.items()
                if setting in self.device_info.settings.power_factors
            ]))

    def _filter_active_envelopes(self, elapsed: float):
        """Filter the active envelopes from IDEL envelopes.

        IDEL envelopes are envelopes which where unactive for
        longer than release time.

        Args:
            elapsed (float): The elapsed time [sec].

        """
        def not_idel(envelope) -> bool:
            return self._calc_adsr_multiplier(elapsed, envelope) > 0

        self.active_envelopes = list(filter(not_idel, self.active_envelopes))

    def _calc_wave_multiplier(self, elapsed: float) -> float:
        """Calculate the power multiplier based on Wave parameters.

        Args:
            elapsed (float): The elapsed time [sec].

        Returns:
            float: The wave power multiplier.

        """
        wp = self.device_info.adsr_model.wp
        wa = self.device_info.adsr_model.wa
        wt = self.device_info.adsr_model.wt

        match wt:
            case "none":
                return 1.0
            case "sine":
                phase = (elapsed % wp) / wp
                return 1.0 + wa * np.sin(2 * np.pi * phase)
            case "square":
                phase = (elapsed % wp) / wp
                return 1.0 + (wa if phase < 0.5 else -wa)
            case "random":
                return 1.0 + (wa * random.uniform(-1, 1))

    def _calc_adsr_multiplier(self, elapsed: float, envelope: tuple[float, float, bool]):
        """
        Calculate the power multiplier based on ADSR parameters for certain envelope.

        Args:
            elapsed (float): The elapsed time [sec].
            envelope (tuple[float, float, bool]): The envelope (instance
                of device) info.

        Returns:
            float: The wave power multiplier.

        """
        a = self.device_info.adsr_model.a
        s = self.device_info.adsr_model.s
        d = self.device_info.adsr_model.d
        r = self.device_info.adsr_model.r

        state_toggle_time, state_toggle_load, is_active = envelope

        # Current Time (start from last state toggle)
        t = elapsed - state_toggle_time

        # Level when Last State Toggle
        llst = state_toggle_load / self.device_info.max_watt

        if is_active:
            if t <= a:
                # Attack Stage (line between (0, 0) and (a, 1))
                return (1 / a) * t + (0)
            if t <= (a + d):
                # Decay Stage (line between (a, 1) and (a+d, s))
                return ((s - 1) / d) * t + (1 - a * (s - 1) / d)

            # Sustain Stage
            return s

        if t <= r * (llst / s):
            # Release Stage (line from (0, llst) with slope same as line between (0, s) and (r, 0))
            return (- s / r) * t + (llst)

        # IDEL Stage
        return 0.0

    def _calc_device_load(self, elapsed: float) -> float:
        """Calculate and update device load at this ``elapsed``.

        It's calculated depending on it's base wattage, settings, wave
        parameters, and adsr parameters.

        Args:
            elapsed (float): The elapsed time [sec].

        """
        self.total_load = np.sum(
            self.device_info.max_watt *
            self.settings_multiplier *
            self._calc_wave_multiplier(elapsed) *
            np.array([self._calc_adsr_multiplier(elapsed, ae)
                     for ae in self.active_envelopes])
        )

        return self.total_load


class SimulationOfHousesLoads:
    """Simulation for the houses loads.

    Args:
        stl (SimulationOfTimeLocation): The :class:`SimulationOfTimeLocation` object.
        pv_conf (PVConf): The :class:`PVConf` for the system.
        log (bool): If True, an csv file will be created and record the system status.

    """

    num_houses: int  #: int: Number of houses in the system.
    running: bool = False   #: Whether the simulation is running or paused.
    system_load: float = .0  #: float: The current system total load.
    houses_loads: list[float]  #: list[float]: Total load for each house.
    #: list[dict[str, DeviceInfo]]: Device state for each device for each house.
    houses_devices_states: list[dict[str, DeviceState]]

    def __init__(self, stl: SimulationOfTimeLocation, num_houses: int, log=False):
        self._stl = stl
        self.num_houses: int = num_houses

        self.houses_loads = [0 for _ in range(self.num_houses)]
        self.houses_devices_states = [
            {
                device.name_formated: DeviceState(device)
                for device in Device
            }
            for _ in range(self.num_houses)
        ]

        self._log = log
        if self._log:
            timestamp = self._stl.get_time().strftime("%Y-%m-%d_%H-%M-%S")
            self._log_file_name = f"log_shl_{timestamp}.csv"

    def start(self):
        """Start the simulation."""
        self.running = True

        if self._log:
            if (not os.path.exists("logs")):
                os.mkdir("logs")

            if (not os.path.exists("logs/sim_houses_loads")):
                os.mkdir("logs/sim_houses_loads")

            with open(f"logs/sim_houses_loads/{self._log_file_name}", mode="w", encoding="utf-8") as log_file:
                columns_line = "elapsed,system_load\n"
                log_file.write(columns_line)
                log_file.close()

        threading.Thread(
            target=self._update,
            kwargs={'dt': 100},
            daemon=True
        ).start()

    def pause(self):
        """Pause the simulation."""
        if self.running:
            self.running = False

    def resume(self):
        """Resume the simulation."""
        if not self.running:
            self.start()

    def _update(self, dt: int):
        """Update the simulation every ``dt`` milliseconds.

        Args:
            dt (int): The number of milliseconds to update.

        """
        while self.running:
            curr_elapsed = self._stl.get_elapsed()

            for idx in range(self.num_houses):
                house_load = 0.0
                for device_name in self.houses_devices_states[idx].keys():
                    self.houses_devices_states[idx][device_name]._filter_active_envelopes(
                        curr_elapsed)
                    device_load = self.houses_devices_states[idx][device_name]._calc_device_load(
                        curr_elapsed)
                    house_load += device_load

                self.houses_loads[idx] = house_load

            self.system_load = sum(self.houses_loads)

            if self._log:
                with open(f"logs/sim_houses_loads/{self._log_file_name}", mode="a", encoding="utf-8") as log_file:
                    record = f"{curr_elapsed:.2f},{self.system_load:.2f}\n"
                    log_file.write(record)
                    log_file.close()

            time.sleep(dt/1000)
