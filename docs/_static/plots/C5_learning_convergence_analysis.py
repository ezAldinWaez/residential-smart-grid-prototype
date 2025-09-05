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


def run_simulation_with_learning_rate(learning_rate):
    """Run simulation with specified learning rate and return weight evolution data"""
    houses_sim = HousesSimulator()
    solar_sim = SolarSystemSimulator()
    power_mng = PowerManager(houses_sim, solar_sim)

    # Set learning rate
    settings.LEARNING_STEP = learning_rate

    base_time = nsrdb_start_point + timedelta(days=2, hours=12)
    time_sim._start_point = base_time

    data = {
        'timestamp': [],
        'house_1_weight': [],
        'house_2_weight': [],
        'house_3_weight': [],
        'weight_variance': [],
        'convergence_metric': [],
    }

    simulation_hours = 24
    steps_per_hour = 10
    total_steps = simulation_hours * steps_per_hour
    dt_hours = 1.0 / steps_per_hour
    dt_seconds = dt_hours * 3600

    houses_sim._dt = (dt_seconds / settings.TIME_FACTOR) * 1000
    solar_sim._dt = (dt_seconds / settings.TIME_FACTOR) * 1000
    power_mng._dt = (dt_seconds / settings.TIME_FACTOR) * 1000

    for step in range(total_steps):
        current_time_hours = step * dt_hours
        current_timestamp = base_time + timedelta(hours=current_time_hours)

        for event_time, event_callback in SCENARIO_EVENTS:
            if abs(current_time_hours - event_time) < dt_hours / 2:
                event_callback(houses_sim)

        houses_sim._update_step()
        solar_sim._update_step()
        power_mng._update_step()

        weights = [vb.weight for vb in power_mng.virtual_batteries]
        weight_variance = np.var(weights)
        convergence_metric = np.std([w - 1.0 for w in weights])  # Deviation from initial weight

        data['timestamp'].append(current_timestamp)
        data['house_1_weight'].append(weights[0])
        data['house_2_weight'].append(weights[1])
        data['house_3_weight'].append(weights[2])
        data['weight_variance'].append(weight_variance)
        data['convergence_metric'].append(convergence_metric)

    return pd.DataFrame(data)


# Run simulations with different learning rates
learning_rates = [0.002, 0.005, 0.01]
learning_rate_labels = ['Slow (α=0.002)', 'Normal (α=0.005)', 'Fast (α=0.01)']
learning_rate_colors = ['blue', 'green', 'red']

results = {}
for lr in learning_rates:
    print(f"Running simulation with learning rate {lr}...")
    results[lr] = run_simulation_with_learning_rate(lr)

fig, axes = plt.subplots(3, 1, figsize=(10, 12))
fig.suptitle('Learning Algorithm Convergence Analysis: Weight Evolution', fontsize=14, fontweight='bold')

# Create 3 subplots, one for each learning rate
for i, (lr, label, color) in enumerate(zip(learning_rates, learning_rate_labels, learning_rate_colors)):
    ax = axes[i]
    df = results[lr]
    
    # Plot weight evolution for each house
    ax.plot(df['timestamp'], df['house_1_weight'], color='red', linestyle='-', linewidth=2.5, label='House 1')
    ax.plot(df['timestamp'], df['house_2_weight'], color='green', linestyle='-', linewidth=2.5, label='House 2')
    ax.plot(df['timestamp'], df['house_3_weight'], color='blue', linestyle='-', linewidth=2.5, label='House 3')
    
    # Add reference lines
    ax.axhline(y=1.0, color='black', linestyle='--', alpha=0.5, label='Initial Weight (1.0)')
    ax.axhline(y=0.8, color='orange', linestyle=':', alpha=0.7, label='Min Weight (0.8)')
    ax.axhline(y=1.4, color='purple', linestyle=':', alpha=0.7, label='Max Weight (1.4)')
    
    ax.set_title(f'{label} Learning Rate', fontsize=12, fontweight='bold')
    ax.set_ylabel('Weight Factor')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.set_ylim(0.75, 1.45)

# Format x-axis for all subplots
for ax in axes.flat:
    ax.tick_params(axis='x', rotation=45)
    plt.setp(ax.xaxis.get_majorticklabels(), ha='right')

plt.tight_layout(pad=2)
plt.show()
