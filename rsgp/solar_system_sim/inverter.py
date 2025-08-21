from datetime import datetime

import pvlib

from .data import InverterConf, InverterMode, ChargePriority
from .panels import Panels
from .battery import Battery
from ..utils.remote_object import expose
from ..config.settings import settings


@expose
class Inverter:
    conf: InverterConf  #: InverterConf: The inverter configuration

    load_line: bool  #: bool: Flag for load line state (connected=1, disconnected=0)
    load_power: float  #: float: Total load for the system
    utility_line: bool  #: bool: Flag for utility line state (connected=1, disconnected=0)
    utility_exchange_power: float  #: float: Total power from/to the utility for the system
    panels_power: float  #: float: The power used by the solar panels [Watt]
    battery_exchange_power: float  #: float: The power exchanged with the battery (+ === charge, - === discharge) [Watt]

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

        self.load_line = True
        self.load_power = 0.0
        self.utility_line = True
        self.utility_exchange_power = 0.0
        self.panels_power = 0.0
        self.battery_exchange_power = 0.0

    def dc_to_ac(self, p_dc: float) -> float:
        if p_dc <= 0:
            return 0.0
        ac_power_calculated = pvlib.inverter.pvwatts(pdc=p_dc, pdc0=self.conf.pdco)
        actual_ac_power = max(0.0, min(float(ac_power_calculated), self.conf.paco))
        return actual_ac_power

    def ac_to_needed_dc(self, p_ac_target: float) -> float:
        if p_ac_target <= 0:
            return 0.0
        p_ac_target_capped = min(p_ac_target, self.conf.paco)
        p_dc_required = p_ac_target_capped / self.conf.eta_inv_ovr
        return p_dc_required

    def operate(self, timestamp: datetime, dt_seconds: float):
        initial_panels_dc_power = self._panels.calc_total_power(timestamp)
        required_load_dc_power = self.ac_to_needed_dc(
            self.conf.pnt + (self.load_power if self.load_line else 0))
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
            if required_load_dc_power > 0.0 and self.utility_line:
                imported_power = self.dc_to_ac(required_load_dc_power)
                self.utility_exchange_power = -1 * imported_power
                required_load_dc_power = 0.0
            return required_load_dc_power

        # You have to call clear on each step; power accumulates in this to allow for multiple steps to calculate the
        # import or export
        self.utility_exchange_power = 0.0
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
        if available_panels_dc_power > 0.0 and self.utility_line:
            ac_power_exported_to_utility = self.dc_to_ac(available_panels_dc_power)
            self.utility_exchange_power = ac_power_exported_to_utility
            available_panels_dc_power = 0.0

        # Store the actual power and used power
        self.panels_power = self._panels.total_power - available_panels_dc_power

        # Disconnect load if demand not met
        if required_load_dc_power > 0.0:
            self.load_line = False
            required_load_dc_power = 0.0

        # Charge battery from utility after all is said and done and store the exchange power of the battrey
        # The condition seems complex, here it is: it enters when the priority is UTILITY_OR_SOLAR, or when SOLAR_FIRST and solar
        # failed to charge. Of course, the utility line has to be connected as well.
        need_to_charge_from_utility = self.utility_line and (
            self.conf.charge_priority is ChargePriority.UTILITY_AND_SOLAR or
            self.conf.charge_priority is ChargePriority.SOLAR_FIRST and battery_exchange_power <= 0.0
        )

        if need_to_charge_from_utility:
            imported_power = self.dc_to_ac(self._battery.conf.max_charge_power)
            self.utility_exchange_power = -1 * imported_power
            battery_exchange_power += self._battery.charge(self._battery.conf.max_charge_power, dt_seconds)

        self.battery_exchange_power = battery_exchange_power

    def __str__(self):
        return f"Inverter(load_power={self.load_power:.3f}, utility_exchange_power={self.utility_exchange_power:.3f}, panels_power={self.panels_power:.3f}, battery_exchange_power={self.battery_exchange_power:.3f})"
