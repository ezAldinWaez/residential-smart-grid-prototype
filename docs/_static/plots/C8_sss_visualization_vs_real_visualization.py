"""
Solar System Simulation vs Real Inverter Data Comparison.

This script compares the RSGP solar system simulation against real SolarMax inverter 
PV power generation data from a physical 8-panel installation in Aleppo, Syria.

Real inverter data extracted from clear-sky day: February 4, 2025
SSS data generated using NSRDB Arizona data with 8-panel configuration
"""

from rsgp.solar_system_sim.simulator import SolarSystemSimulator
from rsgp.houses_sim.simulator import HousesSimulator
from rsgp.power_mng.manager import PowerManager
from rsgp.config.settings import settings
from rsgp.utils.nsrdb_data import nsrdb_start_point
from rsgp.utils.time_sim import time_sim

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import timedelta
import csv


def load_real_inverter_data():
    """
    Load real SolarMax inverter PV power data from clear-sky day (Feb 4, 2025).

    Extracts PV power generation from 8-panel system in Aleppo, Syria.
    Focuses on clear-sky day with good solar conditions for comparison.

    Returns:
        tuple: (time_hours, pv_power_watts) arrays for real inverter PV data
    """
    csv_path = '../data/inverter_logs/DataLog_929321041053717_20250203-20250209.csv'

    # Read CSV with proper handling of multiline timestamps
    # Create DataFrame
    columns = [
        'Device_mode', 'Time', 'AC_voltage_V', 'AC_frequency_Hz',
        'Battery_voltage_V', 'Battery_capacity_pct', 'Charging_current_A',
        'Battery_discharge_current_A', 'Output_voltage_V', 'Output_frequency_Hz',
        'Output_apparent_power_VA', 'Output_active_power_W', 'Load_percent',
        'PV1_input_voltage_V', 'PV1_input_power_W'
    ]
    data = []
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        _ = next(reader)  # Skip header

        for row in reader:
            if len(row) >= 15:  # Ensure we have all columns
                data.append(row)

    df = pd.DataFrame(data, columns=columns)

    # Clean and convert timestamp (handle multiline format)
    df['Time'] = df['Time'].str.replace('\n', ' ').str.strip()
    df['timestamp'] = pd.to_datetime(df['Time'])
    df['PV1_input_power_W'] = pd.to_numeric(df['PV1_input_power_W'], errors='coerce')

    # Filter for clear-sky day: February 4, 2025 (highest peak power from analysis)
    clear_sky_date = '2025-02-04'
    df = df[df['timestamp'].dt.date == pd.to_datetime(clear_sky_date).date()]

    # Remove invalid data points
    df = df.dropna(subset=['timestamp', 'PV1_input_power_W'])
    df = df[df['PV1_input_power_W'] >= 0]  # Remove negative values

    # Sort by time
    df = df.sort_values('timestamp')

    # Convert to time_hours relative to start of day
    start_of_day = df['timestamp'].min().replace(hour=0, minute=0, second=0, microsecond=0)
    time_hours = (df['timestamp'] - start_of_day).dt.total_seconds() / 3600
    pv_power_watts = df['PV1_input_power_W'].values

    return time_hours, pv_power_watts


def generate_sss_pv_data():
    """
    Generate SSS PV power data using RSGP system with 8-panel configuration.

    Uses NSRDB Arizona data with pvlib modeling to simulate a full 24-hour 
    clear-sky day for comparison with real inverter data.

    Accounts for timezone difference: Aleppo (UTC+2) vs Arizona (UTC-7) = 9 hours

    Returns:
        tuple: (time_hours, pv_power_watts) arrays for SSS PV data
    """
    # Configure simulation settings for 8-panel system (matching real system)
    original_panels = settings.PANELS_NUM
    settings.PANELS_NUM = 8  # Set to match real system

    # Initialize RSGP simulators
    solar_sim = SolarSystemSimulator()
    houses_sim = HousesSimulator()
    power_mng = PowerManager(houses_sim, solar_sim)

    houses_sim._dt = (30 / settings.TIME_FACTOR) * 1000
    solar_sim._dt = (30 / settings.TIME_FACTOR) * 1000
    power_mng._dt = (30 / settings.TIME_FACTOR) * 1000

    # Configure simulation timing with timezone adjustment
    base_time = nsrdb_start_point + timedelta(days=40, hours=7)  # Adjust for timezone difference
    time_sim._start_point = base_time

    # Generate full 24-hour data at 30-second intervals to match real data frequency
    time_hours = np.arange(0, 24, 0.5/60)  # Every 30 seconds for full day

    # Generate SSS PV power profile for full 24 hours
    pv_power_sss = []

    for t_hours in time_hours:
        t_seconds = t_hours * 3600

        # Update simulators for current time
        houses_sim._update_step(t_seconds)
        solar_sim._update_step(t_seconds)
        power_mng._update_step(t_seconds)

        # Collect PV power output
        pv_power = solar_sim.panels.total_power
        pv_power_sss.append(pv_power)

    pv_power_sss = np.array(pv_power_sss)

    # Restore original panel setting
    settings.PANELS_NUM = original_panels

    return time_hours, pv_power_sss


# Load real data
time_real, power_real = load_real_inverter_data()

# Generate SSS data for full 24 hours with timezone adjustment
time_sss, power_sss = generate_sss_pv_data()

# Create figure with subplots - following ADSR comparison style
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))
fig.suptitle('RSGP Solar System Simulation vs Real SolarMax PV Power Comparison',
             fontsize=14, fontweight='bold')

# Plot 1: Real PV data
ax1.plot(time_real, power_real, 'g-', linewidth=1.2, label='Real SolarMax PV Power (8 panels, Aleppo Syria)')
ax1.set_ylabel('PV Power [W]')
ax1.set_title('Real SolarMax Inverter PV Power Generation (Clear-sky day, Feb 4, 2025)')
ax1.grid(True)
ax1.legend()
ax1.set_xlim(0, 24)  # Show full 24-hour range
ax1.set_xticks(range(0, 25, 3))  # Major ticks every 3 hours
ax1.set_ylim(0, max(power_real.max(), power_sss.max()) * 1.1)

# Plot 2: SSS Model
ax2.plot(time_sss, power_sss, 'b-', linewidth=1.2, label='RSGP SSS PV Power (8 panels, NSRDB Arizona)')
ax2.set_ylabel('PV Power [W]')
ax2.set_title('RSGP Solar System Simulation PV Power Generation (pvlib + NSRDB)')
ax2.grid(True)
ax2.legend()
ax2.set_xlim(0, 24)  # Show full 24-hour range
ax2.set_xticks(range(0, 25, 3))  # Major ticks every 3 hours
ax2.set_ylim(0, max(power_real.max(), power_sss.max()) * 1.1)

# Plot 3: Overlay comparison
ax3.plot(time_real, power_real, 'g-', linewidth=1.2, alpha=0.7, label='Real SolarMax Data')
ax3.plot(time_sss, power_sss, 'b--', linewidth=1.2, alpha=0.7, label='SSS pvlib Model')
ax3.set_xlabel('Time [Hours]')
ax3.set_ylabel('PV Power [W]')
ax3.set_title('Direct Comparison: Real vs SSS PV Power Generation')
ax3.grid(True)
ax3.legend()
ax3.set_xlim(0, 24)  # Show full 24-hour range
ax3.set_xticks(range(0, 25, 3))  # Major ticks every 3 hours
ax3.set_ylim(0, max(power_real.max(), power_sss.max()) * 1.1)

# Calculate comparison statistics
real_energy = np.trapezoid(y=power_real, x=time_real)
sss_energy = np.trapezoid(y=power_sss, x=time_sss)
real_avg = np.mean(power_real[power_real > 10])  # Average when generating
sss_avg = np.mean(power_sss[power_sss > 10])    # Average when generating

# Add statistics box
stats_text = f"""Energy Comparison (Clear-sky Day):
Real SolarMax: {real_energy:.1f} Wh
SSS pvlib Model: {sss_energy:.1f} Wh
Difference: {abs(real_energy - sss_energy):.1f} Wh ({abs(real_energy - sss_energy)/real_energy*100:.1f}%)

Average PV Power (when generating):
Real SolarMax: {real_avg:.1f} W
SSS Model: {sss_avg:.1f} W

System Configuration: 8 solar panels
Real: Aleppo, Syria Feb 2025 | SSS: NSRDB Arizona 2023"""

ax3.text(0.02, 0.98, stats_text, transform=ax3.transAxes, fontsize=9,
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

plt.tight_layout(pad=2)
plt.show()
