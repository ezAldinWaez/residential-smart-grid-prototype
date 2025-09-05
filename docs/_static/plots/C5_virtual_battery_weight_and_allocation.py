from rsgp.houses_sim.simulator import HousesSimulator
from rsgp.solar_system_sim.simulator import SolarSystemSimulator
from rsgp.power_mng.manager import PowerManager
from rsgp.config.settings import settings
from rsgp.utils.nsrdb_data import nsrdb_start_point
from rsgp.utils.time_sim import time_sim
from docs._static.plots.scenario_events import SCENARIO_EVENTS

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import pandas as pd
from datetime import timedelta

houses_sim = HousesSimulator()
solar_sim = SolarSystemSimulator()
power_mng = PowerManager(houses_sim, solar_sim)
base_time = nsrdb_start_point + timedelta(days=2, hours=12)
time_sim._start_point = base_time

data = {
    'timestamp': [],
    'house_1_weight': [],
    'house_2_weight': [],
    'house_3_weight': [],
    'house_1_capacity': [],
    'house_2_capacity': [],
    'house_3_capacity': [],
    'physical_battery_capacity': [],
    'house_1_load': [],
    'house_2_load': [],
    'house_3_load': [],
}

simulation_hours = 24
steps_per_hour = 10
total_steps = simulation_hours * steps_per_hour
dt_hours = 1.0 / steps_per_hour  # 6 minutes
dt_seconds = dt_hours * 3600

houses_sim._dt = (dt_seconds / settings.TIME_FACTOR) * 1000
solar_sim._dt = (dt_seconds / settings.TIME_FACTOR) * 1000
power_mng._dt = (dt_seconds / settings.TIME_FACTOR) * 1000

for step in range(total_steps):
    current_time_hours = step * dt_hours
    current_time_seconds = current_time_hours * 3600
    current_timestamp = base_time + timedelta(hours=current_time_hours)

    for event_time, event_callback in SCENARIO_EVENTS:
        if abs(current_time_hours - event_time) < dt_hours / 2:
            event_callback(houses_sim)

    houses_sim._update_step(current_time_seconds)
    solar_sim._update_step(current_time_seconds)
    power_mng._update_step(current_time_seconds)

    data['timestamp'].append(current_timestamp)
    data['house_1_weight'].append(power_mng.virtual_batteries[0].weight)
    data['house_2_weight'].append(power_mng.virtual_batteries[1].weight)
    data['house_3_weight'].append(power_mng.virtual_batteries[2].weight)
    data['house_1_capacity'].append(power_mng.virtual_batteries[0].total_capacity)
    data['house_2_capacity'].append(power_mng.virtual_batteries[1].total_capacity)
    data['house_3_capacity'].append(power_mng.virtual_batteries[2].total_capacity)
    data['physical_battery_capacity'].append(solar_sim.battery.conf.total_capacity)
    data['house_1_load'].append(houses_sim.houses[0].load_power)
    data['house_2_load'].append(houses_sim.houses[1].load_power)
    data['house_3_load'].append(houses_sim.houses[2].load_power)

df = pd.DataFrame(data)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
fig.suptitle('Virtual Battery Weight Evolution and Capacity Allocation', fontsize=14, fontweight='bold')

# Plot 1: Weight evolution over time
ax1.plot(df['timestamp'], df['house_1_weight'], 'r-', linewidth=2.5, label='House 1 Weight')
ax1.plot(df['timestamp'], df['house_2_weight'], 'g-', linewidth=2.5, label='House 2 Weight')
ax1.plot(df['timestamp'], df['house_3_weight'], 'b-', linewidth=2.5, label='House 3 Weight')

# Add reference lines for weight boundaries
initial_weight = 1.0
min_weight = 0.8
max_weight = 1.4  # For 3 houses: 1 + (1 - 0.8) * (3 - 1)
ax1.axhline(y=initial_weight, color='black', linestyle='--', alpha=0.5, label='Initial Weight (1.0)')
ax1.axhline(y=min_weight, color='orange', linestyle=':', alpha=0.7, label=f'Min Weight ({min_weight})')
ax1.axhline(y=max_weight, color='red', linestyle=':', alpha=0.7, label=f'Max Weight ({max_weight})')

ax1.set_title('Adaptive Weight Learning Over Time', fontsize=12, fontweight='bold')
ax1.set_ylabel('Weight Factor')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax1.set_ylim(min_weight - 0.05, max_weight + 0.05)

# Plot 2: Virtual battery capacity allocation
h1_fill = ax2.fill_between(df['timestamp'], 0, df['house_1_capacity'] / 1000, alpha=0.4, color='red', label='House 1 Capacity')
h2_fill = ax2.fill_between(df['timestamp'], df['house_1_capacity'] / 1000, (df['house_1_capacity'] + df['house_2_capacity']) / 1000, alpha=0.4, color='green', label='House 2 Capacity')
h3_fill = ax2.fill_between(df['timestamp'], (df['house_1_capacity'] + df['house_2_capacity']) / 1000,
                 (df['house_1_capacity'] + df['house_2_capacity'] + df['house_3_capacity']) / 1000,
                 alpha=0.4, color='blue', label='House 3 Capacity')

ax2.set_title('Virtual Battery Capacity Allocation', fontsize=12, fontweight='bold')
ax2.set_ylabel('Capacity [kWh]')
ax2.legend(handles=[h1_fill, h2_fill, h3_fill])
ax2.grid(True, alpha=0.3)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

for ax in [ax1, ax2]:
    ax.tick_params(axis='x', rotation=45)
    plt.setp(ax.xaxis.get_majorticklabels(), ha='right')

plt.tight_layout(pad=2)
plt.show()
