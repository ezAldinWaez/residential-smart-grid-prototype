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
from datetime import timedelta

houses_sim = HousesSimulator()
solar_sim = SolarSystemSimulator()
power_mng = PowerManager(houses_sim, solar_sim)
base_time = nsrdb_start_point + timedelta(days=2, hours=12)
time_sim._start_point = base_time

data = {
    'timestamp': [],
    'house_1_soc': [],
    'house_2_soc': [],
    'house_3_soc': [],
    'house_1_residual_capacity': [],
    'house_2_residual_capacity': [],
    'house_3_residual_capacity': [],
    'house_1_total_capacity': [],
    'house_2_total_capacity': [],
    'house_3_total_capacity': [],
    'house_1_charge_power': [],
    'house_2_charge_power': [],
    'house_3_charge_power': [],
    'house_1_discharge_power': [],
    'house_2_discharge_power': [],
    'house_3_discharge_power': [],
    'house_1_load': [],
    'house_2_load': [],
    'house_3_load': [],
    'solar_power': [],
    'physical_battery_soc': [],
}

simulation_hours = 24
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

    # Collect virtual battery data
    vb_data = []
    for i, vb in enumerate(power_mng.virtual_batteries):
        soc = (vb.residual_capacity / vb.total_capacity * 100) if vb.total_capacity > 0 else 0
        vb_data.extend([
            soc,
            vb.residual_capacity,
            vb.total_capacity,
            getattr(vb, '_last_charge_power', 0),  # Track charge power if available
            getattr(vb, '_last_discharge_power', 0)  # Track discharge power if available
        ])

    # Collect data
    data['timestamp'].append(current_timestamp)
    data['house_1_soc'].append(vb_data[0])
    data['house_2_soc'].append(vb_data[5])
    data['house_3_soc'].append(vb_data[10])
    data['house_1_residual_capacity'].append(vb_data[1])
    data['house_2_residual_capacity'].append(vb_data[6])
    data['house_3_residual_capacity'].append(vb_data[11])
    data['house_1_total_capacity'].append(vb_data[2])
    data['house_2_total_capacity'].append(vb_data[7])
    data['house_3_total_capacity'].append(vb_data[12])
    data['house_1_charge_power'].append(vb_data[3])
    data['house_2_charge_power'].append(vb_data[8])
    data['house_3_charge_power'].append(vb_data[13])
    data['house_1_discharge_power'].append(vb_data[4])
    data['house_2_discharge_power'].append(vb_data[9])
    data['house_3_discharge_power'].append(vb_data[14])
    data['house_1_load'].append(houses_sim.houses[0].load_power)
    data['house_2_load'].append(houses_sim.houses[1].load_power)
    data['house_3_load'].append(houses_sim.houses[2].load_power)
    data['solar_power'].append(solar_sim.panels.total_power)
    data['physical_battery_soc'].append((solar_sim.battery.residual_capacity /
                                        solar_sim.battery.conf.total_capacity * 100) if solar_sim.battery.conf.total_capacity > 0 else 0)

df = pd.DataFrame(data)

fig, axes = plt.subplots(3, 1, figsize=(10, 12))
fig.suptitle('Virtual Battery State-of-Charge Tracking and Energy Flow', fontsize=14, fontweight='bold')

# Plot 1: Virtual battery SoC evolution
ax1 = axes[0]
ax1.plot(df['timestamp'], df['house_1_soc'], 'r-', linewidth=2.5, label='House 1 VB SoC')
ax1.plot(df['timestamp'], df['house_2_soc'], 'g-', linewidth=2.5, label='House 2 VB SoC')
ax1.plot(df['timestamp'], df['house_3_soc'], 'b-', linewidth=2.5, label='House 3 VB SoC')

# Add physical battery SoC for reference
ax1.plot(df['timestamp'], df['physical_battery_soc'], 'k--', linewidth=2, alpha=0.7, label='Physical Battery SoC')

# Fill areas to show SoC levels
ax1.fill_between(df['timestamp'], df['house_1_soc'], alpha=0.2, color='red')
ax1.fill_between(df['timestamp'], df['house_2_soc'], alpha=0.2, color='green')
ax1.fill_between(df['timestamp'], df['house_3_soc'], alpha=0.2, color='blue')

ax1.set_title('Virtual Battery State-of-Charge Evolution', fontsize=12, fontweight='bold')
ax1.set_ylabel('State-of-Charge [%]')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax1.set_ylim(0, 100)

# Plot 2: Virtual battery capacity allocation over time
ax2 = axes[1]
ax2.plot(df['timestamp'], df['house_1_residual_capacity'] / 1000, 'r-', linewidth=2.5, label='House 1 Residual')
ax2.plot(df['timestamp'], df['house_2_residual_capacity'] / 1000, 'g-', linewidth=2.5, label='House 2 Residual')
ax2.plot(df['timestamp'], df['house_3_residual_capacity'] / 1000, 'b-', linewidth=2.5, label='House 3 Residual')

# Show total capacity as dotted lines
ax2.plot(df['timestamp'], df['house_1_total_capacity'] / 1000, 'r:', linewidth=1.5, alpha=0.7, label='House 1 Total')
ax2.plot(df['timestamp'], df['house_2_total_capacity'] / 1000, 'g:', linewidth=1.5, alpha=0.7, label='House 2 Total')
ax2.plot(df['timestamp'], df['house_3_total_capacity'] / 1000, 'b:', linewidth=1.5, alpha=0.7, label='House 3 Total')

ax2.set_title('Virtual Battery Residual and Total Capacity', fontsize=12, fontweight='bold')
ax2.set_ylabel('Capacity [kWh]')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

# Plot 3: House loads and solar generation context
ax3 = axes[2]
ax3.plot(df['timestamp'], df['house_1_load'], 'r-', linewidth=2, alpha=0.7, label='House 1 Load')
ax3.plot(df['timestamp'], df['house_2_load'], 'g-', linewidth=2, alpha=0.7, label='House 2 Load')
ax3.plot(df['timestamp'], df['house_3_load'], 'b-', linewidth=2, alpha=0.7, label='House 3 Load')
ax3.plot(df['timestamp'], df['solar_power'], 'orange', linewidth=3, label='Solar Generation')

# Fill area for solar generation
ax3.fill_between(df['timestamp'], df['solar_power'], alpha=0.3, color='orange')

ax3.set_title('Energy Context: House Loads and Solar Generation', fontsize=12, fontweight='bold')
ax3.set_ylabel('Power [W]')
ax3.legend()
ax3.grid(True, alpha=0.3)
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

# Format x-axis for all subplots
for ax in axes.flat:
    ax.tick_params(axis='x', rotation=45)
    plt.setp(ax.xaxis.get_majorticklabels(), ha='right')

plt.tight_layout(pad=2)
plt.show()
