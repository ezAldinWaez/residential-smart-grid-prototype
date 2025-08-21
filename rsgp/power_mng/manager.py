from __future__ import annotations
from typing import TYPE_CHECKING
from threading import Thread
import time

import numpy as np

from .virtual_battery import VirtualBattery
from ..utils.remote_object import expose
from ..config.settings import settings
from ..utils.decorators import log_start_end_error
from ..utils.helpers import log_record_into_csv
from ..utils.time_sim import time_sim
if TYPE_CHECKING:
    from ..houses_sim.simulator import HousesSimulator
    from ..solar_system_sim.simulator import SolarSystemSimulator

# TODO: link utility_exchange_power between inverter and each house


@expose
class PowerManager:
    def __init__(self, houses_sim: HousesSimulator, solar_system_sim: SolarSystemSimulator):
        self._houses_sim = houses_sim
        self._solar_sim = solar_system_sim
        self._running = False

        self.static_factor = 1 / self._houses_sim.get_num_houses()

    def is_running(self) -> bool:
        return self._running

    def start(self, dt: int = None) -> None:
        self._running = True
        self._dt = dt
        self.virtual_batteries = [
            VirtualBattery(
                idx=idx,
                init_capacity=self._solar_sim.inverter._battery.conf.capacity * self.static_factor,
                init_charge_level=self._solar_sim.inverter._battery.charge_level * self.static_factor,
                charge_efficiency=self._solar_sim.inverter._battery.conf.charge_efficiency,
                time_interval=(self._dt / 1000) * settings.TIME_FACTOR,
            ) for idx in range(self._houses_sim.get_num_houses())
        ]

        Thread(
            target=self._update_loop,
            daemon=True
        ).start()

    def pause(self) -> None:
        if self._running:
            self._running = False

    def resume(self) -> None:
        if not self._running:
            self.start(self._dt)

    @log_start_end_error("Starting power manager.", "Stoping power manager.")
    def _update_loop(self) -> None:
        while self._running:
            self._update_step()
            time.sleep(self._dt/1000)

    def _update_step(self) -> None:

        elapsed = time_sim.get_elapsed()
        timestamp = time_sim.get_timestamp(elapsed)

        loads = [house.load_power if house.get_load_line else 0.0 for house in self._houses_sim.houses]
        solar_power = self._solar_sim.inverter.panels_power
        battery_exchange = self._solar_sim.inverter.battery_exchange_power
        utility_power = self._solar_sim.inverter.utility_exchange_power

        # Adjust the weights
        avg_load = sum(loads) / len(loads)
        baselined_loads = [load - avg_load for load in loads]
        max_baselined_load = max([abs(baselined_load) for baselined_load in baselined_loads])

        normalized_baselined_loads = [
            baselined_load / max_baselined_load if max_baselined_load > 0 else 0
            for baselined_load in baselined_loads
        ]

        is_at_minimum = [
            self.virtual_batteries[idx].weight == settings.GUARANTEED_MINIMUM_WEIGHT and baselined_loads[idx] < 0.0
            for idx in range(len(baselined_loads))
        ]

        for idx, at_minimum in enumerate(is_at_minimum):
            if not at_minimum:
                continue

            total_positive_adjustment = sum(
                (normalized_load if normalized_load > 0.0 else 0.0)
                for normalized_load in normalized_baselined_loads
            )

            if total_positive_adjustment == 0.0:
                break

            loss = normalized_baselined_loads[idx]
            normalized_baselined_loads[idx] = 0.0
            new_total = total_positive_adjustment + loss
            for j in range(len(normalized_baselined_loads)):
                if normalized_baselined_loads[j] > 0.0:
                    normalized_baselined_loads[j] = normalized_baselined_loads[j] * \
                        new_total / total_positive_adjustment

        for idx, normalized_load in enumerate(normalized_baselined_loads):
            self.virtual_batteries[idx].adjust_weight(normalized_load * settings.LEARNING_STEP)

        ordered_idx = [idx for idx, val in sorted(list(enumerate(loads)), key=lambda item: item[1])]

        equal_factor = 1 / (( 1/ self.static_factor) + 1)
        for idx in ordered_idx:
            equal_factor = 1 / ((1 / equal_factor) - 1)
            new_load = max(loads[idx] - solar_power * equal_factor, 0.0)
            solar_power -= loads[idx] - new_load
            loads[idx] = new_load

        equal_factor = 1 / (( 1/ self.static_factor) + 1)
        for idx in ordered_idx:
            equal_factor = 1 / ((1 / equal_factor) - 1)
            new_load = max(loads[idx] - utility_power * equal_factor, 0.0)
            utility_power -= loads[idx] - new_load
            loads[idx] = new_load
        
        min_load, max_load = min(loads), max(loads)
        factors = [(load - min_load) / (max_load - min_load) for load in loads] if (max_load - min_load) > 0 else [self.static_factor] * len(loads)

        if battery_exchange < 0.0:
            for idx in range(len(loads)):
                taken_power = self.virtual_batteries[idx].discharge(-1 * battery_exchange * factors[idx])
                if -1 * battery_exchange * factors[idx] - taken_power > 0.0001:
                    self._houses_sim.get_house(idx).set_load_line(False)
        
        ordered_idx = [idx for idx, val in sorted(list(enumerate(self.virtual_batteries)), key= lambda item: (item[1].capacity - item[1].charge_level))]
        equal_factor = 1 / (( 1/ self.static_factor) + 1)
        if battery_exchange > 0.0001:
            for idx in ordered_idx:
                equal_factor = 1 / ((1 / equal_factor) - 1)
                battery_exchange -= self.virtual_batteries[idx].charge(equal_factor * battery_exchange)

        # Set inverter utility line connection status
        is_any_utility_on = False
        list_of_utility_lines_state = [house.utility_line for house in self._houses_sim.houses]
        for utility in list_of_utility_lines_state:
            if utility:
                is_any_utility_on = True
                break
        self._solar_sim.inverter.utility_line = is_any_utility_on

        self._solar_sim.inverter.load_power = self._houses_sim.get_system_load()

        if settings.CSV_LOGGING:
            log_record_into_csv(
                settings.CSV_PM_LOG_PATH,
                timestamp=f"{timestamp}",
                ** {f"virtual_battery_{vb.idx+1}_charge_level": f"{vb.charge_level:.3f}" for vb in self.virtual_batteries},

            )

    def summary(self) -> str:
        return str('\n\n'.join(f"{vb}" for vb in self.virtual_batteries))
