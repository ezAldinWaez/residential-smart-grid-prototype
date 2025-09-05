from rsgp.houses_sim.simulator import HousesSimulator
from rsgp.solar_system_sim.simulator import SolarSystemSimulator
from rsgp.power_mng.manager import PowerManager
from rsgp.config.settings import settings
from rsgp.utils.nsrdb_data import nsrdb_start_point
from rsgp.utils.time_sim import time_sim
from docs._static.plots.scenario_events import SCENARIO_EVENTS

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from datetime import timedelta

houses_sim = HousesSimulator()
solar_sim = SolarSystemSimulator()
power_mng = PowerManager(houses_sim, solar_sim)
base_time = nsrdb_start_point + timedelta(days=2, hours=12)
time_sim._start_point = base_time

# Capture power distribution data at specific time points
capture_times = [2.0, 6.0, 10.0, 14.0]  # Hours: morning, noon, afternoon, evening
capture_data = []

simulation_hours = 16
steps_per_hour = 30
total_steps = simulation_hours * steps_per_hour
dt_hours = 1.0 / steps_per_hour
dt_seconds = dt_hours * 3600

houses_sim._dt = (dt_seconds / settings.TIME_FACTOR) * 1000
solar_sim._dt = (dt_seconds / settings.TIME_FACTOR) * 1000
power_mng._dt = (dt_seconds / settings.TIME_FACTOR) * 1000

for step in range(total_steps):
    current_time_hours = step * dt_hours
    current_time_seconds = current_time_hours * 3600
    current_timestamp = base_time + timedelta(hours=current_time_hours)

    # Apply scenario events
    for event_time, event_callback in SCENARIO_EVENTS:
        if abs(current_time_hours - event_time) < dt_hours / 2:
            event_callback(houses_sim)

    # Update simulations
    houses_sim._update_step(current_time_seconds)
    solar_sim._update_step(current_time_seconds)
    power_mng._update_step(current_time_seconds)

    # Capture data at specific time points
    for capture_time in capture_times:
        if abs(current_time_hours - capture_time) < dt_hours / 2:
            # Get house loads and available power
            house_loads = [house.load_power for house in houses_sim.houses]
            solar_power = solar_sim.panels.total_power
            utility_power = 8000  # Assume 8kW utility capacity

            # Simulate the power distribution algorithm
            houses_by_load = sorted(enumerate(house_loads), key=lambda x: x[1])

            power_allocation = {
                'timestamp': current_timestamp,
                'time_label': f"{int(capture_time + 8):02d}:00",
                'solar_available': solar_power,
                'utility_available': utility_power,
                'house_data': []
            }

            solar_remaining = solar_power
            utility_remaining = utility_power
            houses_remaining = len(house_loads)

            for house_idx, load in houses_by_load:
                # Solar allocation
                solar_share = solar_remaining / houses_remaining if houses_remaining > 0 else 0
                solar_used = min(load, solar_share)

                # Utility allocation
                remaining_load = load - solar_used
                utility_share = utility_remaining / houses_remaining if houses_remaining > 0 else 0
                utility_used = min(remaining_load, utility_share)

                # Virtual battery needed
                vb_needed = load - solar_used - utility_used

                power_allocation['house_data'].append({
                    'house_id': house_idx + 1,
                    'total_load': load,
                    'solar_used': solar_used,
                    'utility_used': utility_used,
                    'vb_needed': vb_needed,
                    'satisfied': abs(vb_needed) < 10  # Within 10W tolerance
                })

                # Update remaining resources
                solar_remaining -= solar_used
                utility_remaining -= utility_used
                houses_remaining -= 1

            capture_data.append(power_allocation)

# Create the waterfall plot
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Power Distribution Waterfall: Priority-Based Allocation Algorithm', fontsize=14, fontweight='bold')

colors = {'solar': 'orange', 'utility': 'gray', 'vb': 'purple', 'unmet': 'red'}
house_colors = ['red', 'green', 'blue']

for i, data in enumerate(capture_data):
    row, col = divmod(i, 2)
    ax = axes[row, col]

    houses = data['house_data']
    house_ids = [h['house_id'] for h in houses]

    # Create stacked bars for each house
    solar_used = [h['solar_used'] for h in houses]
    utility_used = [h['utility_used'] for h in houses]
    vb_needed = [max(0, h['vb_needed']) for h in houses]  # Only positive VB usage

    # Sort by house ID for consistent display
    sorted_data = sorted(zip(house_ids, solar_used, utility_used, vb_needed))
    house_ids, solar_used, utility_used, vb_needed = zip(*sorted_data)

    x_pos = np.arange(len(house_ids))

    # Create stacked bars
    p1 = ax.bar(x_pos, solar_used, color=colors['solar'], label='Solar Power', alpha=0.8)
    p2 = ax.bar(x_pos, utility_used, bottom=solar_used, color=colors['utility'], label='Utility Power', alpha=0.8)

    utility_bottom = [s + u for s, u in zip(solar_used, utility_used)]
    p3 = ax.bar(x_pos, vb_needed, bottom=utility_bottom, color=colors['vb'], label='Virtual Battery', alpha=0.8)

    # Add value labels on bars
    for j, (x, solar, utility, vb) in enumerate(zip(x_pos, solar_used, utility_used, vb_needed)):
        if solar > 50:  # Only label if significant
            ax.text(x, solar/2, f'{int(solar)}W', ha='center', va='center', fontweight='bold', fontsize=8)
        if utility > 50:
            ax.text(x, solar + utility/2, f'{int(utility)}W', ha='center', va='center', fontweight='bold', fontsize=8)
        if vb > 50:
            ax.text(x, solar + utility + vb/2, f'{int(vb)}W', ha='center', va='center', fontweight='bold', fontsize=8)

    ax.set_title(f'{data["time_label"]} - Solar: {int(data["solar_available"])}W, Utility: {int(data["utility_available"])}W',
                 fontsize=11, fontweight='bold')
    ax.set_xlabel('House ID')
    ax.set_ylabel('Power [W]')
    ax.set_xticks(x_pos)
    ax.set_xticklabels([f'House {h}' for h in house_ids])
    ax.legend(loc='upper left', fontsize=9)
    ax.grid(True, alpha=0.3)

# Add explanatory text
fig.text(0.5, 0.02,
         'Algorithm: Houses processed by ascending load order. Each house gets fair share of remaining solar/utility power.\n' +
         'Priority ensures smaller consumers access renewable energy first, preventing large loads from monopolizing resources.',
         ha='center', fontsize=10, style='italic', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.5))

plt.tight_layout(pad=2)
plt.subplots_adjust(bottom=0.15)
plt.show()
