from rsgp.utils.nsrdb_data import nsrdb_data

import matplotlib.pyplot as plt
import numpy as np

daily_ghi_max = nsrdb_data.groupby(nsrdb_data['Timestamp'].dt.date)['GHI'].max()
clear_day_date = daily_ghi_max.idxmax()  # Date with highest peak GHI

clear_day_data = nsrdb_data[nsrdb_data['Timestamp'].dt.date == clear_day_date].copy()
clear_day_data = clear_day_data.sort_values('Timestamp')

clear_day_data['Hour'] = clear_day_data['Timestamp'].dt.hour + clear_day_data['Timestamp'].dt.minute / 60.0

hours = clear_day_data['Hour'].values
dni = clear_day_data['DNI'].values
dhi = clear_day_data['DHI'].values
ghi = clear_day_data['GHI'].values
zenith_angle = clear_day_data['Solar Zenith Angle'].values

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
fig.suptitle('Solar Irradiance and Solar Position for a Clear Day', fontsize=14, fontweight='bold')


# Plot 1: Irradiance components throughout the day
ax1.plot(hours, dni, 'r-', linewidth=2.5, label='DNI (Direct Normal)')
ax1.plot(hours, dhi, 'b-', linewidth=2.5, label='DHI (Diffuse Horizontal)')
ax1.plot(hours, ghi, 'g-', linewidth=2.5, label='GHI (Global Horizontal)')
ax1.fill_between(hours, dni, alpha=0.2, color='red', label='DNI Area')
ax1.fill_between(hours, dhi, alpha=0.2, color='blue', label='DHI Area')

ax1.set_xlabel('Hour of Day')
ax1.set_ylabel('Irradiance [W/m²]')
ax1.set_title(f'Solar Irradiance Components - {clear_day_date}', fontsize=12, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)

ax1.set_ylim(0, max(np.max(dni), np.max(ghi)) * 1.1)

# Plot 2: GHI verification and solar zenith angle
ax2_twin = ax2.twinx()

ax2.plot(hours, ghi, 'g-', linewidth=2.5, label='GHI (Measured)')
ax2.fill_between(hours, ghi, alpha=0.2, color='green')

ax2_twin.plot(hours, zenith_angle, 'orange', linewidth=2, alpha=0.8, label='Solar Zenith Angle')
ax2_twin.axhline(y=90, color='orange', linestyle=':', alpha=0.7, label='90° (Horizon)')

ax2.set_xlabel('Hour of Day')
ax2.set_ylabel('Irradiance [W/m²]', color='green')
ax2_twin.set_ylabel('Solar Zenith Angle [°]', color='orange')
ax2.set_title('GHI Verification & Solar Position', fontsize=12, fontweight='bold')

lines1, labels1 = ax2.get_legend_handles_labels()
lines2, labels2 = ax2_twin.get_legend_handles_labels()
ax2.legend(lines1 + lines2, labels1 + labels2)

ax2.grid(True, alpha=0.3)
ax2.set_ylim(0, np.max(ghi) * 1.1)
ax2_twin.set_ylim(0, 100)

# Color coordinate the y-axis labels
ax2.tick_params(axis='y', labelcolor='green')
ax2_twin.tick_params(axis='y', labelcolor='orange')

plt.tight_layout(pad=2)
plt.show()
