"""Settings."""

from datetime import datetime
from pathlib import Path


class Settings:
    """Settings."""
    TIME_FACTOR = 3600

    HOUSES_NUM = 12

    BATTERY_CAPACITY = 100_000  # [Wh]
    BATTERY_CHARGE_EFFICIENCY = .95  # [%]
    BATTERY_MAX_CHARGE_POWER = 40_000  # [W]
    BATTERY_MAX_DISCHARGE_POWER = 10_000  # [W]

    PV_NUM_PANELS = 80
    PV_PANEL_AREA = 1.6  # [m^2]
    PV_EFFICIENCY = .15  # [%]

    LOG_LEVEL = "INFO"
    CSV_LOGGING = True

    ROOT_DIR = Path(__file__).parent.parent

    DATA_DIR = ROOT_DIR / "data"
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    Log_DIR = ROOT_DIR / "logs"
    Log_DIR.mkdir(parents=True, exist_ok=True)

    CSV_Log_DIR = Log_DIR / f"rsgp_{datetime.now().strftime("%Y-%m-%d_%H-%M")}"
    CSV_Log_DIR.mkdir(parents=True, exist_ok=True)

    NSRDB_PATH = DATA_DIR / "nsrdb.csv"
    LOG_PATH = Log_DIR / "rsgp.log"

    CSV_HLS_LOG_PATH = CSV_Log_DIR / "houses_loads_simulation.csv"
    CSV_SSS_LOG_PATH = CSV_Log_DIR / "solar_system_simulation.csv"
    CSV_PM_LOG_PATH = CSV_Log_DIR / "power_management.csv"


settings = Settings()
