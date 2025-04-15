"""Device."""

from .data import DeviceConf, RegularDevices

import random

import numpy as np


class Device:
    """Device.

    Args:
        device_name (str): Device name.
    """
    name: str  #: str: Device name.
    conf: DeviceConf  #: DeviceConf: Device static configuration.
    load: float = .0  #: float: Total load for all device instances.
    #: list[tuple[float, float, bool]]: Envelopes, each envelope contains
    #: three elements:
    #:
    #:    1. float: time elapsed at last state toggle for the envelope;
    #:    2. float: total load at last state toggle for the envelope;
    #:    3. bool: envelope state toggle.
    envelopes: list[tuple[float, float, bool]]
    #: dict[str, str]: Current settings for all instances.
    current_settings: dict[str, str]
    #: float: Setting multiplier for current settings.
    settings_multiplier: float = 1

    def __init__(self, device_name: str):
        self.name = RegularDevices[device_name].name
        self.conf = RegularDevices[device_name].value

        self.envelopes = [
            (.0, .0, False)
            for _ in range(self.conf.max_count)
        ]

        if self.conf.settings:
            self.current_settings = {
                setting: options[0]
                for setting, options in self.conf.settings.options.items()
            }

    def toggle_envelope_state(self, idx: int, elapsed: float) -> None:
        """Toggle envelope state.

        Args:
            idx (int): The envelope index.
            elapsed (float): Current elapsed time. [sec]
        """
        prev_state = self.envelopes[idx][2]
        self.envelopes[idx] = (elapsed, self.load, not prev_state)

    def update_setting(self, setting_name: str, new_option: str) -> None:
        """Update a specific setting for the device.

        Notice that it will applies for all instances.

        Args:
            setting_name (str): Updated setting name.
            new_option (str): The new setting option.
        """
        if self.conf.settings and setting_name in self.conf.settings.options:
            self.current_settings[setting_name] = new_option

            self.settings_multiplier = np.prod(np.array([
                self.conf.settings.power_factors[setting].get(option, 1)
                for setting, option in self.current_settings.items()
                if setting in self.conf.settings.power_factors
            ]))

    def calc_load(self, elapsed: float) -> float:
        """Calculate and update device load at this `elapsed`.

        To minimize calculations, it filters idle envelopes first.

        The load is calculated depending on it's base wattage, settings,
        wave parameters, and adsr parameters.

        Args:
            elapsed (float): The elapsed time. [sec]
        """
        envelopes = self.filter_idle_envelopes(elapsed)

        self.load = np.sum(
            self.conf.base_watt *
            self.settings_multiplier *
            self.calc_wave_multiplier(elapsed) *
            np.array([self.calc_adsr_multiplier(elapsed, e)
                     for e in envelopes])
        )

        return self.load

    def filter_idle_envelopes(self, elapsed: float) -> list[tuple[float, float, bool]]:
        """Filter the active envelopes from IDLE envelopes.

        IDLE envelopes are envelopes which where unactive for
        longer than release time.

        Args:
            elapsed (float): The elapsed time. [sec]

        Returns:
            list[tuple[float, float, bool]]: The filtered envelopes list.
        """
        def not_idle(envelope) -> bool:
            return self.calc_adsr_multiplier(elapsed, envelope) > 0

        return list(filter(not_idle, self.envelopes))

    def calc_wave_multiplier(self, elapsed: float) -> float:
        """Calculate the power multiplier based on Wave parameters.

        Args:
            elapsed (float): The elapsed time. [sec]

        Returns:
            float: The wave power multiplier.
        """
        wp = self.conf.adsr.wp
        wa = self.conf.adsr.wa
        wt = self.conf.adsr.wt

        match wt:
            case "none":
                return 1
            case "sine":
                phase = (elapsed % wp) / wp
                return 1 + wa * np.sin(2 * np.pi * phase)
            case "square":
                phase = (elapsed % wp) / wp
                return 1 + (wa if phase < .5 else -wa)
            case "random":
                return 1 + (wa * random.uniform(-1, 1))

    def calc_adsr_multiplier(self, elapsed: float, envelope: tuple[float, float, bool]) -> float:
        """Calculate the power multiplier based on ADSR parameters for certain envelope.

        Args:
            elapsed (float): The elapsed time. [sec]
            envelope (tuple[float, float, bool]): The envelope (instance
                of device) info.

        Returns:
            float: The wave power multiplier.
        """
        a = self.conf.adsr.a
        s = self.conf.adsr.s
        d = self.conf.adsr.d
        r = self.conf.adsr.r

        state_toggle_time, state_toggle_load, is_active = envelope

        # Current Time (start from last state toggle)
        t = elapsed - state_toggle_time

        # Level when Last State Toggle
        llst = state_toggle_load / self.conf.base_watt

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

        # IDLE Stage
        return .0
