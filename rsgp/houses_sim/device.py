"""Houses simulation device class."""

import random

from .data import DeviceConf, RegularDevices

from Pyro5.api import expose
import numpy as np


@expose
class DeviceClass:
    """Device class."""

    name: str  #: str: Device class name.
    conf: DeviceConf  #: DeviceConf: Device class static configuration.
    load: float  #: float: Total load for all device instances.

    def __init__(self, device_name: str) -> None:
        self.name = RegularDevices[device_name].name
        self.conf = RegularDevices[device_name].value
        self.load = 0.0

        self._envelopes = [
            (0.0, 0.0, False)
            for _ in range(self.conf.max_count)
        ]

    def get_name(self) -> str:
        """Get device name.

        Returns:
            str: Device name.

        """
        return str(self.name)

    def get_conf_summary(self) -> str:
        """Get device class configuration summary.

        Returns:
            str: Device class configuration summary.

        """
        return str(self.conf)

    def get_conf_base_watt(self) -> float:
        """Get device class base wattage.

        Returns:
            float: Device class base wattage.

        """
        return float(self.conf.base_watt)

    def get_conf_max_count(self) -> int:
        """Get maximum count for the device class.

        Returns:
            int: Maximum count for the device class.

        """
        return int(self.conf.max_count)

    def get_load(self) -> float:
        """Get total load for the device class.

        Returns:
            float: Total load for the device class.

        """
        return float(self.load)

    def get_envelopes(self) -> list[tuple[float, float, bool]]:
        """Get device class envelopes.

        Returns:
            list[tuple[float, float, bool]]: Device class envelopes.

        """
        return [
            (float(envelope[0]), float(envelope[1]), bool(envelope[2]))
            for envelope in self._envelopes
        ]

    def set_envelopes(self, envelopes: list[tuple[float, float, bool]]) -> None:
        """Set device class envelopes.

        Args:
            envelopes (list[tuple[float, float, bool]]): Device class envelopes.

        """
        self._envelopes = envelopes

    def toggle_envelope_state(self, idx: int, elapsed: float) -> None:
        """Toggle the state of a specific device instance envelope.

        Args:
            idx (int): Index of the device instance envelope to toggle.
            elapsed (float): Current elapsed time in the simulation.        

        """
        prev_state = self._envelopes[idx][2]
        self._envelopes[idx] = (elapsed, self.load, not prev_state)

    def calc_load(self, elapsed: float) -> float:
        """Calculate the total load for the device class based on the ADSR envelope and wave type.

        Args:
            elapsed (float): Current elapsed time in the simulation.

        Returns:
            float: Total load for the device class.

        """
        not_idle_envelopes = self.filter_idle_envelopes(elapsed)

        self.load = np.sum(
            self.conf.base_watt * self.calc_wave_multiplier(elapsed) *
            np.array([self.calc_adsr_multiplier(elapsed, e) for e in not_idle_envelopes])
        )

        return self.load

    def filter_idle_envelopes(self, elapsed: float) -> list[tuple[float, float, bool]]:
        """Filter out idle envelopes.

        Args:
            elapsed (float): Current elapsed time in the simulation.

        Returns:
            list[tuple[float, float, bool]]: List of non-idle envelopes.

        """
        not_idle_envelopes = list(filter(
            lambda envelope: (self.calc_adsr_multiplier(elapsed, envelope) > 0),
            self._envelopes
        ))

        return not_idle_envelopes

    def calc_wave_multiplier(self, elapsed: float) -> float:
        """Calculate the wave multiplier based on the wave type and elapsed time.

        Args:
            elapsed (float): Current elapsed time in the simulation.

        Returns:
            float: Wave multiplier.

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
        """Calculate the ADSR (Attack-Decay-Sustain-Release) multiplier.

        Args:
            elapsed (float): Current elapsed time in the simulation.
            envelope (tuple[float, float, bool]): A tuple containing the state toggle time, the
                load at the state toggle, and the active status of the envelope.

        Returns:
            float: ADSR multiplier.

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
        return 0.0

    def __str__(self) -> str:
        return f"DeviceClass(name='{self.name}', load={self.load:.2f})"
