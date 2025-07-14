"""Solar system simulated inverter."""

from datetime import datetime
import os
import pvlib


from .data import InverterConf
from .battery import Battery
from .panels import Panels
from .utility import Utility
from .load import Load
from ..config.settings import settings
from ..utils.remote_interface import remote_interface_expose


@remote_interface_expose
class Inverter:
    """
    Solar system simulated inverter.

    Args:
        - battery (Battery): The battery instance
        - panels (Panels): The panels instance
        - utility (Utility): The utility instance
        - load (Load): The load instance
    """
    conf: InverterConf  #: InverterConf: The inverter configuration
    battery: Battery  #: Battery: The battery instance
    panels: Panels  #: Panels: The panels instance
    utility: Utility  #: Utility: The utility instance
    load: Load  #: Load: The load instance

    def __init__(self, battery: Battery, panels: Panels, utility: Utility, load: Load):
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
        self.utility = utility
        self.load = load

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

    def work(self, timestamp: datetime, dt_seconds: float):
        """_summary_

        Args:
            timestamp (datetime): _description_
            dt_seconds (float): _description_
        """
        available_panels_dc_power = self.panels.calc_total_power(timestamp)
        required_load_dc_power = self.ac_to_needed_dc(
            self.load.system_load + self.get_night_consumption()
        )


        # Meet load from panels dc, convert it to ac, and charge battery with the remaining
        if available_panels_dc_power > 0:
            dc_to_inverter_for_load = min(
                available_panels_dc_power,
                required_load_dc_power
            )

            available_panels_dc_power -= dc_to_inverter_for_load
            required_load_dc_power -= dc_to_inverter_for_load

            if available_panels_dc_power > 0:

                available_panels_dc_power -= self.battery.charge(available_panels_dc_power, dt_seconds)

        # Meet remaining load from battery USB/SUB/SBU - Solar First/Solar Only/Solar+Utility
        if required_load_dc_power > 0.0:

            dc_from_batt = self.battery.discharge(required_load_dc_power, dt_seconds)
            if dc_from_batt > 0.0:

                required_load_dc_power -= dc_from_batt

        # Export remaining panels dc to utility after meeting all demands
        if available_panels_dc_power > 0.0 and self.utility.is_connected:

            # TODO: Export extra power to the utility
            ac_power_exported_to_utility = self.dc_to_ac(available_panels_dc_power)
            self.utility.export_power(ac_power_exported_to_utility)
            available_panels_dc_power = 0.0

        # Store the curtailed power
        self.panels.curtailed_power = available_panels_dc_power

        # TODO: Meet the load from utility (bypassing), or break if not connected to utility.
        if required_load_dc_power > 0.0:

            if self.utility.is_connected:
                imported_power = self.dc_to_ac(required_load_dc_power)
                self.utility.import_power(imported_power)
            else:
                self.load.set_connection_status(False)
                required_load_dc_power = 0

    def __str__(self):
        return (
            f"Inverter Status:\n"
            f"- Utility status: {self.utility.is_connected}"
        )
