"""Device."""

# TODO: Document this module.

import random

from .data import DeviceConf, RegularDevices
from ..remote_object import expose

import numpy as np


@expose
class Device:
    name: str  #: str: Device name
    conf: DeviceConf  #: DeviceConf: Device static configuration
    load: float  #: float: Total load for all device instances
    #: list[tuple[float, float, bool]]: Envelopes (elapsed_time, total_load, is_active)
    envelopes: list[tuple[float, float, bool]]

    def __init__(self, device_name: str):
        self.name = RegularDevices[device_name].name
        self.conf = RegularDevices[device_name].value
        self.load = 0.0
        self.envelopes = [
            (0.0, 0.0, False)
            for _ in range(self.conf.max_count)
        ]

    def get_name(self) -> str:
        return str(self.name)

    def get_conf_summary(self) -> str:
        return str(self.conf)

    def get_conf_base_watt(self) -> float:
        return float(self.conf.base_watt)

    def get_conf_max_count(self) -> int:
        return int(self.conf.max_count)

    def get_load(self) -> float:
        return float(self.load)

    def get_envelopes(self) -> list[tuple[float, float, bool]]:
        return [
            (float(envelope[0]), float(envelope[1]), bool(envelope[2]))
            for envelope in self.envelopes
        ]

    def toggle_envelope_state(self, idx: int, elapsed: float) -> None:
        prev_state = self.envelopes[idx][2]
        self.envelopes[idx] = (elapsed, self.load, not prev_state)

    def calc_load(self, elapsed: float) -> float:
        not_idle_envelopes = self.filter_idle_envelopes(elapsed)

        self.load = np.sum(
            self.conf.base_watt * self.calc_wave_multiplier(elapsed) *
            np.array([self.calc_adsr_multiplier(elapsed, e) for e in not_idle_envelopes])
        )

        return self.load

    def filter_idle_envelopes(self, elapsed: float) -> None:
        not_idle_envelopes = list(filter(
            lambda envelope: (self.calc_adsr_multiplier(elapsed, envelope) > 0),
            self.envelopes
        ))

        return not_idle_envelopes

    def calc_wave_multiplier(self, elapsed: float) -> float:
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
