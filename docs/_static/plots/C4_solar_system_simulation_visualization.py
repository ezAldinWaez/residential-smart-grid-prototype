from rsgp.utils.nsrdb_data import nsrdb_start_point
from rsgp.solar_system_sim.simulator import SolarSystemSimulator
from rsgp.houses_sim.simulator import HousesSimulator
from docs._static.plots.scenario_events import SCENARIO_EVENTS

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from datetime import timedelta

solar_sim = SolarSystemSimulator()
houses_sim = HousesSimulator()
base_time = nsrdb_start_point + timedelta(days=2)

data = {
    'timestamp': [],
    'panels_total_power': [],
    'battery_residual_capacity': [],
    'battery_soc': [],
    'inverter_panels_power': [],
    'inverter_battery_exchange_power': [],
    'inverter_load_line': [],
    'inverter_load_power': [],
    'inverter_utility_line': [],
    'inverter_utility_exchange_power': [],
}

simulation_hours = 24
steps_per_hour = 10
total_steps = simulation_hours * steps_per_hour
dt_hours = 1.0 / steps_per_hour  # 6 minutes
dt_seconds = dt_hours * 3600

for step in range(total_steps):
    current_time_hours = step * dt_hours
    current_timestamp = base_time + timedelta(hours=current_time_hours)

    for event_time, event_callback in SCENARIO_EVENTS:
        if abs(current_time_hours - event_time) < dt_hours / 2:
            event_callback(houses_sim)

    houses_sim._update_step()
    system_load = sum(house.load_power for house in houses_sim.houses)

    solar_power = solar_sim.panels.calc_total_power(current_timestamp)
    solar_sim.inverter.load_power = system_load

    solar_sim.inverter.operate(current_timestamp, dt_seconds)

    data['timestamp'].append(current_timestamp)
    data['panels_total_power'].append(solar_power)
    data['battery_residual_capacity'].append(solar_sim.battery.residual_capacity)
    data['battery_soc'].append((solar_sim.battery.residual_capacity / solar_sim.battery.conf.total_capacity) * 100)
    data['inverter_panels_power'].append(solar_sim.inverter.panels_power)
    data['inverter_battery_exchange_power'].append(solar_sim.inverter.battery_exchange_power)
    data['inverter_load_line'].append(int(solar_sim.inverter.load_line))
    data['inverter_load_power'].append(solar_sim.inverter.load_power)
    data['inverter_utility_line'].append(int(solar_sim.inverter.utility_line))
    data['inverter_utility_exchange_power'].append(solar_sim.inverter.utility_exchange_power)

df = pd.DataFrame(data)

fig, axes = plt.subplots(3, 1, figsize=(10, 9))
fig.suptitle('Solar System Simulation: Response to Device Control Scenario', fontsize=14, fontweight='bold')

# Plot 1: Solar generation and load consumption
ax1 = axes[0]
ax1.plot(df['timestamp'], df['panels_total_power'], 'orange', linewidth=2, label='Solar Generation')
ax1.plot(df['timestamp'], df['inverter_load_power'], 'blue', linewidth=2, label='Load Consumption')
ax1.fill_between(df['timestamp'], df['panels_total_power'], alpha=0.3, color='orange')
ax1.fill_between(df['timestamp'], df['inverter_load_power'], alpha=0.3, color='blue')
ax1.set_title('Solar Generation vs Load Consumption', fontsize=12, fontweight='bold')
ax1.set_ylabel('Power [W]')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

# Plot 2: Battery state and exchange power
ax2 = axes[1]
ax2_twin = ax2.twinx()

ax2.plot(df['timestamp'], df['battery_soc'], 'green', linewidth=2, label='Battery SoC')
ax2.fill_between(df['timestamp'], df['battery_soc'], alpha=0.3, color='green')

battery_exchange_kw = df['inverter_battery_exchange_power']
ax2_twin.plot(df['timestamp'], battery_exchange_kw, 'purple', linewidth=2, alpha=0.8, label='Battery Power Exchange')
ax2_twin.axhline(y=0, color='black', linestyle='--', alpha=0.5)


ax2.set_title('Battery Operation', fontsize=12, fontweight='bold')
ax2.set_ylabel('State of Charge [%]', color='green')
ax2.tick_params(axis='y', labelcolor='green')
ax2.set_ylim(0, 100)
ax2_twin.set_ylabel('Power Exchange [W]', color='purple')
ax2_twin.tick_params(axis='y', labelcolor='purple')

lines1, labels1 = ax2.get_legend_handles_labels()
lines2, labels2 = ax2_twin.get_legend_handles_labels()
ax2.legend(lines1 + lines2, labels1 + labels2)

ax2.grid(True, alpha=0.3)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

# Plot 3: Utility grid exchange
# TODO: Simplify and fix this plot
ax4 = axes[2]
positive_mask = df['inverter_utility_exchange_power'] >= 0
negative_mask = df['inverter_utility_exchange_power'] < 0

if positive_mask.any():
    ax4.plot(df['timestamp'][positive_mask], df['inverter_utility_exchange_power'][positive_mask],
             'green', linewidth=2, label='Export to Grid')
if negative_mask.any():
    ax4.plot(df['timestamp'][negative_mask], df['inverter_utility_exchange_power'][negative_mask],
             'red', linewidth=2, label='Import from Grid')

ax4.fill_between(df['timestamp'], df['inverter_utility_exchange_power'], 0,
                 where=(df['inverter_utility_exchange_power'] >= 0), alpha=0.3, color='green', interpolate=True)
ax4.fill_between(df['timestamp'], df['inverter_utility_exchange_power'], 0,
                 where=(df['inverter_utility_exchange_power'] < 0), alpha=0.3, color='red', interpolate=True)

ax4.axhline(y=0, color='black', linestyle='-', alpha=0.5)
ax4.set_title('Utility Grid Exchange', fontsize=12, fontweight='bold')
ax4.set_ylabel('Power [W]')
ax4.legend()
ax4.grid(True, alpha=0.3)
ax4.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

for ax in axes.flat:
    ax.tick_params(axis='x', rotation=45)
    plt.setp(ax.xaxis.get_majorticklabels(), ha='right')

plt.tight_layout(pad=4)
plt.show()

pass
