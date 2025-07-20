"""RSGP settings."""

from datetime import datetime
from pathlib import Path

from rsgp.config.constants import SECONDS_IN_HOUR
from rsgp.solar_system_sim.data import InverterMode
from rsgp.solar_system_sim.data import ChargePriority


class Settings:
    """Settings."""
    # =================================================================================================================
    # SIMULATION GENERAL SETTINGS
    # =================================================================================================================
    TIME_FACTOR = SECONDS_IN_HOUR
    HOUSES_NUM = 12

    # =================================================================================================================
    # BATTERY SETTINGS
    # =================================================================================================================
    BATTERY_CAPACITY = 100_000  # [Wh]
    BATTERY_CHARGE_EFFICIENCY = 0.95  # [%]
    BATTERY_MAX_CHARGE_POWER = 40_000  # [Watt]
    BATTERY_MAX_DISCHARGE_POWER = 10_000  # [Watt]

    # =================================================================================================================
    # PV SETTINGS
    # =================================================================================================================
    PV_NUM_PANELS = 80
    PV_PANEL_AREA = 1.6  # [m^2]
    PV_EFFICIENCY = 0.15  # [%]

    # =================================================================================================================
    # INVERTER SETTINGS
    # =================================================================================================================
    # AC power rating of the inverter [Watt]
    INVERTER_NOMINAL_AC_POWER = 15000.0

    # DC power rating of the inverter [Watt]
    INVERTER_PDCO = 16000.0

    # Nominal inverter efficiency (e.g., 0.96)
    INVERTER_ETA_INV_NOM = 0.96

    # Reference inverter efficiency (e.g., 0.9637)
    INVERTER_ETA_INV_REF = 0.9637

    # AC power consumed by inverter at night [Watt]
    INVERTER_PNT = 20.0

    # Simplified overall nominal efficiency for reverse calculation (DC needed for AC load)
    # It could be INVERTER_ETA_INV_NOM, or INVERTER_NOMINAL_AC_POWER / INVERTER_PDCO, or a specific value (e.g., 0.95)
    INVERTER_ETA_OVR = INVERTER_ETA_INV_NOM

    # Initial mode the inverter is set to use
    INITIAL_INVERTER_MODE = InverterMode.SBU

    # Initial charge priority the inverter is set to use
    INITIAL_CHARGE_PRIORITY = ChargePriority.SOLAR_ONLY

    # =================================================================================================================
    # LOGGING SETTINGS
    # =================================================================================================================
    LOG_LEVEL = "DEBUG"  # It could be "DEBUG", "INFO", "WARNING", "ERROR", or "CRITICAL"
    LOG_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
    LOG_BACKUP_COUNT = 3

    CSV_LOGGING = True

    _ROOT_DIR = Path(__file__).parent.parent

    _STATIC_DIR = _ROOT_DIR / "_static"
    _STATIC_DIR.mkdir(parents=True, exist_ok=True)

    _Log_DIR = _ROOT_DIR / "_logs"
    _Log_DIR.mkdir(parents=True, exist_ok=True)

    _CSV_Log_DIR = _Log_DIR / f"rsgp_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"
    _CSV_Log_DIR.mkdir(parents=True, exist_ok=True)

    NSRDB_PATH = _STATIC_DIR / "nsrdb.csv"
    LOG_PATH = _Log_DIR / "rsgp.log"

    CSV_HLS_LOG_PATH = _CSV_Log_DIR / "houses_loads_simulation.csv"
    CSV_SSS_LOG_PATH = _CSV_Log_DIR / "solar_system_simulation.csv"
    CSV_PM_LOG_PATH = _CSV_Log_DIR / "power_management.csv"

    # =================================================================================================================
    # REMOTE OBJECT SETTINGS
    # =================================================================================================================
    REMOTE_OBJECT_HOST = 'localhost'
    REMOTE_OBJECT_PORT = 41991


settings = Settings()
