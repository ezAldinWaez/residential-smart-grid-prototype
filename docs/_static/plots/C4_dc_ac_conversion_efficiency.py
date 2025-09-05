from rsgp.solar_system_sim.inverter import Inverter
from rsgp.solar_system_sim.panels import Panels
from rsgp.solar_system_sim.battery import Battery

import matplotlib.pyplot as plt
import numpy as np

battery = Battery()
panels = Panels()
inverter = Inverter(battery=battery, panels=panels)

paco = inverter.conf.paco
pdco = inverter.conf.pdco
eta_inv_nom = inverter.conf.eta_inv_nom

p_dc_range = np.linspace(1, pdco + 1000, 1000)

p_ac_pvwatts = np.array([
    inverter.dc_to_ac(p_dc)
    for p_dc in p_dc_range])
p_ac_linear = np.array([
    min(p_dc * eta_inv_nom, paco) if p_dc > 0 else 0.0
    for p_dc in p_dc_range])
efficiency_pvwatts = np.array([
    (p_ac_pvwatts[idx] / p_dc) * 100 if p_dc > 0 else 0.0
    for idx, p_dc in enumerate(p_dc_range)])
efficiency_linear = np.array([
    (p_ac_linear[idx] / p_dc) * 100 if p_dc > 0 else 0.0
    for idx, p_dc in enumerate(p_dc_range)])

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
fig.suptitle('Inverter DC-AC Conversion and Efficiency', fontsize=14, fontweight='bold')

# Plot 1: Power conversion curves
ax1.plot(p_dc_range, p_ac_pvwatts, 'b-', linewidth=2, label='PVWatts Model')
ax1.plot(p_dc_range, p_ac_linear, 'g--', linewidth=2, alpha=0.7, label=f'Ideal Linear (η={eta_inv_nom:.3f})')
ax1.axhline(y=paco, color='red', linestyle='--', alpha=0.7, label=f'AC Rating ({paco/1000:.0f} kW)')
ax1.axvline(x=pdco, color='orange', linestyle='--', alpha=0.7, label=f'DC Rating ({pdco/1000:.0f} kW)')

ax1.set_xlabel('DC Power Input [W]')
ax1.set_ylabel('AC Power Output [W]')
ax1.set_title('DC-to-AC Power Conversion', fontsize=12, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_xlim(1, pdco + 1000)

# Plot 2: Efficiency comparison
ax2.plot(p_dc_range, efficiency_pvwatts, 'b-', linewidth=2, label='PVWatts Efficiency')
ax2.plot(p_dc_range, efficiency_linear, 'g--', linewidth=2, alpha=0.7, label='Linear Efficiency')
ax2.axhline(
    y=eta_inv_nom * 100, color='red', linestyle='--', alpha=0.7,
    label=f'Nominal Efficiency ({eta_inv_nom:.1%})')

ax2.set_xlabel('DC Power Input [W]')
ax2.set_ylabel('Conversion Efficiency [%]')
ax2.set_title('Efficiency Comparison', fontsize=12, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_xlim(1, pdco + 1000)
ax2.set_ylim(0, 100)

plt.tight_layout(pad=2)
plt.show()
