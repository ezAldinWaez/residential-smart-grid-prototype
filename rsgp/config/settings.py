"""RSGP settings."""

from datetime import datetime
from pathlib import Path


class Settings:
    """Settings."""
    # ==============================================================================
    # SIMULATION GENERAL SETTINGS
    # ==============================================================================
    TIME_FACTOR = 3600
    HOUSES_NUM = 12

    # ==============================================================================
    # BATTERY SETTINGS
    # ==============================================================================
    BATTERY_CAPACITY = 100_000  # [Wh]
    BATTERY_CHARGE_EFFICIENCY = .95  # [%]
    BATTERY_MAX_CHARGE_POWER = 40_000  # [W]
    BATTERY_MAX_DISCHARGE_POWER = 10_000  # [W]

    # ==============================================================================
    # PV SETTINGS
    # ==============================================================================
    PV_NUM_PANELS = 80
    PV_PANEL_AREA = 1.6  # [m^2]
    PV_EFFICIENCY = .15  # [%]

    # ==============================================================================
    # INVERTER SETTINGS
    # ==============================================================================
    # AC power rating of the inverter (Watts). Used to cap output.
    INVERTER_NOMINAL_AC_POWER = 15000.0  # Paco - UPPED from 5000.0 W

    # DC power rating of the inverter (Watts). This is pdc0 for pvlib.inverter.pvwatts.
    INVERTER_PDCO = 16000.0 # UPPED from 5200.0 W

    # Nominal inverter efficiency for pvlib.inverter.pvwatts (e.g., 0.96)
    # The default in pvlib.inverter.pvwatts is 0.96.
    INVERTER_ETA_INV_NOM = 0.96

    # Reference inverter efficiency for pvlib.inverter.pvwatts (e.g., 0.9637)
    # The default in pvlib.inverter.pvwatts is 0.9637.
    INVERTER_ETA_INV_REF = 0.9637
    
    # AC power consumed by inverter at night (Watts).
    # This is not part of the pvlib.inverter.pvwatts model output but can be a separate behavior.
    INVERTER_PNT = 20.0 # Slightly increased for a larger inverter, was 10.0 W   

    # Simplified overall nominal efficiency for reverse calculation (DC needed for AC load).
    # You can set this to INVERTER_ETA_INV_NOM, or INVERTER_NOMINAL_AC_POWER / INVERTER_PDCO,
    # or a specific value based on typical operating conditions.
    EFFECTIVE_INVERTER_NOMINAL_EFFICIENCY = 0.95 # Kept at 0.95, a reasonable general value

    # ==============================================================================
    # LOGGING SETTINGS
    # ==============================================================================
    LOG_LEVEL = "DEBUG" # It could be "DEBUG", "INFO", "WARNING", "ERROR", or "CRITICAL".
    LOG_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
    LOG_BACKUP_COUNT = 3
    CSV_LOGGING = True

    _ROOT_DIR = Path(__file__).parent.parent

    _DATA_DIR = _ROOT_DIR / "data"
    _DATA_DIR.mkdir(parents=True, exist_ok=True)

    _Log_DIR = _ROOT_DIR / "logs"
    _Log_DIR.mkdir(parents=True, exist_ok=True)

    _CSV_Log_DIR = _Log_DIR / f"rsgp_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"
    _CSV_Log_DIR.mkdir(parents=True, exist_ok=True)

    NSRDB_PATH = _DATA_DIR / "nsrdb.csv"
    LOG_PATH = _Log_DIR / "rsgp.log"

    CSV_HLS_LOG_PATH = _CSV_Log_DIR / "houses_loads_simulation.csv"
    CSV_SSS_LOG_PATH = _CSV_Log_DIR / "solar_system_simulation.csv"
    CSV_PM_LOG_PATH = _CSV_Log_DIR / "power_management.csv"


    # ==============================================================================
    # REMOTE INTERFACE SETTINGS
    # ==============================================================================
    REMOTE_INTERFACE_HOST = 'localhost'
    REMOTE_INTERFACE_PORT = 41991

settings = Settings()