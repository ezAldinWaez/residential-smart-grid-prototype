"""Solar system simulated inverter."""

from datetime import datetime

import pvlib

from .data import InverterConf, InverterMode, ChargePriority
from .panels import Panels
from .battery import Battery
from ..remote_object import expose
from ..config.settings import settings


@expose
class UtilityInterface:
    """Utility interface for the inverter."""
    is_connected: bool  #: bool: The connection status of the utility
    exchange_power_ac: float  #: float: The total power exchanged with the utility (+ === export, - === import) [Watt]

    # TODO: do something with the exchange power; maybe to log and track it

    def __init__(self):
        self.is_connected = True
        self.exchange_power_ac = 0.0

    def get_connection_status(self) -> bool:
        return self.is_connected

    def set_connection_status(self, new_status: bool):
        self.is_connected = new_status

    def export_power(self, power_ac: float) -> None:
        self.exchange_power_ac += power_ac

    def import_power(self, power_ac: float) -> None:
        self.exchange_power_ac -= power_ac

    def clear_exchange_power(self) -> None:
        self.exchange_power_ac = 0.0

    def __str__(self):
        if self.is_connected:
            return "Utility interface is connected."
        else:
            return "Utility interface is disconnected."


@expose
class LoadInterface:
    """Load interface for the inverter."""
    is_connected: bool  #: bool: The connection status of the load
    system_load: float  #: float: The current system load [Watt]

    def __init__(self):
        self.is_connected = True
        self.system_load = 0.0

    def get_system_load(self) -> float:
        return self.system_load

    def set_system_load(self, system_load):
        self.system_load = system_load

    def get_connection_status(self) -> bool:
        return self.is_connected

    def set_connection_status(self, new_status: bool):
        self.is_connected = new_status

    def __str__(self):
        if self.is_connected:
            return "Load interface is connected"
        else:
            return "Load interface is disconnected"


@expose
class Inverter:
    """Solar system simulated inverter.

    Args:
        - battery (Battery): The battery object connected to the inverter
        - panels (Panels): The panels object connected to the inverter
    """

    conf: InverterConf  #: InverterConf: The inverter configuration
    utility_interface: UtilityInterface  #: UtilityInterface: The inverter utility interface
    load_interface: LoadInterface  #: LoadInterface: The inverter load interface
    cycle_used_solar: float  #: float: The power used by the solar panels [Watt]
    cycle_battery_exchange: float  #: float: The power exchanged with the battery (+ === charge, - === discharge) [Watt]

    def __init__(self, battery: Battery, panels: Panels):
        self.conf = InverterConf(
            paco=settings.INVERTER_NOMINAL_AC_POWER,
            pdco=settings.INVERTER_PDCO,
            pnt=settings.INVERTER_PNT,
            eta_inv_nom=settings.INVERTER_ETA_INV_NOM,
            eta_inv_ref=settings.INVERTER_ETA_INV_REF,
            eta_inv_ovr=settings.INVERTER_ETA_OVR,
            mode=settings.INVERTER_INIT_MODE,
            charge_priority=settings.INVERTER_INIT_CHARGE_PRIORITY
        )

        self._battery = battery
        self._panels = panels

        self.utility_interface = UtilityInterface()
        self.load_interface = LoadInterface()

        self.cycle_used_solar = 0.0
        self.cycle_battery_exchange = 0.0

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

    def operate(self, timestamp: datetime, dt_seconds: float):
        """Simulate the inverter's operation for a given time step.

        This method orchestrates the power flow within the solar system,
        considering the inverter's mode, charge priority, and the availability
        of solar power, battery charge, and utility connection.

        Args:
            - timestamp (datetime): The current simulation timestamp
            - dt_seconds (float): The time step duration in seconds
        """

        initial_panels_dc_power = self._panels.calc_total_power(timestamp)
        required_load_dc_power = self.ac_to_needed_dc(
            self.conf.pnt + (self.load_interface.system_load if self.load_interface.is_connected else 0))
        available_panels_dc_power = initial_panels_dc_power

        # Meet load from panels dc (S is for solar), convert it to ac, charge battery with the remaining
        def S(available_panels_dc_power: float, required_load_dc_power: float):
            battery_exchange_power = 0.0
            if available_panels_dc_power > 0:
                dc_to_inverter_for_load = min(available_panels_dc_power, required_load_dc_power)

                available_panels_dc_power -= dc_to_inverter_for_load
                required_load_dc_power -= dc_to_inverter_for_load

                # It is worth noting this will not change regardless of the charge priority of the battery
                if available_panels_dc_power > 0:
                    battery_exchange_power = self._battery.charge(available_panels_dc_power, dt_seconds)
                    available_panels_dc_power -= battery_exchange_power
            return available_panels_dc_power, required_load_dc_power, battery_exchange_power

        # Meet remaining load from battery (B is for battery)
        def B(required_load_dc_power: float):
            battery_exchange_power = 0.0
            if required_load_dc_power > 0.0:
                battery_exchange_power = self._battery.discharge(required_load_dc_power, dt_seconds)
                if battery_exchange_power > 0.0:
                    required_load_dc_power -= battery_exchange_power
            return required_load_dc_power, -1 * battery_exchange_power

        # Import from utility (U is for utility) to meet the demand
        def U(required_load_dc_power: float):
            if required_load_dc_power > 0.0 and self.utility_interface.is_connected:
                imported_power = self.dc_to_ac(required_load_dc_power)
                self.utility_interface.import_power(imported_power)
                required_load_dc_power = 0.0
            return required_load_dc_power

        # You have to call clear on each step; power accumulates in this to allow for multiple steps to calculate the
        # import or export
        self.utility_interface.clear_exchange_power()

        battery_exchange_power = 0.0

        if self.conf.mode is InverterMode.SBU:
            available_panels_dc_power, required_load_dc_power, battery_exchange_power = \
                S(available_panels_dc_power, required_load_dc_power)
            required_load_dc_power, battery_usage = \
                B(required_load_dc_power)
            required_load_dc_power = \
                U(required_load_dc_power)
        elif self.conf.mode is InverterMode.SUB:
            available_panels_dc_power, required_load_dc_power, battery_exchange_power = \
                S(available_panels_dc_power, required_load_dc_power)
            required_load_dc_power = \
                U(required_load_dc_power)
            required_load_dc_power, battery_usage = \
                B(required_load_dc_power)
        elif self.conf.mode is InverterMode.USB:
            required_load_dc_power = \
                U(required_load_dc_power)
            available_panels_dc_power, required_load_dc_power, battery_exchange_power = \
                S(available_panels_dc_power, required_load_dc_power)
            required_load_dc_power, battery_usage = \
                B(required_load_dc_power)
        else:
            raise ValueError(f"Invalid inverter mode: {self.conf.mode}")

        battery_exchange_power += battery_usage

        # Export remaining panels dc to utility after meeting all demands
        if available_panels_dc_power > 0.0 and self.utility_interface.is_connected:
            ac_power_exported_to_utility = self.dc_to_ac(available_panels_dc_power)
            self.utility_interface.export_power(ac_power_exported_to_utility)
            available_panels_dc_power = 0.0

        # Store the curtailed power and used power
        # TODO: do something with the curtalied power; maybe to log and track it
        self._panels.curtailed_power = available_panels_dc_power
        self.cycle_used_solar = initial_panels_dc_power - self._panels.curtailed_power

        # Disconnect load if demand not met
        if required_load_dc_power > 0.0:
            self.load_interface.set_connection_status(False)
            required_load_dc_power = 0.0

        # Charge battery from utility after all is said and done and store the exchange power of the battrey
        # The condition seems complex, here it is: it enters when the priority is UTILITY_OR_SOLAR, or when SOLAR_FIRST and solar
        # failed to charge. Of course, the utility line has to be connected as well.
        need_to_charge_from_utility = self.utility_interface.is_connected and (
            self.conf.charge_priority is ChargePriority.UTILITY_AND_SOLAR or
            self.conf.charge_priority is ChargePriority.SOLAR_FIRST and battery_exchange_power <= 0.0
        )

        if need_to_charge_from_utility:
            imported_power = self.dc_to_ac(self._battery.conf.max_charge_power)
            self.utility_interface.import_power(imported_power)
            battery_exchange_power += self._battery.charge(self._battery.conf.max_charge_power, dt_seconds)

        self.cycle_battery_exchange = battery_exchange_power

    def __str__(self):
        return (
            f"- Inverter:\n"
            f"\t- Configurations: {self.conf}\n"
            f"\t- Utility interface: {self.utility_interface}\n"
            f"\t- Load interface: {self.load_interface}\n"
            f"\t- Cycle used solar: {self.cycle_used_solar:.3f} Watt\n"
            f"\t- Cycle battery exchange: {self.cycle_battery_exchange:.3f} Watt"
        )
