import matplotlib.pyplot as plt
import numpy as np

from rsgp.houses_sim.device import DeviceClass
from rsgp.config.settings import settings

settings.TIME_FACTOR = 1.0

device_1 = DeviceClass('REFRIGERATOR')
device_2 = DeviceClass('HVAC')
device_3 = DeviceClass('MICROWAVE')
device_4 = DeviceClass('WATER_HEATER')


device_1.toggle_envelope_state(0, 0.0)
device_2.toggle_envelope_state(0, 0.0)
device_3.toggle_envelope_state(0, 0.0)
device_4.toggle_envelope_state(0, 0.0)

time = np.linspace(0.0, 50.0, 500)

power_1 = np.array([device_1.calc_load(elapsed) for elapsed in time[:-100]])
power_2 = np.array([device_2.calc_load(elapsed) for elapsed in time[:-100]])
power_3 = np.array([device_3.calc_load(elapsed) for elapsed in time[:-100]])
power_4 = np.array([device_4.calc_load(elapsed) for elapsed in time[:-100]])

device_1.toggle_envelope_state(0, time[-100])
device_2.toggle_envelope_state(0, time[-100])
device_3.toggle_envelope_state(0, time[-100])
device_4.toggle_envelope_state(0, time[-100])

power_1 = np.append(power_1, [device_1.calc_load(elapsed) for elapsed in time[-100:]])
power_2 = np.append(power_2, [device_2.calc_load(elapsed) for elapsed in time[-100:]])
power_3 = np.append(power_3, [device_3.calc_load(elapsed) for elapsed in time[-100:]])
power_4 = np.append(power_4, [device_4.calc_load(elapsed) for elapsed in time[-100:]])

plt.figure(figsize=(10, 6))
plt.plot(time, power_1, label='Refrigerator')
plt.plot(time, power_2, label='HVAC')
plt.plot(time, power_3, label='Microwave')
plt.plot(time, power_4, label='Water Heater')
plt.xlabel('Time [Sec]')
plt.ylabel('Power [Watt]')
plt.grid(True)
plt.legend()
plt.show()
