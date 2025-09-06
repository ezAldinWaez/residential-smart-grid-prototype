"""
ADSR Device Model vs Real Load Profile Comparison.

This script compares the RSGP ADSR envelope refrigerator model against real refrigerator
power consumption data from MDPI paper (Energies 2018, 11, 607).

Real refrigerator data extracted from Figure 4 using WebPlotDigitizer.
"""

from rsgp.houses_sim.device import DeviceClass
from rsgp.config.settings import settings
import matplotlib.pyplot as plt
import numpy as np

# Configure simulation settings
settings.TIME_FACTOR = 1.0


def load_real_refrigerator_data():
    """
    Load real refrigerator power consumption data extracted from MDPI paper Figure 4.

    Data extracted using WebPlotDigitizer from:
    Paper: "The Determination of Load Profiles and Power Consumptions of Home Appliances"
    Energies 2018, 11, 607; https://doi.org/10.3390/en11030607
    Figure 4: Daily power consumption of the refrigerator

    Returns:
        tuple: (time_hours, power_watts) arrays for real refrigerator data
    """

    # Path to the extracted data    
    csv_path = '../data/real_refrigerator_power_MDPI_2018_figure4_WebPlotDigitizer.csv'

    # Load data
    data = np.loadtxt(csv_path, delimiter=',')
    time_hours = data[:, 0]
    power_watts = data[:, 1]

    # Clean negative baseline values (likely digitization artifacts)
    power_watts = np.maximum(power_watts, 0)

    return time_hours, power_watts


def generate_adsr_refrigerator_data(real_time_hours, real_power_watts):
    """
    Generate ADSR refrigerator model data using RSGP system.
    Matches the timing of the real data by detecting when device turns on/off.

    Args:
        real_time_hours: Time array from real data
        real_power_watts: Power array from real data

    Returns:
        tuple: (time_hours, power_watts) arrays for ADSR model
    """
    # Create refrigerator device using RSGP system (same as C3 approach)
    refrigerator = DeviceClass('REFRIGERATOR')

    # Analyze real data to find device on/off transitions
    power_threshold = 5.0  # Watts - threshold to determine on/off state

    # Find when device turns on and off
    device_on_times = []
    device_off_times = []

    is_currently_on = False
    for i in range(len(real_power_watts)):
        power_now = real_power_watts[i]

        if not is_currently_on and power_now > power_threshold:
            # Device turned on
            device_on_times.append(real_time_hours[i])
            is_currently_on = True
        elif is_currently_on and power_now <= power_threshold:
            # Device turned off
            device_off_times.append(real_time_hours[i])
            is_currently_on = False

    for i, on_time in enumerate(device_on_times):
        off_time = device_off_times[i] if i < len(device_off_times) else "end"

    # Create time array matching real data
    time_hours = real_time_hours.copy()
    time_seconds = time_hours * 3600

    # Generate ADSR power profile with same on/off timing
    power_adsr = []
    current_state_on = False

    for i, t_hours in enumerate(time_hours):
        t_seconds = t_hours * 3600

        # Check if we should toggle device state based on real data transitions
        should_be_on = False
        for j, on_time in enumerate(device_on_times):
            if j < len(device_off_times):
                off_time = device_off_times[j]
                if on_time <= t_hours <= off_time:
                    should_be_on = True
                    break
            else:
                # Last cycle, no off time yet
                if t_hours >= on_time:
                    should_be_on = True
                    break

        # Toggle device if state changed
        if should_be_on and not current_state_on:
            refrigerator.toggle_envelope_state(0, t_seconds)
            current_state_on = True
        elif not should_be_on and current_state_on:
            refrigerator.toggle_envelope_state(0, t_seconds)
            current_state_on = False

        # Calculate power at current time
        power = refrigerator.calc_load(t_seconds)
        power_adsr.append(power)

    power_adsr = np.array(power_adsr)

    return time_hours, power_adsr


# Load real data
time_real, power_real = load_real_refrigerator_data()

# Generate ADSR data matching real data timing
time_adsr, power_adsr = generate_adsr_refrigerator_data(time_real, power_real)

# Create figure with subplots - following C3 style
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))
fig.suptitle('RSGP ADSR Refrigerator Model vs Real Load Profile Comparison',
             fontsize=14, fontweight='bold')

# Plot 1: Real data
ax1.plot(time_real, power_real, 'g-', linewidth=1.2, label='Real Refrigerator Data (MDPI 2018)')
ax1.set_ylabel('Power [W]')
ax1.set_title('Real Refrigerator Power Consumption (WebPlotDigitizer Extract)')
ax1.grid(True)
ax1.legend()
ax1.set_ylim(0, max(power_real.max(), power_adsr.max()) * 1.1)

# Plot 2: ADSR Model
ax2.plot(time_adsr, power_adsr, 'b-', linewidth=1.2, label='RSGP ADSR Model')
ax2.set_ylabel('Power [W]')
ax2.set_title('RSGP ADSR Envelope Refrigerator Model')
ax2.grid(True)
ax2.legend()
ax2.set_ylim(0, max(power_real.max(), power_adsr.max()) * 1.1)

# Plot 3: Overlay comparison
ax3.plot(time_real, power_real, 'g-', linewidth=1.2, alpha=0.7, label='Real Data')
ax3.plot(time_adsr, power_adsr, 'b--', linewidth=1.2, alpha=0.7, label='ADSR Model')
ax3.set_xlabel('Time [Hours]')
ax3.set_ylabel('Power [W]')
ax3.set_title('Direct Comparison: Real vs ADSR Model')
ax3.grid(True)
ax3.legend()
ax3.set_ylim(0, max(power_real.max(), power_adsr.max()) * 1.1)

# Calculate comparison statistics
real_energy = np.trapezoid(y=power_real, x=time_real)
adsr_energy = np.trapezoid(y=power_adsr, x=time_adsr)
real_avg = np.mean(power_real[power_real > 25])
adsr_avg = np.mean(power_adsr[power_adsr > 25])

# Add statistics box
stats_text = f"""Energy Comparison:
Real Data: {real_energy:.1f} Wh
ADSR Model: {adsr_energy:.1f} Wh
Difference: {abs(real_energy - adsr_energy):.1f} Wh ({abs(real_energy - adsr_energy)/real_energy*100:.1f}%)

Average Power (when active):
Real Data: {real_avg:.1f} W
ADSR Model: {adsr_avg:.1f} W"""

ax3.text(0.02, 0.98, stats_text, transform=ax3.transAxes, fontsize=9,
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

plt.tight_layout(pad=2)
plt.show()
