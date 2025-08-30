import matplotlib.pyplot as plt
import numpy as np

from rsgp.houses_sim.device import DeviceClass
from rsgp.houses_sim.data import ADSRConf, DeviceConf
from rsgp.config.settings import settings

settings.TIME_FACTOR = 1.0

# Create device configurations with different ADSR parameters
# Base configuration (HVAC-like)
base_adsr = ADSRConf(a=3, d=2, s=0.8, r=0.5, wt='none', wp=2, wa=0.0)
base_conf = DeviceConf(base_watt=3500, max_count=1, adsr=base_adsr)

# Attack time variations
fast_attack_adsr = ADSRConf(a=1, d=2, s=0.8, r=0.5, wt='none', wp=2, wa=0.0)
slow_attack_adsr = ADSRConf(a=6, d=2, s=0.8, r=0.5, wt='none', wp=2, wa=0.0)

# Sustain level variations
low_sustain_adsr = ADSRConf(a=3, d=2, s=0.4, r=0.5, wt='none', wp=2, wa=0.0)
high_sustain_adsr = ADSRConf(a=3, d=2, s=1.0, r=0.5, wt='none', wp=2, wa=0.0)

# Release time variations
fast_release_adsr = ADSRConf(a=3, d=2, s=0.8, r=0.2, wt='none', wp=2, wa=0.0)
slow_release_adsr = ADSRConf(a=3, d=2, s=0.8, r=2.0, wt='none', wp=2, wa=0.0)

# Wave modulation variations
sine_wave_adsr = ADSRConf(a=3, d=2, s=0.8, r=0.5, wt='sine', wp=2, wa=0.15)
square_wave_adsr = ADSRConf(a=3, d=2, s=0.8, r=0.5, wt='square', wp=2, wa=0.15)

# Create device classes with different configurations
configurations = [
    # Attack time comparison
    [
        (DeviceConf(base_watt=3500, max_count=1, adsr=fast_attack_adsr), 'Fast Attack (1s)', 'red'),
        (DeviceConf(base_watt=3500, max_count=1, adsr=base_adsr), 'Normal Attack (3s)', 'blue'),
        (DeviceConf(base_watt=3500, max_count=1, adsr=slow_attack_adsr), 'Slow Attack (6s)', 'orange')
    ],
    # Sustain level comparison
    [
        (DeviceConf(base_watt=3500, max_count=1, adsr=low_sustain_adsr), 'Low Sustain (0.4)', 'green'),
        (DeviceConf(base_watt=3500, max_count=1, adsr=base_adsr), 'Normal Sustain (0.8)', 'blue'),
        (DeviceConf(base_watt=3500, max_count=1, adsr=high_sustain_adsr), 'High Sustain (1.0)', 'purple')
    ],
    # Release time comparison
    [
        (DeviceConf(base_watt=3500, max_count=1, adsr=fast_release_adsr), 'Fast Release (0.2s)', 'cyan'),
        (DeviceConf(base_watt=3500, max_count=1, adsr=base_adsr), 'Normal Release (0.5s)', 'blue'),
        (DeviceConf(base_watt=3500, max_count=1, adsr=slow_release_adsr), 'Slow Release (2.0s)', 'magenta')
    ],
    # Wave modulation comparison
    [
        (DeviceConf(base_watt=3500, max_count=1, adsr=ADSRConf(a=3, d=2, s=0.8, r=0.5, wt='none', wp=2, wa=0.0)), 'No Wave', 'gray'),
        (DeviceConf(base_watt=3500, max_count=1, adsr=sine_wave_adsr), 'Sine Wave (15%)', 'blue'),
        (DeviceConf(base_watt=3500, max_count=1, adsr=square_wave_adsr), 'Square Wave (15%)', 'red')
    ]
]

titles = ['Attack Time Impact', 'Sustain Level Impact', 'Release Time Impact', 'Wave Modulation Impact']

# Create the plot
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle('ADSR Parameter Impact on Device Load Curves', fontsize=16, fontweight='bold')

time = np.linspace(0.0, 30.0, 300)

for idx, (config_set, title) in enumerate(zip(configurations, titles)):
    ax = axes[idx // 2, idx % 2]

    for device_conf, label, color in config_set:
        # Create fresh device class with custom configuration
        device = DeviceClass('HVAC')
        device.conf = device_conf

        # Pre-calculate segments like the reference example
        # Segment 1: OFF (0-5s)
        power_1 = np.array([device.calc_load(t) for t in time[time < 5.0]])

        # Turn ON at t=5
        device.toggle_envelope_state(0, 5.0)

        # Segment 2: ON (5-15s)
        power_2 = np.array([device.calc_load(t) for t in time[(time >= 5.0) & (time < 15.0)]])

        # Turn OFF at t=15
        device.toggle_envelope_state(0, 15.0)

        # Segment 3: OFF (15-25s)
        power_3 = np.array([device.calc_load(t) for t in time[(time >= 15.0) & (time < 25.0)]])

        # Turn ON at t=25
        device.toggle_envelope_state(0, 25.0)

        # Segment 4: ON (25-30s)
        power_4 = np.array([device.calc_load(t) for t in time[time >= 25.0]])

        # Combine all segments
        power_values = np.concatenate([power_1, power_2, power_3, power_4])

        ax.plot(time, power_values, label=label, color=color, alpha=0.7)

    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlabel('Time (seconds)', fontsize=11)
    ax.set_ylabel('Power (W)', fontsize=11)
    ax.legend()
    ax.grid(True, alpha=0.3, linestyle='--')

    # Add toggle time indicators
    ax.axvline(x=5, color='black', linestyle=':', alpha=0.6, label='Device On')
    ax.axvline(x=15, color='red', linestyle=':', alpha=0.6, label='Device Off')
    ax.axvline(x=25, color='black', linestyle=':', alpha=0.6, label='Device On')

    # Add phase annotations
    if idx == 0:  # Only on first plot to avoid clutter
        ax.text(7, ax.get_ylim()[1] * 0.85, 'A→D→S', fontsize=9, alpha=0.7,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3))
        ax.text(16, ax.get_ylim()[1] * 0.85, 'Release', fontsize=9, alpha=0.7,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='orange', alpha=0.3))

plt.tight_layout(pad=3.0)
plt.show()
