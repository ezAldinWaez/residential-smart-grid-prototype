from rsgp.houses_sim.device import DeviceClass, RegularDevices
from rsgp.houses_sim.data import ADSRConf, DeviceConf
from rsgp.config.settings import settings

import matplotlib.pyplot as plt
import numpy as np

settings.TIME_FACTOR = 1.0

adsr = ADSRConf(a=5, d=10, s=0.7, r=4, wt='none', wp=1, wa=0.0)
device = DeviceClass('HVAC')
device.conf = DeviceConf(base_watt=1000, max_count=1, adsr=adsr)

time = np.linspace(0.0, 50.0, 500)

power = np.array([device.calc_load(t) for t in time[:50]])
device.toggle_envelope_state(0, time[50])
power = np.append(power, [device.calc_load(t) for t in time[50:400]])
device.toggle_envelope_state(0, time[400])
power = np.append(power, [device.calc_load(t) for t in time[400:]])

plt.figure(figsize=(10, 6))
plt.plot(time, power, 'b-', linewidth=2, label='ADSR Envelope')
plt.fill_between(time, power, alpha=0.2, color='blue')

plt.axvline(x=time[50], color='green', linestyle='--', label='Device ON')
plt.axvline(x=time[400], color='red', linestyle='--', label='Device OFF')

plt.text(
    x=time[50]+adsr.a/2,
    y=np.average(power[50:50+10*adsr.a]),
    rotation=np.degrees(np.arctan((power[50+10*adsr.a] - power[50]) / (time[50+10*adsr.a] - time[50]))),
    s='Attack', fontsize=11, ha='center', transform_rotates_text=True, rotation_mode='anchor')
plt.text(
    x=time[50]+adsr.a+adsr.d/2,
    y=np.average(power[50+10*adsr.a:50+10*(adsr.a+adsr.d)]),
    rotation=np.degrees(np.arctan((power[50+10*(adsr.a+adsr.d)] - power[50+10*adsr.a]) / (time[50+10*(adsr.a+adsr.d)] - time[50+10*adsr.a]))),
    s='Decay', fontsize=11, ha='center', transform_rotates_text=True, rotation_mode='anchor')
plt.text(
    x=time[50]+adsr.a+adsr.d+(time[400]-(time[50]+adsr.a+adsr.d))/2,
    y=adsr.s * device.conf.base_watt,
    s='Sustain', fontsize=11, ha='center')
plt.text(
    x=time[400]+adsr.r/2,
    y=np.average(power[400:400+10*adsr.r]),
    rotation=np.degrees(np.arctan((power[400+10*adsr.r] - power[400]) / (time[400+10*adsr.r] - time[400]))),
    s='Release', fontsize=11, ha='center', transform_rotates_text=True, rotation_mode='anchor',
    )

plt.title('ADSR Envelope: Attack-Decay-Sustain-Release', fontsize=14, fontweight='bold')
plt.xlabel('Time [sec]')
plt.ylabel('Power [W]')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout(pad=2)
plt.show()
