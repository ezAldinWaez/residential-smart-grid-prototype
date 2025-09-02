import subprocess
import time
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from Pyro5.api import Proxy
from dotenv import load_dotenv


# Start RSGP simulation as subprocess
rsgp_process = subprocess.Popen(
    ['python', '-m', 'rsgp'],
    cwd='../../../',
    env={**os.environ, 'CSV_LOGGING': 'True'})

# Wait for simulation to start up
time.sleep(3)

try:
    # Setup Pyro connections
    load_dotenv()
    HOST = os.getenv('RSGP_REMOTE_OBJECT_HOST', '0.0.0.0')
    PORT = int(os.getenv('RSGP_REMOTE_OBJECT_PORT', 41991))
    BASE = f'PYRO:{{name}}@{HOST}:{PORT}'

    time_sim = Proxy(BASE.format(name='time_sim'))
    houses_sim = Proxy(BASE.format(name='houses_sim'))
    settings = Proxy(BASE.format(name='settings'))

    # Run the device control scenario
    scenario_events = [
        # Turn on HVAC in house 1 (simulates 2 hours)
        (2, lambda elapsed_sim: houses_sim.get_house(0).get_device('HVAC').toggle_envelope_state(0, elapsed_sim)),
        # Turn on WATER_HEATER in house 2 (simulates 4 hours)
        (4, lambda elapsed_sim: houses_sim.get_house(1).get_device('WATER_HEATER').toggle_envelope_state(0, elapsed_sim)),
        # Turn on MICROWAVE in house 3 (simulates 6 hours)
        (6, lambda elapsed_sim: houses_sim.get_house(2).get_device('MICROWAVE').toggle_envelope_state(0, elapsed_sim)),
        # Turn on REFRIGERATOR in house 1 (simulates 8 hours)
        (8, lambda elapsed_sim: houses_sim.get_house(0).get_device('REFRIGERATOR').toggle_envelope_state(0, elapsed_sim)),
        # Turn off HVAC in house 1 (simulates 12 hours)
        (12, lambda elapsed_sim: houses_sim.get_house(0).get_device('HVAC').toggle_envelope_state(0, elapsed_sim)),
        # Turn on HVAC in house 2 (simulates 15 hours)
        (15, lambda elapsed_sim: houses_sim.get_house(1).get_device('HVAC').toggle_envelope_state(0, elapsed_sim)),
        # Turn off WATER_HEATER in house 2 (simulates 18 hours)
        (18, lambda elapsed_sim: houses_sim.get_house(1).get_device('WATER_HEATER').toggle_envelope_state(0, elapsed_sim)),
        # Turn off MICROWAVE in house 3 (simulates 20 hours)
        (20, lambda elapsed_sim: houses_sim.get_house(2).get_device('MICROWAVE').toggle_envelope_state(0, elapsed_sim)),
    ]

    start_time = time.time()
    for event_time, event_callback in scenario_events:
        # Wait until the event time
        while (time.time() - start_time) < event_time:
            time.sleep(0.1)

        event_callback(time_sim.get_elapsed())

    csv_file = settings.get_setting('CSV_HS_LOG_PATH')

    # Let simulation run for a bit more to capture final data
    time.sleep(3)

finally:
    rsgp_process.terminate()

# Read CSV data
df = pd.read_csv(csv_file)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Create the plot
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle('RSGP Houses Simulation: Real-time Device Control Scenario', fontsize=16, fontweight='bold')

# Plot 1: System load over time
ax1 = axes[0, 0]
ax1.plot(df['timestamp'], df['system_load'], 'b-', linewidth=2, label='System Load')
ax1.set_title('Total System Load')
ax1.set_ylabel('Power (W)')
ax1.grid(True, alpha=0.3)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

# Plot 2: Individual house loads
ax2 = axes[0, 1]
ax2.plot(df['timestamp'], df['house_1_load_power'], 'r-', label='House 1', linewidth=2)
ax2.plot(df['timestamp'], df['house_2_load_power'], 'g-', label='House 2', linewidth=2)
ax2.plot(df['timestamp'], df['house_3_load_power'], 'b-', label='House 3', linewidth=2)
ax2.set_title('Individual House Loads')
ax2.set_ylabel('Power (W)')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

# Plot 3: Load line states
ax3 = axes[1, 0]
ax3.step(df['timestamp'], df['house_1_load_line'], 'r-', where='post', label='House 1', linewidth=2)
ax3.step(df['timestamp'], df['house_2_load_line'], 'g-', where='post', label='House 2', linewidth=2)
ax3.step(df['timestamp'], df['house_3_load_line'], 'b-', where='post', label='House 3', linewidth=2)
ax3.set_title('Load Line Connection States')
ax3.set_ylabel('Connected (1) / Disconnected (0)')
ax3.set_ylim(-0.1, 1.1)
ax3.legend()
ax3.grid(True, alpha=0.3)
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

# Plot 4: Utility exchange power
ax4 = axes[1, 1]
ax4.plot(df['timestamp'], df['house_1_utility_power'], 'r-', label='House 1', linewidth=2)
ax4.plot(df['timestamp'], df['house_2_utility_power'], 'g-', label='House 2', linewidth=2)
ax4.plot(df['timestamp'], df['house_3_utility_power'], 'b-', label='House 3', linewidth=2)
ax4.axhline(y=0, color='k', linestyle='--', alpha=0.5)
ax4.set_title('Utility Exchange Power')
ax4.set_ylabel('Power (W)\n(+: Export, -: Import)')
ax4.legend()
ax4.grid(True, alpha=0.3)
ax4.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

# Format x-axis for all subplots
for ax in axes.flat:
    ax.tick_params(axis='x', rotation=45)
    plt.setp(ax.xaxis.get_majorticklabels(), ha='right')

plt.show()
