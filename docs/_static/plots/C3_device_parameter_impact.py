from rsgp.houses_sim.device import DeviceClass
from rsgp.houses_sim.data import ADSRConf, DeviceConf
from rsgp.config.settings import settings

import matplotlib.pyplot as plt
import numpy as np

settings.TIME_FACTOR = 1.0

base_adsr = ADSRConf(a=3, d=2, s=0.8, r=0.5, wt='none', wp=2, wa=0.0)
base_conf = DeviceConf(base_watt=3500, max_count=1, adsr=base_adsr)

fast_attack_adsr = ADSRConf(a=1, d=2, s=0.8, r=0.5, wt='none', wp=2, wa=0.0)
slow_attack_adsr = ADSRConf(a=6, d=2, s=0.8, r=0.5, wt='none', wp=2, wa=0.0)

low_sustain_adsr = ADSRConf(a=3, d=2, s=0.4, r=0.5, wt='none', wp=2, wa=0.0)
high_sustain_adsr = ADSRConf(a=3, d=2, s=1.0, r=0.5, wt='none', wp=2, wa=0.0)

fast_release_adsr = ADSRConf(a=3, d=2, s=0.8, r=0.2, wt='none', wp=2, wa=0.0)
slow_release_adsr = ADSRConf(a=3, d=2, s=0.8, r=2.0, wt='none', wp=2, wa=0.0)

sine_wave_adsr = ADSRConf(a=3, d=2, s=0.8, r=0.5, wt='sine', wp=2, wa=0.15)
square_wave_adsr = ADSRConf(a=3, d=2, s=0.8, r=0.5, wt='square', wp=2, wa=0.15)

configurations = [
    [
        (DeviceConf(base_watt=3500, max_count=1, adsr=fast_attack_adsr), 'Fast Attack (1s)', 'red'),
        (DeviceConf(base_watt=3500, max_count=1, adsr=base_adsr), 'Normal Attack (3s)', 'blue'),
        (DeviceConf(base_watt=3500, max_count=1, adsr=slow_attack_adsr), 'Slow Attack (6s)', 'orange')
    ],
    [
        (DeviceConf(base_watt=3500, max_count=1, adsr=low_sustain_adsr), 'Low Sustain (0.4)', 'green'),
        (DeviceConf(base_watt=3500, max_count=1, adsr=base_adsr), 'Normal Sustain (0.8)', 'blue'),
        (DeviceConf(base_watt=3500, max_count=1, adsr=high_sustain_adsr), 'High Sustain (1.0)', 'purple')
    ],
    [
        (DeviceConf(base_watt=3500, max_count=1, adsr=fast_release_adsr), 'Fast Release (0.2s)', 'cyan'),
        (DeviceConf(base_watt=3500, max_count=1, adsr=base_adsr), 'Normal Release (0.5s)', 'blue'),
        (DeviceConf(base_watt=3500, max_count=1, adsr=slow_release_adsr), 'Slow Release (2.0s)', 'magenta')
    ],
    [
        (DeviceConf(base_watt=3500, max_count=1, adsr=ADSRConf(a=3, d=2, s=0.8, r=0.5, wt='none', wp=2, wa=0.0)), 'No Wave', 'gray'),
        (DeviceConf(base_watt=3500, max_count=1, adsr=sine_wave_adsr), 'Sine Wave (15%)', 'blue'),
        (DeviceConf(base_watt=3500, max_count=1, adsr=square_wave_adsr), 'Square Wave (15%)', 'red')
    ]
]

titles = ['Attack Time Impact', 'Sustain Level Impact', 'Release Time Impact', 'Wave Modulation Impact']

fig, axes = plt.subplots(4, 1, figsize=(10, 12))
fig.suptitle('ADSR Parameter Impact on Device Load Curves', fontsize=14, fontweight='bold')

time = np.linspace(0.0, 30.0, 300)

for idx, (config_set, title) in enumerate(zip(configurations, titles)):
    ax = axes[idx]

    for device_conf, label, color in config_set:
        device = DeviceClass('HVAC')
        device.conf = device_conf

        power = np.array([device.calc_load(t) for t in time[time < 5.0]])
        device.toggle_envelope_state(0, 5)
        power = np.append(power, [device.calc_load(t) for t in time[(time >= 5.0) & (time < 15.0)]])
        device.toggle_envelope_state(0, 15)
        power = np.append(power, [device.calc_load(t) for t in time[(time >= 15.0) & (time < 25.0)]])
        device.toggle_envelope_state(0, 25)
        power = np.append(power, [device.calc_load(t) for t in time[time >= 25.0]])

        ax.plot(time, power, label=label, color=color, alpha=0.7)

    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlabel('Time [sec]')
    ax.set_ylabel('Power [W]')
    ax.legend()
    ax.grid(True, alpha=0.3, linestyle='--')

    ax.axvline(x=5, color='black', linestyle=':', alpha=0.7, label='Device On')
    ax.axvline(x=15, color='red', linestyle=':', alpha=0.7, label='Device Off')
    ax.axvline(x=25, color='black', linestyle=':', alpha=0.7, label='Device On')

plt.tight_layout(pad=2)
plt.show()
