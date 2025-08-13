from __future__ import annotations
from typing import TYPE_CHECKING
from threading import Thread
import time

from .virtual_battery import VirtualBattery
from ..remote_object import expose
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

        self.virtual_batteries = [
            VirtualBattery(
                idx=idx,
                capacity=self._solar_sim.inverter._battery.conf.capacity * self.static_factor,
                init_charge_level=self._solar_sim.inverter._battery.charge_level * self.static_factor
            ) for idx in range(self._houses_sim.get_num_houses())
        ]

    def is_running(self) -> bool:
        return self._running

    def start(self, dt: int = None) -> None:
        self._running = True
        self._dt = dt

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

        loads = [house.load_power for house in self._houses_sim.houses]
        solar_power = self._solar_sim.inverter.panels_power
        battery_exchange = self._solar_sim.inverter.battery_exchange_power
        utility_power = self._solar_sim.inverter.utility_exchange_power

        # Adjust the weights
        loads_copy = [load for load in loads]
        avg_load = sum(loads) / len(loads)
        baselined_loads = [load - avg_load for load in loads]
        for idx in range(len(baselined_loads)):
            if self.virtual_batteries[idx].weight == 1.0 + (1.0 - settings.MINIMUM_GUARANTEED_WEIGHT):
                baselined_loads[idx] = min(baselined_loads[idx], 0.0)
                if baselined_loads[idx] == 0.0: 
                    loads_copy[idx] = 0.0
            elif self.virtual_batteries[idx].weight == settings.MINIMUM_GUARANTEED_WEIGHT:
                baselined_loads[idx] = max(baselined_loads[idx], 0.0)
                if baselined_loads[idx] == 0.0:
                    loads_copy[idx] = 0.0
        new_avg_load = sum(loads_copy) / len(loads_copy)
        new_baselined_loads = [load - new_avg_load for load in loads_copy]   
        max_baselined_load = max([abs(baselined_load) for baselined_load in new_baselined_loads])
        normalized_baselined_loads = [baselined_load / max_baselined_load if max_baselined_load > 0 else 0 for baselined_load in baselined_loads]
        weight_adjustments = [normalized_load * settings.LEARNING_RATE for normalized_load in normalized_baselined_loads]
        for idx in range(len(loads)):
            self.virtual_batteries[idx].adjust_weight(weight_adjustments[idx])
        
        # Using 0.0001 instead of 0 because a float number may reach 5.0e-12 and not 0; we thus use epsilon.
        while solar_power > 0.0001 and sum(loads) > 0.0001:
            for idx in range(len(loads)):
                new_load = max(loads[idx] - solar_power * self.static_factor * self.virtual_batteries[idx].weight, 0.0)
                solar_power -= loads[idx] - new_load
                loads[idx] = new_load

        while utility_power > 0.0001 and sum(loads) > 0.0001:
            for idx in range(len(loads)):
                new_load = max(loads[idx] - utility_power * self.static_factor * self.virtual_batteries[idx].weight, 0.0)
                utility_power -= loads[idx] - new_load
                loads[idx] = new_load

        while battery_exchange < 0.0001 and sum(loads) > 0.0001:
            for idx in range(len(loads)):
                taken_power = self.virtual_batteries[idx].discharge(-1 * battery_exchange * self.static_factor * self.virtual_batteries[idx].weight)
                if taken_power < 0.0001:
                    if loads[idx] > 0.0001:
                        self._houses_sim.get_house(idx).set_load_line(False)
                        # Reduce the demand from the battery by the amount remaining from the offending load
                        battery_exchange += loads[idx]
                        loads[idx] = 0.0
                        continue
                new_load = max(loads[idx] - taken_power, 0.0)
                battery_exchange += taken_power
                loads[idx] = new_load

        while battery_exchange > 0.0001:
            if all([bat.capacity - bat.charge_level < 0.0001 for bat in self.virtual_batteries]):
                break
            for idx in range(len(loads)):
                battery_exchange -= self.virtual_batteries[idx].charge(battery_exchange * self.static_factor * self.virtual_batteries[idx].weight)

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
        return str((
            f"Power Manager Status: ..."
        ))
