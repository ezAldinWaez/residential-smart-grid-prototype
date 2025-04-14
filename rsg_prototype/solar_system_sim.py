"""Solar system simulation with battery."""

from dataclasses import dataclass
from datetime import datetime
import threading
import time
import os

import pandas as pd
import pvlib

from .time_sim import TimeSimulator


@dataclass
class PVConf:
    """PV configuration."""

    num_panels: int  #: int: Panels count.
    panel_area: float  #: float: Panel area. [m^2]
    panel_efficiency: float  #: float: Panel efficiency multiplier.

    def __str__(self):
        return "PV Configuration:\n" +\
            f"  Panels Count: {self.num_panels}\n" +\
            f"  Panel Area: {self.panel_area}\n" +\
            f"  Panel Efficiency: {self.panel_efficiency}"

    def __post_init__(self):
        assert self.num_panels > 0
        assert self.panel_area > 0
        assert 0 < self.panel_efficiency <= 1


@dataclass
class BattConf:
    """Battery configuration."""

    capacity: float  #: float: Total capacity of the battery. [Wh]
    charge_efficiency: float  #: float: Efficiency of charging. [%]
    max_charge_power: float  #: float: Maximum charge rate. [W]
    max_discharge_power: float  #: float: Maximum discharge rate. [W]

    def __post_init__(self):
        assert self.capacity > 0
        assert 0 < self.charge_efficiency <= 1
        assert self.max_charge_power > 0
        assert self.max_discharge_power > 0

    def __str__(self):
        return "Battery Configuration:\n" +\
            f"  capacity: {self.capacity}\n" +\
            f"  charge_efficiency: {self.charge_efficiency}\n" +\
            f"  max_charge_power: {self.max_charge_power}\n" +\
            f"  max_discharge_power: {self.max_discharge_power}"


class BattState:
    """Battery state that holds the battery status.

    Args:
        conf (BattConf): The battery configuration.
        init_charge_level_multiplier (float): The initialized charge level for the battery.

    """

    conf: BattConf  #: BattConf: The battery configuration.
    charge_level: float  #: float: Current charge level of the battery in Wh.

    def __init__(self, conf: BattConf, init_charge_level_multiplier: float):
        assert 0 <= init_charge_level_multiplier <= 1

        self.conf = conf
        self.charge_level = self.conf.capacity * init_charge_level_multiplier

    def charge(self, power: float, time: float) -> float:
        """Charge the battery.

        Args:
            power (float): The power available for charging. [W]
            time (float): The time interval. [sim_sec]

        Returns:
            float: The power actually used for charging. [W]

        """
        charge_power = min(power, self.conf.max_charge_power)
        charge_power *= self.conf.charge_efficiency
        charge_energy = charge_power * (time / 3600)

        energy_to_full = self.conf.capacity - self.charge_level
        actual_charge_energy = min(charge_energy, energy_to_full)
        self.charge_level += actual_charge_energy

        actual_charge_power = actual_charge_energy * (3600 / time)
        actual_charge_power /= self.conf.charge_efficiency
        return actual_charge_power

    def discharge(self, power: float, time: float) -> float:
        """Discharge the battery.

        Args:
            power (float): The power required. [W]
            time (float): The time interval. [sim_sec]

        Returns:
            float: The power actually provided by the battery.

        """
        discharge_power = min(power, self.conf.max_discharge_power)
        discharge_power /= self.conf.charge_efficiency
        discharge_energy = discharge_power * (time / 3600)

        actual_discharge_energy = min(discharge_energy, self.charge_level)
        self.charge_level -= actual_discharge_energy

        actual_discharge_power = actual_discharge_energy * (3600 / time)
        actual_discharge_power *= self.conf.charge_efficiency
        return actual_discharge_power

    def __str__(self):
        return f"Battery State: {self.charge_level:.2f} / {self.conf.capacity:.2f} Wh " +\
            f"({self.charge_level / self.conf.capacity:.2%})"


class SolarSystemSimulator:
    """Solar system simulator.

    Args:
        ts (TimeSimulator): Time simulator instance.
        pv_conf (PVConf): PV configuration.
        batt_conf (BattConf): Battery configuration.
        nsrdb_data (DataFrame): ....
        log (bool): If True, an csv file will be created and record the system status.

    """

    pv_conf: PVConf  #: PVConf: The PV configuration for the system.
    #: BattState: The battery state for the system.
    batt: BattState
    #: bool: Whether the simulation is running or paused.
    running: bool = False
    zenith_angle: float = .0  #: float: The current zenith angle for the sun.
    poa_irradiance: float = .0  #: float: ...
    #: float: The current power given by one panel.
    panel_power: float = .0
    #: float: The current total power given by the panels.
    total_power: float = .0
    pv_loc: pvlib.location.Location  #: Location: The pvlib location instance.
    nsrdb_data: pd.DataFrame  #: DataFrame: ...

    def __init__(self, ts: TimeSimulator, pv_conf: PVConf, batt_conf: BattConf, nsrdb_data: pd.DataFrame, log=False):
        self._ts = ts
        self.pv_conf = pv_conf

        self.pv_loc = pvlib.location.Location(
            latitude=ts.location['lat'],
            longitude=ts.location['lng'],
            tz=ts.location['tz'],
        )

        self.batt = BattState(
            conf=batt_conf,
            init_charge_level_multiplier=.5,
        )

        self.nsrdb_data = nsrdb_data

        self._log = log
        if self._log:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self._log_fp = f"logs/{timestamp}/log_solar_system_sim_{timestamp}.csv"
            if not os.path.exists("logs"):
                os.mkdir("logs")
            if not os.path.exists(f"logs/{timestamp}"):
                os.mkdir(f"logs/{timestamp}")

    def start(self, dt: int = None):
        """Start the simulation.

        Args:
            dt (int): Update time. [millisecond] 

        """
        self.running = True

        if not dt:
            dt = self._dt

        self._dt = dt

        if self._log:
            with open(self._log_fp, mode="w", encoding="utf-8") as f:
                f.write("elapsed,total_power\n")
                f.close()

        threading.Thread(
            target=self.update,
            kwargs={'dt': dt},
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
            current_timestamp = self._ts.get_time()
            data = find_nearest_timestamp_row(
                self.nsrdb_data, current_timestamp)

            elapsed = self._ts.get_elapsed()
            curr_time = self._ts.get_time(elapsed)

            solar_pos = self.pv_loc.get_solarposition(curr_time)

            self.zenith_angle = data['Solar Zenith Angle']

            if self.zenith_angle > 90:
                self.poa_irradiance = 0
            else:
                self.poa_irradiance = pvlib.irradiance.get_total_irradiance(
                    surface_tilt=35,
                    surface_azimuth=180,
                    solar_zenith=data['Solar Zenith Angle'],
                    solar_azimuth=solar_pos['azimuth'],
                    dni=data['DNI'],
                    ghi=data['GHI'],
                    dhi=data['DHI'],
                )['poa_global'].iloc[0]

            self.panel_power = self.poa_irradiance * self.pv_conf.panel_area * \
                self.pv_conf.panel_efficiency
            self.total_power = self.panel_power * self.pv_conf.num_panels

            if self._log:
                with open(self._log_fp, mode="a", encoding="utf-8") as f:
                    f.write(f"{elapsed:.2f},{self.total_power:.2f}\n")
                    f.close()

            time.sleep(dt/1000)


def find_nearest_timestamp_row(df, target_timestamp):
    """Find the row in DataFrame with timestamp closest to the target timestamp.

    Args:
        df: pandas DataFrame with 'Timestamp' column
        target_timestamp: pandas Timestamp or datetime-like object to search for

    Returns:
        Series: The row from df with nearest timestamp
    """

    target_ts = pd.to_datetime(target_timestamp)
    time_diffs = (df['Timestamp'] - target_ts).abs()
    nearest_idx = time_diffs.idxmin()
    return df.loc[nearest_idx]
