"""Power manager."""

from __future__ import annotations
from typing import TYPE_CHECKING
import threading
import time

from .virtual_battery import VirtualBattery
from ..config.settings import settings
from ..utils.decorators import log_start_end_error
from ..utils.helpers import log_record_into_csv
from ..utils.remote_interface import remote_interface_expose
if TYPE_CHECKING:
    from ..time_sim.simulator import TimeSimulator
    from ..houses_loads_sim.simulator import HousesLoadsSimulator
    from ..solar_system_sim.simulator import SolarSystemSimulator


@remote_interface_expose
class PowerManager:
    def __init__(self, time_sim: TimeSimulator, houses_loads_sim: HousesLoadsSimulator, solar_system_sim: SolarSystemSimulator):
        self._time_sim = time_sim
        self._houses_loads_sim = houses_loads_sim
        self._solar_system_sim = solar_system_sim
        self._running = False
        self.static_factor = 1 / self._houses_loads_sim.get_num_houses()
        self.virtual_batteries = [VirtualBattery(self._solar_system_sim.inverter.battery.conf.capacity * self.static_factor, self._solar_system_sim.inverter.battery.charge_level * self.static_factor) for house in self._houses_loads_sim.get_houses()]
        self.switched_on = False
        self._solar_system_sim.post_inverter_work_hook = self.switch_on

    def is_running(self) -> bool:
        return self._running

    def start(self, dt: int = None) -> None:
        self._running = True
        self._dt = dt

        threading.Thread(
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

    def switch_on(self):
        self.switched_on = True
        pass

    def _update_step(self) -> None:
        if not self.switched_on:
            return
        elapsed = self._time_sim.get_elapsed()
        timestamp = self._time_sim.get_timestamp(elapsed)

        loads = [house.get_load() for house in self._houses_loads_sim.get_houses()]
        solar_power = self._solar_system_sim.inverter.cycle_used_solar
        battery_exchange = self._solar_system_sim.inverter.cycle_battery_exchange
        utility_power = self._solar_system_sim.inverter.utility.exchange_power_ac

        # Using 0.0001 instead of 0 because a float number may reach 5.0e-12 and not 0; we thus use epsilon.
        while solar_power > 0.0001 and sum(loads) > 0.0001:
            for i in range(len(loads)):
                new_load = max(loads[i] - solar_power * self.static_factor, 0.0)
                solar_power -= loads[i] - new_load
                loads[i] = new_load
        
        while utility_power > 0.0001 and sum(loads) > 0.0001:
            for i in range(len(loads)):
                new_load = max(loads[i] - utility_power * self.static_factor, 0.0)
                utility_power -= loads[i] - new_load
                loads[i] = new_load

        
        while battery_exchange < 0.0001 and sum(loads) > 0.0001:
            for i in range(len(loads)):
                taken_power = self.virtual_batteries[i].discharge(-1 * battery_exchange * self.static_factor)
                if taken_power < 0.0001:
                    if loads[i] > 0.0001: 
                        self._houses_loads_sim.get_house(i).set_load_line(False)
                        # Reduce the demand from the battery by the amount remaining from the offending load
                        battery_exchange += loads[i]
                        loads[i] = 0.0
                        continue
                new_load = max(loads[i] - taken_power, 0.0)
                battery_exchange += taken_power
                loads[i] = new_load
        
        while battery_exchange > 0.0001:
            if all([bat.capacity - bat.charge_level < 0.0001 for bat in self.virtual_batteries]): 
                break 
            for i in range(len(loads)):
                battery_exchange -= self.virtual_batteries[i].charge(battery_exchange * self.static_factor)

        # Set inverter utility line connection status
        is_any_utility_on = False
        list_of_utility_lines_state = [house.utility_line for house in self._houses_loads_sim.houses]
        for utility in list_of_utility_lines_state: 
            if utility:
                is_any_utility_on = True
                break
        self._solar_system_sim.inverter.utility.set_connection_status(is_any_utility_on)

        self._solar_system_sim.inverter.load.set_system_load(self._houses_loads_sim.get_system_load()
        )

        if settings.CSV_LOGGING:
            log_record_into_csv(
                settings.CSV_PM_LOG_PATH,
                timestamp=f"{timestamp}",
            )
        self.switched_on = False

    def summary(self) -> str:
        return str((
            f"Power Manager Status: ..."
        ))
