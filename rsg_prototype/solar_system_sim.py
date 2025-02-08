"""Solar system simulation with battery."""

from dataclasses import dataclass
from datetime import datetime
import threading
import time
import os

import pvlib
from pvlib import irradiance

from .time_loc_sim import TimeLocSimulator


@dataclass
class PVConf:
    """PV configuration."""

    num_panels: int  #: int: Panels count.
    panel_area: float  #: float: Panel area. [m^2]
    panel_efficiency: float  #: float: Panel efficiency multiplier.

    def __str__(self):
        return "PVConf:\n" +\
            f"  panels count: {self.num_panels}\n" +\
            f"  panel area: {self.panel_area}\n" +\
            f"  panel efficiency: {self.panel_efficiency}"

    def __post_init__(self):
        assert self.num_panels > 0
        assert self.panel_area > 0
        assert 0 < self.panel_efficiency <= 1


@dataclass
class Battery:
    """Battery configuration and state."""

    capacity: float  #: float: Total capacity of the battery in Wh.
    charge_level: float  #: float: Current charge level of the battery in Wh.
    charge_efficiency: float  #: float: Efficiency of charging (0 to 1).
    max_charge_rate: float  #: float: Maximum charge rate in W.
    max_discharge_rate: float  #: float: Maximum discharge rate in W.

    def __post_init__(self):
        assert self.capacity > 0
        assert 0 <= self.charge_level <= self.capacity
        assert 0 < self.charge_efficiency <= 1
        assert self.max_charge_rate > 0
        assert self.max_discharge_rate > 0

    def charge(self, power: float, dt: float):
        """Charge the battery.

        Args:
            power (float): The power available for charging in W.
            dt (float): The time interval in seconds.

        Returns:
            float: The power actually used for charging.

        """
        available_power = min(power, self.max_charge_rate)
        energy_to_add = available_power * (dt / 3600) * self.charge_efficiency
        new_charge_level = self.charge_level + energy_to_add

        if new_charge_level > self.capacity:
            energy_to_add = self.capacity - self.charge_level
            self.charge_level = self.capacity
        else:
            self.charge_level = new_charge_level

        return energy_to_add * 3600 / dt  # Return the power actually used

    def discharge(self, power: float, dt: float):
        """Discharge the battery.

        Args:
            power (float): The power required in W.
            dt (float): The time interval in seconds.

        Returns:
            float: The power actually provided by the battery.

        """
        required_energy = power * (dt / 3600)
        available_energy = min(
            required_energy, min(self.max_discharge_rate, self.charge_level)
        )
        self.charge_level -= available_energy

        return available_energy * 3600 / dt  # Return the power actually provided

    def __str__(self):
        return f"Battery Configuration: \n" +\
            f"  Charge Efficiency: {self.charge_efficiency}\n" +\
            f"  Max Charge Rate: {self.max_charge_rate}\n" +\
            f"  Max Discharge Rate: {self.max_discharge_rate}\n" +\
            f"Battery State: {self.charge_level:.2f} / {self.capacity:.2f} Wh " +\
            f"({self.charge_level / self.capacity:.2%})"


class SolarSystemSimulator:
    """Solar system simulator."""

    pv_conf: PVConf  #: PVConf: The PV configuration for the system.

    #: Battery: The battery inctanse for the system.
    battery: Battery

    #: bool: Whether the simulation is running or paused.
    running: bool = False

    #: float: The current zenith angle for the sun.
    zenith_angle: float = .0

    #: float: ...
    poa_irradiance: float = .0

    #: float: The current power given by one panel.
    panel_power: float = .0

    #: float: The current total power given by the panels.
    total_power: float = .0

    #: pvlib.location.Location: The pvlib location instance.
    pv_loc: pvlib.location.Location

    def __init__(self, tls: TimeLocSimulator, pv_conf: PVConf, battery_conf: Battery, log=False):
        self._tls = tls
        self.pv_conf = pv_conf
        self.battery = battery_conf

        self.pv_loc = pvlib.location.Location(
            latitude=self._tls.loc_info.lat,
            longitude=self._tls.loc_info.lng,
            tz=self._tls.loc_info.tz_name,
            altitude=self._tls.loc_info.alt,
            name=self._tls.loc_name,
        )

        self._log = log
        if self._log:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self._log_fp = f"logs/{timestamp}/log_solar_system_sim_{timestamp}.csv"
            if not os.path.exists("logs"):
                os.mkdir("logs")
            if not os.path.exists(f"logs/{timestamp}"):
                os.mkdir(f"logs/{timestamp}")

    def start(self):
        """Start the simulation."""
        self.running = True

        if self._log:
            with open(self._log_fp, mode="w", encoding="utf-8") as f:
                f.write("elapsed,total_power\n")
                f.close()

        threading.Thread(
            target=self.update,
            kwargs={'dt': 100},
            daemon=True
        ).start()

    def pause(self):
        """Pause the simulation."""
        if self.running:
            self.running = False

    def resume(self):
        """Resume the simulation."""
        if not self.running:
            self.start()

    def update(self, dt: int):
        """Update the simulation every ``dt`` milliseconds.

        Args:
            dt (int): The number of milliseconds to update.

        """
        while self.running:
            elapsed = self._tls.get_elapsed()
            curr_time = self._tls.get_time(elapsed)

            # Get solar position (elevation and azimuth)
            solar_pos = self.pv_loc.get_solarposition(curr_time)

            # Calculate the solar zenith angle
            self.zenith_angle = solar_pos['zenith'].iloc[0]

            if self.zenith_angle > 90:
                self.poa_irradiance = 0
            else:
                # Use a simplified clear-sky model for daytime irradiance
                self.poa_irradiance = irradiance.get_total_irradiance(
                    surface_tilt=45,  # Assumed fixed tilt for simplicity
                    surface_azimuth=180,  # Facing south
                    solar_zenith=self.zenith_angle,  # Zenith angle from solar position
                    # Azimuth angle from solar position
                    solar_azimuth=solar_pos['azimuth'],
                    dni=1000,  # Direct normal irradiance (clear sky)
                    ghi=1000,  # Global horizontal irradiance (clear sky)
                    dhi=100,  # Diffuse horizontal irradiance
                    dni_extra=1367,  # Extra-terrestrial irradiance
                )['poa_global'].iloc[0]

            # Calculate the wattage output of each panel
            self.panel_power = self.poa_irradiance * self.pv_conf.panel_area * \
                self.pv_conf.panel_efficiency
            self.total_power = self.panel_power * self.pv_conf.num_panels

            if self._log:
                with open(self._log_fp, mode="a", encoding="utf-8") as f:
                    f.write(f"{elapsed:.2f},{self.total_power:.2f}\n")
                    f.close()

            time.sleep(dt/1000)
