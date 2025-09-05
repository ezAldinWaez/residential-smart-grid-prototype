"""Solar system simulation inverter."""

from datetime import datetime, timedelta

from .data import InverterConf, InverterMode, ChargePriority
from .panels import Panels
from .battery import Battery
from ..config.settings import settings

from Pyro5.api import expose
import pvlib


@expose
class Inverter:
    """Inverter.

    Args:
        battery (Battery): The battery object.
        panels (Panels): The panels object.

    """

    conf: InverterConf  #: InverterConf: The inverter configuration.
    load_line: bool  #: bool: Flag for load line state (connected=1, disconnected=0).
    load_power: float  #: float: Total load for the system.
    utility_line: bool  #: bool: Flag for utility line state (connected=1, disconnected=0).
    #: float: Total power from/to the utility for the system (+ === export, - === import).
    utility_exchange_power: float
    panels_power: float  #: float: The power used by the solar panels [Watt].
    #: float: The power exchanged with the battery (+ === charge, - === discharge) [Watt].
    battery_exchange_power: float

    def __init__(self, battery: Battery, panels: Panels) -> None:
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

        self._load_reconnection_time = None

    def dc_to_ac(self, p_dc: float) -> float:
        """Convert DC power to AC power using the inverter's characteristics.

        Args:
            p_dc (float): DC power input to the inverter [Watt].

        Returns:
            float: AC power output from the inverter [Watt]. 

        """
        if p_dc <= 0:
            return 0.0
        ac_power_calculated = pvlib.inverter.pvwatts(
            pdc=p_dc,
            pdc0=self.conf.pdco,
            eta_inv_nom=self.conf.eta_inv_nom,
            eta_inv_ref=self.conf.eta_inv_ref
        )
        actual_ac_power = max(0.0, min(float(ac_power_calculated), self.conf.paco))
        return actual_ac_power

    def ac_to_needed_dc(self, p_ac_target: float) -> float:
        """Convert a target AC power output to the required DC power input for the inverter.

        Args:
            p_ac_target (float): The target AC power output from the inverter [Watt].

        Returns:
            float: The required DC power input to the inverter [Watt].
        """

        if p_ac_target <= 0:
            return 0.0
        p_ac_target_capped = min(p_ac_target, self.conf.paco)
        p_dc_required = p_ac_target_capped / self.conf.eta_inv_ovr
        return p_dc_required

    def operate(self, timestamp: datetime, dt_seconds: float) -> None:
        """Calculate the power flow in the solar system for the given time interval.

        It calculates the power flow in the solar system based on the current timestamp and time
        interval. It determines how power is distributed among the load, battery, solar panels,
        and utility grid, adhering to the inverter's operational mode and charge priority
        settings.

        The power flow is calculated in DC, then converted to AC where needed, with the inverter's
        efficiency taken into account.

        The :func:`_S`, :func:`_B`, and :func:`_U` helper functions encapsulate the logic for sourcing power from
        solar, battery, and utility respectively. They return the remaining power needs or
        surpluses after their operation.

        The ``battery_exchange_power`` and ``utility_exchange_power`` are reset at the beginning of
        each :func:`operate` call to ensure calculations are based on the current time step. The final
        ``battery_exchange_power`` is the sum of all battery charge/discharge events during the
        current operational cycle.

        If there's any remaining ``available_panels_dc_power`` after meeting all demands and the
        utility line is connected, this surplus power is exported to the utility.

        If ``required_load_dc_power`` is still greater than zero after all power sources have been
        considered, it means the load could not be fully met, and the ``load_line`` is
        disconnected.

        Finally, if the battery needs charging from the utility based on the ``charge_priority``
        settings, it charges the battery from the utility.

        Args:
            timestamp (datetime): The current timestamp.
            dt_seconds (float): The time interval in seconds.

        """
        initial_panels_dc_power = self._panels.calc_total_power(timestamp)
        required_load_dc_power = self.ac_to_needed_dc(
            self.conf.pnt + (self.load_power if self.load_line else 0))
        available_panels_dc_power = initial_panels_dc_power

        def _S(available_panels_dc_power: float, required_load_dc_power: float) -> tuple[float, float, float]:
            """Meet load from panels dc (S is for solar), convert it to ac, charge battery with the remaining.

            Args:
                available_panels_dc_power (float): The current DC power available from panels [Watt].
                required_load_dc_power (float): The DC power required by the load [Watt].

            Returns:
                tuple[float, float, float]: A tuple containing:

                    - **remaining_panels_dc_power** (*float*): Solar power left after meeting load and charging battery [Watt].
                    - **remaining_load_dc_power** (*float*): Load power still needed after solar contribution [Watt].
                    - **battery_charge_power** (*float*): Power used to charge the battery from solar [Watt].

            """
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

        def _B(required_load_dc_power: float) -> tuple[float, float]:
            """Meet remaining load from battery (B is for battery).

            Args:
                required_load_dc_power (float): The DC power required by the load [Watt].

            Returns:
                tuple[float, float]: A tuple containing:

                    - required_load_dc_power (float): Load power still needed after battery contribution [Watt].
                    - battery_exchange_power (float): Power used to discharge the battery to meet load [Watt].

            """
            battery_exchange_power = 0.0
            if required_load_dc_power > 0.0:
                battery_exchange_power = self._battery.discharge(required_load_dc_power, dt_seconds)
                if battery_exchange_power > 0.0:
                    required_load_dc_power -= battery_exchange_power
            return required_load_dc_power, -battery_exchange_power

        def _U(required_load_dc_power: float) -> float:
            """Import from utility (U is for utility) to meet the demand.

            Args:
                required_load_dc_power (float): The DC power required by the load [Watt].

            Returns:
                float: Load power still needed after utility contribution [Watt].

            """
            if required_load_dc_power > 0.0 and self.utility_line:
                imported_power = self.dc_to_ac(required_load_dc_power)
                self.utility_exchange_power = -imported_power
                required_load_dc_power = 0.0
            return required_load_dc_power

        # You have to call clear on each step; power accumulates in this to allow for multiple steps to calculate the
        # import or export
        self.utility_exchange_power = 0.0
        battery_exchange_power = 0.0

        if self.conf.mode is InverterMode.SBU:
            available_panels_dc_power, required_load_dc_power, battery_exchange_power = \
                _S(available_panels_dc_power, required_load_dc_power)
            required_load_dc_power, battery_usage = \
                _B(required_load_dc_power)
            required_load_dc_power = \
                _U(required_load_dc_power)
        elif self.conf.mode is InverterMode.SUB:
            available_panels_dc_power, required_load_dc_power, battery_exchange_power = \
                _S(available_panels_dc_power, required_load_dc_power)
            required_load_dc_power = \
                _U(required_load_dc_power)
            required_load_dc_power, battery_usage = \
                _B(required_load_dc_power)
        elif self.conf.mode is InverterMode.USB:
            required_load_dc_power = \
                _U(required_load_dc_power)
            available_panels_dc_power, required_load_dc_power, battery_exchange_power = \
                _S(available_panels_dc_power, required_load_dc_power)
            required_load_dc_power, battery_usage = \
                _B(required_load_dc_power)
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
            self._load_reconnection_time = timestamp + timedelta(seconds=settings.INVERTER_LOAD_RECONNECTION_INTERVAL)

        # Charge battery from utility after all is said and done and store the exchange power of the battrey
        # The condition seems complex, here it is: it enters when the priority is UTILITY_OR_SOLAR, or when SOLAR_FIRST and solar
        # failed to charge. Of course, the utility line has to be connected as well.
        need_to_charge_from_utility = self.utility_line and (
            self.conf.charge_priority is ChargePriority.UTILITY_AND_SOLAR or
            self.conf.charge_priority is ChargePriority.SOLAR_FIRST and battery_exchange_power <= 0.0
        )

        if need_to_charge_from_utility:
            imported_power = self.dc_to_ac(self._battery.conf.max_charge_power)
            self.utility_exchange_power = -imported_power
            battery_exchange_power += self._battery.charge(self._battery.conf.max_charge_power, dt_seconds)

        self.battery_exchange_power = battery_exchange_power

        if self._load_reconnection_time and timestamp > self._load_reconnection_time:
            self._load_reconnection_time = None
            self.load_line = True

    def __str__(self) -> str:
        return f"Inverter(load_line={self.load_line}, load_power={self.load_power:.3f}, utility_line={self.utility_line}, utility_exchange_power={self.utility_exchange_power:.3f}, panels_power={self.panels_power:.3f}, battery_exchange_power={self.battery_exchange_power:.3f})"
