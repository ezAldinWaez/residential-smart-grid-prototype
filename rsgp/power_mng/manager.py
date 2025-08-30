from __future__ import annotations
from typing import TYPE_CHECKING
from threading import Thread
import time

from .virtual_battery import VirtualBattery
from ..config.settings import settings
from ..utils.decorators import log_start_end_error
from ..utils.helpers import log_record_into_csv
from ..utils.time_sim import time_sim
from ..config.constants import EPSILON
if TYPE_CHECKING:
    from ..houses_sim.simulator import HousesSimulator
    from ..solar_system_sim.simulator import SolarSystemSimulator

from Pyro5.api import expose
import numpy as np


@expose
class PowerManager:
    """Power manager.

    Args:
        houses_sim (HousesSimulator): Houses simulator.
        solar_system_sim (SolarSystemSimulator): Solar system simulator.

    """

    virtual_batteries: list[VirtualBattery]  #: list[VirtualBattery]: list of virtual batteries.
    vb_static_ratio: float  #: float: Static ratio for virtual battery capacity.

    def __init__(self, houses_sim: HousesSimulator, solar_system_sim: SolarSystemSimulator) -> None:
        self._houses_sim = houses_sim
        self._solar_system_sim = solar_system_sim
        self._running = False

        self.vb_static_ratio = 1 / self._houses_sim.get_num_houses()

        self.virtual_batteries = [VirtualBattery(
            idx=idx,
            init_total_capacity=self._solar_system_sim.battery.conf.total_capacity * self.vb_static_ratio,
            init_residual_capacity=self._solar_system_sim.battery.residual_capacity * self.vb_static_ratio,
            charge_efficiency=self._solar_system_sim.battery.conf.charge_efficiency,
            min_weight=settings.GUARANTEED_MINIMUM_WEIGHT,
            max_weight=1+(1-settings.GUARANTEED_MINIMUM_WEIGHT) * self._houses_sim.get_num_houses(),
        ) for idx in range(self._houses_sim.get_num_houses())]

    def is_running(self) -> bool:
        """Check if the power manager is running.

        Returns:
            bool: True if the power manager is running, False otherwise.

        """
        return self._running

    def start(self, dt: int = None) -> None:
        """Start the power manager.

        Args:
            dt (int): Simulation time step in milliseconds.

        """
        self._running = True
        self._dt = dt

        Thread(
            target=self._update_loop,
            daemon=True
        ).start()

    def pause(self) -> None:
        """Pause the power manager."""
        if self._running:
            self._running = False

    def resume(self) -> None:
        """Resume the power manager."""
        if not self._running:
            self.start(self._dt)

    def learn_step(self, houses_load_powers: np.ndarray) -> float:
        """..."""
        # Calculate normalized baseline for houses load powers
        hlp_baselined = houses_load_powers - houses_load_powers.mean()
        hlp_baselined_max = abs(hlp_baselined).max()
        hlp_baselined_norm = hlp_baselined / hlp_baselined_max \
            if hlp_baselined_max > 0 else np.zeros_like(hlp_baselined)

        # Some useful calculations
        hlpbn_pos_indices = [
            idx for idx in range(len(hlp_baselined_norm))
            if hlp_baselined_norm[idx] > 0.0
        ]
        hlpbn_neg_indices = [
            idx for idx in range(len(hlp_baselined_norm))
            if hlp_baselined_norm[idx] < 0.0
        ]
        hlpbn_at_min_indices = [
            idx for idx in range(len(hlp_baselined_norm))
            if self.virtual_batteries[idx].weight == settings.GUARANTEED_MINIMUM_WEIGHT
        ]
        hlpbn_pos_sum = sum(hlp_baselined_norm[hlpbn_pos_indices])
        total_excess_capacity = 0.0

        if hlpbn_pos_sum == 0.0:
            return total_excess_capacity

        # Make at_min houses which loads bellow avg (negative baseline) looks like exactly avg
        # loads; and share thier diffrence from avg (thier baseline) with other above avg houses
        # (positive baseline).
        for hlpbn_neg_at_min_idx in set(hlpbn_at_min_indices) & set(hlpbn_neg_indices):
            for hlpbn_pos_idx in hlpbn_pos_indices:
                share = hlp_baselined_norm[hlpbn_neg_at_min_idx] * (hlp_baselined_norm[hlpbn_pos_idx] / hlpbn_pos_sum)
                hlp_baselined_norm[hlpbn_pos_idx] += share
            # It is logically definitive/deterministic for neg_at_min baselined norm to become 0.0 when you remove the some of shares from it.
            hlp_baselined_norm[hlpbn_neg_at_min_idx] = 0.0

        # Adjust the weights
        for hlpbn_idx, hlpbn_val in enumerate(hlp_baselined_norm):
            total_excess_capacity += self.virtual_batteries[hlpbn_idx].adjust(hlpbn_val * settings.LEARNING_STEP)

        return total_excess_capacity

    def calc_houses_vb_usage(self, houses_load_powers: np.ndarray, inverter_panels_power: float, inverter_utility_exchange_power: float) -> np.ndarray:
        """..."""
        # Calculate virtual batteries usage of each house
        houses_vb_usage = np.zeros_like(houses_load_powers)
        for idx, num_houses_remaining in zip(houses_load_powers.argsort(), range(self._houses_sim.get_num_houses(), 0, -1)):
            load_power = houses_load_powers[idx]

            used_panels_power = min(load_power, inverter_panels_power / num_houses_remaining)
            load_power -= used_panels_power

            used_utility_power = min(load_power, inverter_utility_exchange_power / num_houses_remaining)
            load_power -= used_utility_power

            inverter_panels_power -= used_panels_power
            inverter_utility_exchange_power -= used_utility_power

            self._houses_sim.get_house(idx).utility_exchange_power = used_utility_power

            houses_vb_usage[idx] = load_power

        return houses_vb_usage

    def charge_all_vb(self, charging_power: float) -> None:
        """..."""
        # Charge equally, sharing houses excesses
        for idx, num_houses_remaining in zip(np.argsort([vb.total_capacity - vb.residual_capacity for vb in self.virtual_batteries]), range(self._houses_sim.get_num_houses(), 0, -1)):
            charging_power -= self.virtual_batteries[int(idx)].charge(
                power=charging_power / num_houses_remaining,
                time_interval=(self._dt / 1000) * settings.TIME_FACTOR,
            )

    def discharge_all_vb(self, discharging_power: float, discharging_weights: np.ndarray) -> np.ndarray:
        """Discharge all virtual batteries by the given discharging power given their discharging
        weights.

        Args:
            discharging_power (float): The power to discharge with [Watt].
            discharging_weights (ndarray): The weights for each virtual battery.

        Returns:
            ndarray: A boolean array indicating whether the usage was met fully for each virtual battery.

        """
        # Discharge, each based on their usage, break load line if unable to meet it
        usage_met_fully_mask = np.zeros_like(discharging_weights, dtype=bool)
        for idx in range(len(self.virtual_batteries)):
            taken_power = self.virtual_batteries[idx].discharge(
                power=discharging_power * discharging_weights[idx],
                time_interval=(self._dt / 1000) * settings.TIME_FACTOR,
            )
            usage_met_fully_mask[idx] = discharging_power * discharging_weights[idx] - taken_power < EPSILON
        return usage_met_fully_mask

    @log_start_end_error("Starting power manager.", "Stoping power manager.")
    def _update_loop(self) -> None:
        while self._running:
            self._update_step()
            time.sleep(self._dt/1000)

    def _update_step(self) -> None:
        # If the inverter has disconnected the load line, then all houses are disconnected and nothing else to do
        if self._solar_system_sim.inverter.load_line is False:
            for house in self._houses_sim.houses:
                house.set_load_line(False)
            return

        houses_load_powers = np.array([house.load_power for house in self._houses_sim.houses])

        inverter_panels_power = self._solar_system_sim.inverter.panels_power
        inverter_battery_exchange_power = self._solar_system_sim.inverter.battery_exchange_power
        inverter_utility_exchange_power = self._solar_system_sim.inverter.utility_exchange_power

        excess_capacity = self.learn_step(houses_load_powers)

        # Charging/discharging
        if inverter_battery_exchange_power > EPSILON:
            self.charge_all_vb(inverter_battery_exchange_power + excess_capacity)
        elif inverter_battery_exchange_power < -EPSILON:
            houses_vb_usage = self.calc_houses_vb_usage(
                houses_load_powers,
                inverter_panels_power,
                inverter_utility_exchange_power
            )

            hvbu_max, hvbu_min = houses_vb_usage.max(), houses_vb_usage.min()
            hvbu_norm = (houses_vb_usage - hvbu_min) / (hvbu_max - hvbu_min) if (hvbu_max - hvbu_min) > 0 \
                else np.full_like(houses_vb_usage, self.vb_static_ratio)

            discharging_power = -inverter_battery_exchange_power
            usage_met_fully_mask = self.discharge_all_vb(discharging_power, hvbu_norm)

            for idx, usage_met_fully in enumerate(usage_met_fully_mask):
                if not usage_met_fully:
                    self._houses_sim.get_house(idx).set_load_line(False)

        # Export utility power
        if inverter_utility_exchange_power > EPSILON:
            exporting_houses = [house for house in self._houses_sim.houses if house.utility_line]
            exporting_vbs = [self.virtual_batteries[house.idx] for house in exporting_houses]
            vb_weight_sum = sum((1 / vb.weight) for vb in exporting_vbs)
            exporting_norm = [(1 / vb.weight) / vb_weight_sum for vb in exporting_vbs]
            for idx, house in enumerate(exporting_houses):
                house.utility_exchange_power = inverter_utility_exchange_power * exporting_norm[idx]

        # Set inverter stuff
        self._solar_system_sim.inverter.utility_line = any([h.utility_line for h in self._houses_sim.houses])
        self._solar_system_sim.inverter.load_power = self._houses_sim.get_system_load()

        if settings.CSV_LOGGING:
            log_record_into_csv(
                settings.CSV_PM_LOG_PATH,
                timestamp=f"{time_sim.get_timestamp()}",
                ** {f"virtual_battery_{vb.idx+1}_charge_level": f"{vb.residual_capacity:.3f}" for vb in self.virtual_batteries},
            )

    def summary(self) -> str:
        """Get a summary of the houses simulation.

        Returns:
            str: Summary of the houses simulation.

        """
        return str('\n\n'.join(f"{vb}" for vb in self.virtual_batteries))
