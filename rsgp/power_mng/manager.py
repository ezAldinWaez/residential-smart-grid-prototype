"""Power manager."""

# TODO: Document this module.

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
    from ..houses_loads_sim.simulator import HousesLoadsSimulator
    from ..solar_system_sim.simulator import SolarSystemSimulator


@expose
class PowerManager:
    def __init__(self, houses_loads_sim: HousesLoadsSimulator, solar_system_sim: SolarSystemSimulator):
        self._houses_loads_sim = houses_loads_sim
        self._solar_system_sim = solar_system_sim
        self._running = False

        self.static_factor = 1 / self._houses_loads_sim.num_houses

        self.virtual_batteries = [
            VirtualBattery(
                idx=idx,
                capacity=self._solar_system_sim.inverter._battery.conf.capacity * self.static_factor,
                init_charge_level=self._solar_system_sim.inverter._battery.charge_level * self.static_factor
            ) for idx in range(self._houses_loads_sim.num_houses)
        ]

        self.switch(False)
        self._solar_system_sim.post_inverter_operate_hook = lambda: self.switch(True)

    def switch(self, state: bool) -> None:
        self.switched = state

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
        while not self.switched:
            continue

        elapsed = time_sim.get_elapsed()
        timestamp = time_sim.get_timestamp(elapsed)

        loads = [house.load for house in self._houses_loads_sim.houses]
        solar_power = self._solar_system_sim.inverter.cycle_used_solar
        battery_exchange = self._solar_system_sim.inverter.cycle_battery_exchange
        utility_power = self._solar_system_sim.inverter.utility_interface.exchange_power_ac

        # Using 0.0001 instead of 0 because a float number may reach 5.0e-12 and not 0; we thus use epsilon.
        while solar_power > 0.0001 and sum(loads) > 0.0001:
            for idx in range(len(loads)):
                new_load = max(loads[idx] - solar_power * self.static_factor, 0.0)
                solar_power -= loads[idx] - new_load
                loads[idx] = new_load

        while utility_power > 0.0001 and sum(loads) > 0.0001:
            for idx in range(len(loads)):
                new_load = max(loads[idx] - utility_power * self.static_factor, 0.0)
                utility_power -= loads[idx] - new_load
                loads[idx] = new_load

        while battery_exchange < 0.0001 and sum(loads) > 0.0001:
            for idx in range(len(loads)):
                taken_power = self.virtual_batteries[idx].discharge(-1 * battery_exchange * self.static_factor)
                if taken_power < 0.0001:
                    if loads[idx] > 0.0001:
                        self._houses_loads_sim.get_house(idx).set_load_line(False)
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
                battery_exchange -= self.virtual_batteries[idx].charge(battery_exchange * self.static_factor)

        # Set inverter utility line connection status
        is_any_utility_on = False
        list_of_utility_lines_state = [house.utility_line for house in self._houses_loads_sim.houses]
        for utility in list_of_utility_lines_state:
            if utility:
                is_any_utility_on = True
                break
        self._solar_system_sim.inverter.utility_interface.set_connection_status(is_any_utility_on)

        self._solar_system_sim.inverter.load_interface.set_system_load(self._houses_loads_sim.get_system_load())

        if settings.CSV_LOGGING:
            log_record_into_csv(
                settings.CSV_PM_LOG_PATH,
                timestamp=f"{timestamp}",
            )

        self.switch(False)

    def summary(self) -> str:
        return str((
            f"Power Manager Status: ..."
        ))
