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
base_time = nsrdb_start_point + timedelta(days=2, hours=10)  # Start at 10 AM for good solar
time_sim._start_point = base_time

data = {
    'timestamp': [],
    'export_power_total': [],
    'house_1_weight': [],
    'house_2_weight': [],
    'house_3_weight': [],
    'house_1_export_weight': [],
    'house_2_export_weight': [],
    'house_3_export_weight': [],
    'house_1_export_power': [],
    'house_2_export_power': [],
    'house_3_export_power': [],
    'house_1_utility_line': [],
    'house_2_utility_line': [],
    'house_3_utility_line': [],
    'solar_power': [],
    'system_load': [],
}

simulation_hours = 8  # Focus on daylight hours when export is likely
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
    
    # Calculate export distribution
    solar_power = solar_sim.panels.total_power
    system_load = sum(house.load_power for house in houses_sim.houses)
    export_power = max(0, solar_power - system_load)  # Only when generation > load
    
    # Get virtual battery weights
    vb_weights = [vb.weight for vb in power_mng.virtual_batteries]
    
    # Calculate export weights (inverse of VB weights for eligible houses)
    utility_lines = [house.utility_line for house in houses_sim.houses]
    eligible_houses = [i for i, ul in enumerate(utility_lines) if ul]
    
    export_weights = [0, 0, 0]  # Initialize for all houses
    export_powers = [0, 0, 0]
    
    if export_power > 10 and eligible_houses:  # Only if significant export and eligible houses
        # Calculate inverse weights for eligible houses only
        eligible_inverse_weights = [1.0 / vb_weights[i] for i in eligible_houses]
        total_inverse_weight = sum(eligible_inverse_weights)
        
        # Normalize and distribute export power
        for idx, house_idx in enumerate(eligible_houses):
            normalized_weight = eligible_inverse_weights[idx] / total_inverse_weight
            export_weights[house_idx] = normalized_weight
            export_powers[house_idx] = export_power * normalized_weight
    
    # Collect data
    data['timestamp'].append(current_timestamp)
    data['export_power_total'].append(export_power)
    data['house_1_weight'].append(vb_weights[0])
    data['house_2_weight'].append(vb_weights[1])
    data['house_3_weight'].append(vb_weights[2])
    data['house_1_export_weight'].append(export_weights[0])
    data['house_2_export_weight'].append(export_weights[1])
    data['house_3_export_weight'].append(export_weights[2])
    data['house_1_export_power'].append(export_powers[0])
    data['house_2_export_power'].append(export_powers[1])
    data['house_3_export_power'].append(export_powers[2])
    data['house_1_utility_line'].append(int(utility_lines[0]))
    data['house_2_utility_line'].append(int(utility_lines[1]))
    data['house_3_utility_line'].append(int(utility_lines[2]))
    data['solar_power'].append(solar_power)
    data['system_load'].append(system_load)

df = pd.DataFrame(data)

fig, axes = plt.subplots(3, 1, figsize=(10, 12))
fig.suptitle('Utility Export Distribution Fairness: Inverse Weight Incentives', fontsize=14, fontweight='bold')

# Plot 1: Virtual battery weights vs export weights (inverse relationship)
ax1 = axes[0]
ax1.plot(df['timestamp'], df['house_1_weight'], 'r-', linewidth=2, label='House 1 VB Weight')
ax1.plot(df['timestamp'], df['house_2_weight'], 'g-', linewidth=2, label='House 2 VB Weight')
ax1.plot(df['timestamp'], df['house_3_weight'], 'b-', linewidth=2, label='House 3 VB Weight')

# Add inverse relationship on secondary axis
ax1_twin = ax1.twinx()
ax1_twin.plot(df['timestamp'], df['house_1_export_weight'], 'r:', linewidth=2, alpha=0.7, label='House 1 Export Weight')
ax1_twin.plot(df['timestamp'], df['house_2_export_weight'], 'g:', linewidth=2, alpha=0.7, label='House 2 Export Weight')
ax1_twin.plot(df['timestamp'], df['house_3_export_weight'], 'b:', linewidth=2, alpha=0.7, label='House 3 Export Weight')

ax1.set_title('Virtual Battery Weights vs Export Weights (Inverse Relationship)', fontsize=12, fontweight='bold')
ax1.set_ylabel('VB Weight Factor', color='black')
ax1_twin.set_ylabel('Export Weight (Normalized)', color='gray')
ax1.tick_params(axis='y', labelcolor='black')
ax1_twin.tick_params(axis='y', labelcolor='gray')

# Combine legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax1_twin.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=9)

ax1.grid(True, alpha=0.3)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

# Plot 2: Export power distribution
ax2 = axes[1]
ax2.stackplot(df['timestamp'], 
             df['house_1_export_power'], df['house_2_export_power'], df['house_3_export_power'],
             labels=['House 1 Export', 'House 2 Export', 'House 3 Export'],
             colors=['red', 'green', 'blue'], alpha=0.7)

ax2.plot(df['timestamp'], df['export_power_total'], 'k-', linewidth=2, label='Total Export Power')

ax2.set_title('Export Power Distribution Among Houses', fontsize=12, fontweight='bold')
ax2.set_ylabel('Export Power [W]')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

# Plot 3: Economic incentive demonstration
ax3 = axes[2]

# Calculate cumulative export benefits (simplified as energy * time)
cumulative_export = np.zeros(3)
for i in range(len(df)):
    dt_hours_actual = dt_hours
    cumulative_export[0] += df.iloc[i]['house_1_export_power'] * dt_hours_actual / 1000  # kWh
    cumulative_export[1] += df.iloc[i]['house_2_export_power'] * dt_hours_actual / 1000
    cumulative_export[2] += df.iloc[i]['house_3_export_power'] * dt_hours_actual / 1000

# Bar chart showing final weights vs cumulative export benefits
houses = ['House 1', 'House 2', 'House 3']
final_weights = [df['house_1_weight'].iloc[-1], df['house_2_weight'].iloc[-1], df['house_3_weight'].iloc[-1]]
colors = ['red', 'green', 'blue']

x_pos = np.arange(len(houses))
width = 0.35

bars1 = ax3.bar(x_pos - width/2, final_weights, width, label='VB Weight (Final)', color=colors, alpha=0.6)
bars2 = ax3.bar(x_pos + width/2, cumulative_export, width, label='Export Benefits [kWh]', color=colors, alpha=0.9)

# Add value labels on bars
for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
    ax3.text(bar1.get_x() + bar1.get_width()/2, bar1.get_height() + 0.02,
             f'{final_weights[i]:.2f}', ha='center', va='bottom', fontsize=10)
    ax3.text(bar2.get_x() + bar2.get_width()/2, bar2.get_height() + 0.02,
             f'{cumulative_export[i]:.2f}', ha='center', va='bottom', fontsize=10)

ax3.set_title('Economic Incentive: Lower VB Weight = Higher Export Benefits', fontsize=12, fontweight='bold')
ax3.set_ylabel('Value')
ax3.set_xticks(x_pos)
ax3.set_xticklabels(houses)
ax3.legend()
ax3.grid(True, alpha=0.3, axis='y')

# Add explanatory text
ax3.text(0.5, -0.25, 
         'Houses with lower VB weights (more efficient usage) receive higher export allocation,\n' +
         'creating economic incentives for optimal energy consumption behavior.',
         ha='center', va='top', transform=ax3.transAxes, fontsize=10, style='italic',
         bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.5))

# Format x-axis for all subplots except the bar chart
for ax in [ax1, ax2]:
    ax.tick_params(axis='x', rotation=45)
    plt.setp(ax.xaxis.get_majorticklabels(), ha='right')

plt.tight_layout(pad=2)
plt.subplots_adjust(bottom=0.15)
plt.show()