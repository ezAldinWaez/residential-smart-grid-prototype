from rsgp.houses_sim.device import DeviceClass
from rsgp.houses_sim.data import ADSRConf, DeviceConf
from rsgp.config.settings import settings

import matplotlib.pyplot as plt
import numpy as np

settings.TIME_FACTOR = 1.0

# Create basic ADSR configuration
adsr = ADSRConf(a=2, d=3, s=0.7, r=4, wt='none', wp=1, wa=0.0)
device_conf = DeviceConf(base_watt=1000, max_count=1, adsr=adsr)

# Create device
device = DeviceClass('HVAC')
device.conf = device_conf

# Time array for 15 seconds
time = np.linspace(0.0, 15.0, 150)

# Calculate power values for each time point
power_values = []
device_turned_on = False
device_turned_off = False

for t in time:
    # Turn ON at t=1
    if t >= 1.0 and not device_turned_on:
        device.toggle_envelope_state(0, 1.0)
        device_turned_on = True

    # Turn OFF at t=10
    if t >= 10.0 and not device_turned_off:
        device.toggle_envelope_state(0, 10.0)
        device_turned_off = True

    power_values.append(device.calc_load(t))

power_values = np.array(power_values)

# Create the plot
plt.figure(figsize=(10, 6))
plt.plot(time, power_values, 'b-', linewidth=2.5, label='ADSR Envelope')
plt.fill_between(time, power_values, alpha=0.2, color='blue')

plt.axvline(x=1, color='green', linestyle='--', alpha=0.7, label='Device ON')
plt.axvline(x=10, color='red', linestyle='--', alpha=0.7, label='Device OFF')

# Simple phase labels
plt.text(2.0, 800, 'Attack', fontsize=11, ha='center')
plt.text(5.0, 870, 'Decay', fontsize=11, ha='center')
plt.text(7.5, 720, 'Sustain', fontsize=11, ha='center')
plt.text(12, 500, 'Release', fontsize=11, ha='center')

plt.title('ADSR Envelope: Attack-Decay-Sustain-Release', fontsize=14)
plt.xlabel('Time (seconds)')
plt.ylabel('Power (W)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
