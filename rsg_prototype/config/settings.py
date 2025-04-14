from pathlib import Path


class Settings:
    TIME_FACTOR = 3600

    NUM_HOUSES = 12

    BATTERY_CAPACITY = 100_000  # [Wh]
    BATTERY_CHARGE_EFFICIENCY = .95  # [%]
    BATTERY_MAX_CHARGE_POWER = 40_000  # [W]
    BATTERY_MAX_DISCHARGE_POWER = 10_000  # [W]

    PV_NUM_PANELS = 80
    PV_PANEL_AREA = 1.6  # [m^2]
    PV_EFFICIENCY = .15  # [%]

    CSV_LOGGING = True

    LOG_LEVEL = "INFO"

    DATA_DIR = Path(__file__).parent.parent.parent / "data"
    NSRDB_DIR: Path = DATA_DIR / "nsrdb"
    GRAPHS_DIR: Path = DATA_DIR / "graphs"
    LOGS_DIR: Path = DATA_DIR / "logs"

    NSRDB_PATH = NSRDB_DIR / "323705_33.45_-112.06_2023.csv"
    LOG_PATH = LOGS_DIR / "rsg_prototype.log"


settings = Settings()
