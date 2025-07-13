"""Solar system simulated inverter."""

from datetime import datetime
import pvlib

from .data import InverterConf
from .battery import Battery
from .panels import Panels
from ..config.settings import settings


class Inverter:
    """
    Solar system simulated inverter.

    Args:
        - battery (Battery): The battery instance
        - panels (Panels): The panels instance
        - initial_grid_status (bool): The initial grid connection status
    """
    conf: InverterConf  #: InverterConf: The inverter configuration
    battery: Battery  #: Battery: The battery instance
    panels: Panels  #: Panels: The panels instance
    is_grid_connected: bool  #: bool: Flag indicating if the inverter is connected to the utility grid

    def __init__(self, battery: Battery, panels: Panels, initial_grid_status: bool = True):
        self.conf = InverterConf(
            paco=settings.INVERTER_NOMINAL_AC_POWER,
            pdco=settings.INVERTER_PDCO,
            pnt=settings.INVERTER_PNT,
            eta_inv_nom=settings.INVERTER_ETA_INV_NOM,
            eta_inv_ref=settings.INVERTER_ETA_INV_REF,
            eta_inv_ovr=settings.INVERTER_ETA_OVR,
        )

        self.battery = battery
        self.panels = panels
        self.is_grid_connected = initial_grid_status

    def set_grid_status(self, is_connected: bool):
        """Allows external control over the grid connection status."""
        self.is_grid_connected = is_connected

    def dc_to_ac(self, p_dc: float) -> float:
        """
        Calculates the AC power produced from a given DC input power.

        Uses the `pvlib.inverter.pvwatts` model.

        Args:
            p_dc (float): DC power available to the inverter [Watt]

        Returns:
            float: AC power produced [Watt], capped at `self.Paco`
        """
        if p_dc <= 0:
            return 0.0
        ac_power_calculated = pvlib.inverter.pvwatts(pdc=p_dc, pdc0=self.conf.pdco)
        actual_ac_power = max(0.0, min(float(ac_power_calculated), self.conf.paco))
        return actual_ac_power

    def ac_to_needed_dc(self, p_ac_target: float) -> float:
        """
        Calculates the DC power required to produce a target AC output power.

        Uses the simplified `eta_inv_ovr` efficiency factor for this reverse calculation.

        Args:
            p_ac_target (float): Target AC output power [Watt]

        Returns:
            float: Required DC input power [Watt]
        """
        if p_ac_target <= 0:
            return 0.0
        p_ac_target_capped = min(p_ac_target, self.conf.paco)
        p_dc_required = p_ac_target_capped / self.conf.eta_inv_ovr
        return p_dc_required

    def get_night_consumption(self) -> float:
        """
        Returns the night consumption of the inverter.

        The inverter actually consume that power all the opration time.

        Returns:
            float: Night consumption [Watt]
        """
        return self.conf.pnt

    def work(self, timestamp: datetime, dt_seconds: float, system_load: float):
        available_panels_dc_power = self.panels.calc_total_power(timestamp)
        required_load_ac_power = system_load + self.get_night_consumption()

        # Meet load from panels dc, convert it to ac, and charge battery with the remaining
        if available_panels_dc_power > 0:
            dc_to_inverter_for_load = min(
                available_panels_dc_power,
                self.ac_to_needed_dc(required_load_ac_power)
            )

            ac_supplied_to_load_from_panels = self.dc_to_ac(dc_to_inverter_for_load)
            available_panels_dc_power -= dc_to_inverter_for_load
            required_load_ac_power -= ac_supplied_to_load_from_panels

            if available_panels_dc_power > 0:
                available_panels_dc_power -= self.battery.charge(available_panels_dc_power, dt_seconds)

        # Meet remaining load from battery
        if required_load_ac_power > 0.0:
            needed_dc_from_batt = self.ac_to_needed_dc(required_load_ac_power)
            dc_from_batt = self.battery.discharge(needed_dc_from_batt, dt_seconds)
            if dc_from_batt > 0.0:
                required_load_ac_power -= self.dc_to_ac(dc_from_batt)

        # Export remaining panels dc to grid after meeting all demands
        if available_panels_dc_power > 0.0 and self.is_grid_connected:
            # TODO: Export extra power to the grid
            # ac_power_exported_to_grid = self.dc_to_ac(available_panels_dc_power)
            # self.grid.export(ac_power_exported_to_grid)
            available_panels_dc_power = 0.0

        # Store the curtailed power
        self.panels.curtailed_power = available_panels_dc_power

        # TODO: Meet the load from grid (bypassing), or break if not connected to grid.
        if required_load_ac_power > 0.0:
            if self.is_grid_connected:
                pass
            else:
                pass


    def __str__(self):
        return (
            f"Inverter Status:\n"
            f"- Grid status: {self.is_grid_connected}"
        )
