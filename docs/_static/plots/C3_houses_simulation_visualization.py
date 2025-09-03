from rsgp.houses_sim.simulator import HousesSimulator
from rsgp.utils.nsrdb_data import nsrdb_start_point
from docs._static.plots.scenario_events import SCENARIO_EVENTS

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta

houses_sim = HousesSimulator()
base_time = nsrdb_start_point

data = {
    'timestamp': [],
    'system_load': [],
    'house_1_load_power': [],
    'house_2_load_power': [],
    'house_3_load_power': [],
    'house_1_load_line': [],
    'house_2_load_line': [],
    'house_3_load_line': [],
    'house_1_utility_power': [],
    'house_2_utility_power': [],
    'house_3_utility_power': [],
}

simulation_hours = 24
steps_per_hour = 10
total_steps = simulation_hours * steps_per_hour
dt_hours = 1.0 / steps_per_hour  # 6 minutes

for step in range(total_steps):
    current_time_hours = step * dt_hours
    current_timestamp = base_time + timedelta(hours=current_time_hours)

    for event_time, event_callback in SCENARIO_EVENTS:
        if abs(current_time_hours - event_time) < dt_hours / 2:
            event_callback(houses_sim)

    houses_sim._update_step()

    data['timestamp'].append(current_timestamp)
    data['system_load'].append(sum(house.load_power for house in houses_sim.houses))
    data['house_1_load_power'].append(houses_sim.houses[0].load_power)
    data['house_2_load_power'].append(houses_sim.houses[1].load_power)
    data['house_3_load_power'].append(houses_sim.houses[2].load_power)
    data['house_1_load_line'].append(int(houses_sim.houses[0].load_line))
    data['house_2_load_line'].append(int(houses_sim.houses[1].load_line))
    data['house_3_load_line'].append(int(houses_sim.houses[2].load_line))
    data['house_1_utility_power'].append(houses_sim.houses[0].utility_exchange_power)
    data['house_2_utility_power'].append(houses_sim.houses[1].utility_exchange_power)
    data['house_3_utility_power'].append(houses_sim.houses[2].utility_exchange_power)

df = pd.DataFrame(data)

fig, axes = plt.subplots(2, 1, figsize=(10, 6))
fig.suptitle('Houses Simulation: Real-time Device Control Scenario', fontsize=14, fontweight='bold')

# Plot 1: System load over time
ax1 = axes[0]
ax1.plot(df['timestamp'], df['system_load'], 'b-', linewidth=2, label='System Load')
ax1.fill_between(df['timestamp'], df['system_load'], alpha=0.3, color='blue')
ax1.set_title('Total System Load', fontsize=12, fontweight='bold')
ax1.set_ylabel('Power [W]')
ax1.grid(True, alpha=0.3)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

# Plot 2: Individual house loads
ax2 = axes[1]
ax2.plot(df['timestamp'], df['house_1_load_power'], 'r-', label='House 1', linewidth=2)
ax2.plot(df['timestamp'], df['house_2_load_power'], 'g-', label='House 2', linewidth=2)
ax2.plot(df['timestamp'], df['house_3_load_power'], 'b-', label='House 3', linewidth=2)
ax2.set_title('Individual House Loads', fontsize=12, fontweight='bold')
ax2.set_ylabel('Power [W]')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

# Format x-axis for all subplots
for ax in axes.flat:
    ax.tick_params(axis='x', rotation=45)
    plt.setp(ax.xaxis.get_majorticklabels(), ha='right')

plt.tight_layout(pad=2)
plt.show()
