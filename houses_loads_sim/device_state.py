import numpy as np
import random

from .data import ApplianceSettings, ADSRParams


class DeviceState:
    def __init__(self, config: dict[str, any]):
        """
        Create device state to hold device kind info.
        
        Parameters
        ----------
        - config : Device static info (from DEVICES_CONFIG in .data module).

        """
        self.base_wattage: float = config.get("wattage")
        self.max_count: int = config.get("max_count")
        self.adsr: ADSRParams = config.get("adsr")
        self.settings: ApplianceSettings = config.get("settings", None)

        self.count = 0
        self.total_load = 0.0

        # Active Envelopes ([(state_toggle_time, state_toggle_load, active_state)])
        self.active_envelopes: list[tuple[float, float, bool]] = []

        # Initialize current settings for each option if appliance settings exist
        self.current_settings: dict[str, str] = {}
        if self.settings:
            for option_name, possible_values in self.settings.options.items():
                # Default to first option
                self.current_settings[option_name] = possible_values[0]

    def update_count_and_active_envelopes(self, elapsed, value: str):
        """
        Update device instances count and edit envelopes indead

        Parameters
        ----------
        - elapsed : Current time (seconds from last epoch).
        - value : The new count.
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

    def filter_active_envelopes(self, elapsed: float):
        """
        Filter the active envelopes from IDEL envelopes - envelopes
        which where unactive for longer than release time.

        Parameters
        ----------
        - elapsed : Current time (seconds from last epoch).
        """
        def not_idel(envelope) -> bool:
            return self.calc_adsr_multiplier(elapsed, envelope) > 0

        self.active_envelopes = list(filter(not_idel, self.active_envelopes))

    def update_setting(self, setting_name: str, value: str):
        """
        Update a specific setting for the device (for all instances).

        Parameters
        ----------
        - setting_name : Updated setting name.
        - value : The new setting option.
        """
        if self.settings and setting_name in self.settings.options:
            self.current_settings[setting_name] = value

    def calc_settings_multiplier(self) -> float:
        """
        Calculate the power multiplier based on current settings.
        """
        return np.prod(np.array([
            self.settings.power_factors[setting_name].get(current_value, 1.0)
            for setting_name, current_value in self.current_settings.items()
            if setting_name in self.settings.power_factors
        ]))

    def calc_wave_multiplier(self, elapsed: float) -> float:
        """
        Calculate the power multiplier based on Wave parameters.

        Parameters
        ----------
        - elapsed : Current time (seconds from last epoch).        
        """
        p = self.adsr.wp  # Wave Period (in sec)
        a = self.adsr.wa  # Wave Amplitude (between 0 and 1)

        match self.adsr.wt:
            case "none":
                return 1.0
            case "sine":
                phase = (elapsed % p) / p
                return 1.0 + a * np.sin(2 * np.pi * phase)
            case "square":
                phase = (elapsed % p) / p
                return 1.0 + (a if phase < 0.5 else -a)
            case "random":
                return 1.0 + (a * random.uniform(-1, 1))

    def calc_adsr_multiplier(self, elapsed: float, envelope: tuple[float, float, bool]):
        """
        Calculate the power multiplier based on ADSR parameters for certain envelope.

        Parameters
        ----------
        - elapsed : Current time (seconds from last epoch).
        - envelope : The envelope (instance of device) info.
        """
        a = self.adsr.a  # Attack Duration
        s = self.adsr.s  # Decay Duration
        d = self.adsr.d  # Sustain Level (between 0 and 1)
        r = self.adsr.r  # Release Duration

        state_toggle_time, state_toggle_load, is_active = envelope

        # Current Time (start from last state toggle)
        t = elapsed - state_toggle_time

        # Level when Last State Toggle
        llst = state_toggle_load / self.base_wattage

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

    def calc_device_load(self, elapsed: float) -> float:
        """
        Calculate and update device load at this `elapsed` depending on
        it's base wattage, it's settings, and it's wave and adsr parameters.

        Parameters
        ----------
        - elapsed : Current time (seconds from last epoch).
        """
        self.total_load = np.sum(
            self.base_wattage *
            self.calc_settings_multiplier() *
            self.calc_wave_multiplier(elapsed) *
            np.array([self.calc_adsr_multiplier(elapsed, ae)
                     for ae in self.active_envelopes])
        )

        return self.total_load
