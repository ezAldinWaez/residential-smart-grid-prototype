"""RSGP settings."""

from datetime import datetime
import os
from pathlib import Path

from .constants import SECONDS_IN_MINUTE, BYTES_IN_MB
from ..solar_system_sim.data import InverterMode, ChargePriority

from Pyro5.api import expose
from dotenv import load_dotenv


@expose
class Settings:
    """RSGP Settings."""

    load_dotenv()

    # =================================================================================================================
    # TIME SIMULATION SETTINGS
    # =================================================================================================================
    TIME_FACTOR = 100 * SECONDS_IN_MINUTE  #: The time factor to multiply the simulation time with to get the real time.

    # =================================================================================================================
    # HOUSES SIMULATION SETTINGS
    # =================================================================================================================
    HOUSES_NUM = 3  #: The number of houses to simulate.

    # =================================================================================================================
    # SOLAR SYSTEM SIMULATION SETTINGS
    # =================================================================================================================
    BATTERY_TOTAL_CAPACITY = 100_000  #: The battery capacity in Watt-hours [Wh].
    BATTERY_INIT_RESIDUAL_CAPACITY = 50_000  #: The initial charge level of the battery [Wh].
    BATTERY_CHARGE_EFFICIENCY = 0.95  #: The efficiency of charging and discharging for the battery [%].
    BATTERY_MAX_CHARGE_POWER = 40_000  #: The maximum charge power for the battery [Watt].
    BATTERY_MAX_DISCHARGE_POWER = 40_000  #: The maximum discharge power for the battery [Watt].

    PANELS_NUM = 80  #: The number of panels in the system.
    PANEL_AREA = 1.6  #: The area of a single solar panel in square meters [m^2].
    PANEL_EFFICIENCY = 0.15  #: The efficiency of a single solar panel as a multiplier [%].

    INVERTER_NOMINAL_AC_POWER = 15000.0  #: AC power rating of the inverter [Watt].
    INVERTER_PDCO = 16000.0  #: DC power rating of the inverter [Watt].
    INVERTER_ETA_INV_NOM = 0.96  #: Nominal inverter efficiency [%] (e.g., 0.96).
    INVERTER_ETA_INV_REF = 0.9637  #: Reference inverter efficiency [%] (e.g., 0.9637).
    INVERTER_PNT = 20.0  #: AC power consumed by inverter at night [Watt].
    INVERTER_ETA_OVR = INVERTER_ETA_INV_NOM  #: Simplified overall nominal efficiency for reverse calculation [%].
    INVERTER_INIT_MODE = InverterMode.SBU  #: Initial mode the inverter is set to use.
    INVERTER_INIT_CHARGE_PRIORITY = ChargePriority.SOLAR_ONLY  #: Initial charge priority the inverter is set to use.
    INVERTER_LOAD_RECONNECTION_INTERVAL = 30.0  #: float: Interval to reconnect the load line after disconnection [sec].

    # =================================================================================================================
    # POWER MANAGEMENT SETTINGS
    # =================================================================================================================
    GUARANTEED_MINIMUM_WEIGHT = 0.8  #: The minimum share of each house; the algorithm will never assign them less.
    LEARNING_STEP = 0.005  #: The rate of adjusting the weights in each update step.

    # =================================================================================================================
    # REMOTE OBJECT SETTINGS
    # =================================================================================================================
    RSGP_REMOTE_OBJECT_HOST = os.getenv("RSGP_REMOTE_OBJECT_HOST", 'localhost')
    RSGP_REMOTE_OBJECT_PORT = int(os.getenv("RSGP_REMOTE_OBJECT_PORT", 41991))

    # =================================================================================================================
    # LOGGING SETTINGS
    # =================================================================================================================
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_MAX_BYTES = 5 * BYTES_IN_MB
    LOG_BACKUP_COUNT = 3

    CSV_LOGGING = os.getenv("CSV_LOGGING", False)

    _ROOT_DIR = Path(__file__).parent.parent

    _STATIC_DIR = _ROOT_DIR / "_static"
    _STATIC_DIR.mkdir(parents=True, exist_ok=True)

    _Log_DIR = _ROOT_DIR / "_logs"
    _Log_DIR.mkdir(parents=True, exist_ok=True)

    _CSV_Log_DIR = _Log_DIR / f"rsgp_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"
    _CSV_Log_DIR.mkdir(parents=True, exist_ok=True)

    NSRDB_PATH = _STATIC_DIR / "nsrdb.csv"
    LOG_PATH = _Log_DIR / "rsgp.log"

    CSV_HS_LOG_PATH = _CSV_Log_DIR / "houses_simulation.csv"
    CSV_SSS_LOG_PATH = _CSV_Log_DIR / "solar_system_simulation.csv"
    CSV_PM_LOG_PATH = _CSV_Log_DIR / "power_management.csv"

    @classmethod
    def get_setting(cls, name):
        """Remote access a static attribute by its name."""
        if hasattr(cls, name) and not name.startswith('_'):
            value = getattr(cls, name)
            if isinstance(value, Path):
                value = str(value)
            return value
        raise AttributeError(f"'{cls.__name__}' object has no public attribute '{name}'")


settings = Settings()
