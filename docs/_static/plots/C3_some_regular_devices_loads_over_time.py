from rsgp.houses_sim.device import DeviceClass
from rsgp.config.settings import settings

import matplotlib.pyplot as plt
import numpy as np

settings.TIME_FACTOR = 1.0

device_1 = DeviceClass('REFRIGERATOR')
device_2 = DeviceClass('HVAC')
device_3 = DeviceClass('MICROWAVE')
device_4 = DeviceClass('WATER_HEATER')

time = np.linspace(0.0, 50.0, 500)

power_1 = np.array([device_1.calc_load(t) for t in time[:50]])
power_2 = np.array([device_2.calc_load(t) for t in time[:50]])
power_3 = np.array([device_3.calc_load(t) for t in time[:50]])
power_4 = np.array([device_4.calc_load(t) for t in time[:50]])

device_1.toggle_envelope_state(0, time[50])
device_2.toggle_envelope_state(0, time[50])
device_3.toggle_envelope_state(0, time[50])
device_4.toggle_envelope_state(0, time[50])

power_1 = np.append(power_1, [device_1.calc_load(t) for t in time[50:450]])
power_2 = np.append(power_2, [device_2.calc_load(t) for t in time[50:450]])
power_3 = np.append(power_3, [device_3.calc_load(t) for t in time[50:450]])
power_4 = np.append(power_4, [device_4.calc_load(t) for t in time[50:450]])

device_1.toggle_envelope_state(0, time[450])
device_2.toggle_envelope_state(0, time[450])
device_3.toggle_envelope_state(0, time[450])
device_4.toggle_envelope_state(0, time[450])

power_1 = np.append(power_1, [device_1.calc_load(t) for t in time[450:]])
power_2 = np.append(power_2, [device_2.calc_load(t) for t in time[450:]])
power_3 = np.append(power_3, [device_3.calc_load(t) for t in time[450:]])
power_4 = np.append(power_4, [device_4.calc_load(t) for t in time[450:]])

plt.figure(figsize=(10, 6))
plt.title('Device Load Curves Over Time', fontsize=14, fontweight='bold')
plt.plot(time, power_1, label='Refrigerator')
plt.plot(time, power_2, label='HVAC')
plt.plot(time, power_3, label='Microwave')
plt.plot(time, power_4, label='Water Heater')
plt.xlabel('Time [Sec]')
plt.ylabel('Power [W]')
plt.grid(True)
plt.legend()
plt.tight_layout(pad=2)
plt.show()
