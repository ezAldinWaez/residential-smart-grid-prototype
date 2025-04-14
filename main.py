from datetime import timedelta, timezone

from rsg_prototype.time_sim import TimeSimulator
from rsg_prototype.houses_loads_sim import HousesLoadsSimulator
from rsg_prototype.solar_system_sim import BattConf, SolarSystemSimulator, PVConf
from rsg_prototype.power_mng import PowerManager
from admin_dashboard import AdminDashboardApp

import pandas as pd
from timezonefinder import TimezoneFinder

TIME_FACTOR = 3600  # [sim_sec/real_sec]

NUM_HOUSES = 12

NUM_PANELS = 80
PANEL_AREA = 1.6  # [m^2]
PANEL_EFFICIENCY = .15  # [%]

BATTERY_CAPACITY = 100_000  # [Wh]
BATTERY_CHARGE_EFFICIENCY = .95  # [%]
BATTERY_MAX_CHARGE_POWER = 40_000  # [W]
BATTERY_MAX_DISCHARGE_POWER = 10_000  # [W]

LOG = True

NSRDB_PATH = "data/nsrdb/323705_33.45_-112.06_2023.csv"


def main():
    """Main."""
    _, nsrdb_data, location = init_nsrdb_data()

    time_sim = TimeSimulator(
        time_factor=TIME_FACTOR,
        dataset_start=nsrdb_data['Timestamp'].min(),
        location=location,
    )
    time_sim.start()

    houses_loads_sim = HousesLoadsSimulator(
        ts=time_sim,
        num_houses=NUM_HOUSES,
        log=LOG,
    )
    houses_loads_sim.start(dt=100)

    solar_system_sim = SolarSystemSimulator(
        ts=time_sim,
        pv_conf=PVConf(
            num_panels=NUM_PANELS,
            panel_area=PANEL_AREA,
            panel_efficiency=PANEL_EFFICIENCY,
        ),
        batt_conf=BattConf(
            capacity=BATTERY_CAPACITY,
            charge_efficiency=BATTERY_CHARGE_EFFICIENCY,
            max_charge_power=BATTERY_MAX_CHARGE_POWER,
            max_discharge_power=BATTERY_MAX_DISCHARGE_POWER,
        ),
        nsrdb_data=nsrdb_data,
        log=LOG,
    )
    solar_system_sim.start(dt=100)

    power_mng = PowerManager(
        hls=houses_loads_sim,
        sss=solar_system_sim,
        log=LOG,
    )
    power_mng.start(dt=100)

    app = AdminDashboardApp(
        ts=time_sim,
        hls=houses_loads_sim,
        sss=solar_system_sim,
        pm=power_mng,
    )
    app.mainloop()


def init_nsrdb_data() -> pd.DataFrame:
    nsrdb_meta = pd.read_csv(NSRDB_PATH, nrows=1)
    nsrdb_data = pd.read_csv(NSRDB_PATH, header=2)

    if nsrdb_data is None:
        raise Exception("Error: Couldn't initialize NSRDB data!")

    tz_offset = int(
        nsrdb_meta["Local Time Zone"][0] - nsrdb_meta["Time Zone"][0]
    )

    lat = float(nsrdb_meta["Latitude"][0])
    lng = float(nsrdb_meta["Longitude"][0])
    tz = TimezoneFinder().timezone_at(lat=lat, lng=lng)

    location = {'lat': lat, 'lng': lng, 'tz': tz}

    nsrdb_data.insert(0, 'Timestamp', pd.to_datetime({
        'year': nsrdb_data['Year'],
        'month': nsrdb_data['Month'],
        'day': nsrdb_data['Day'],
        'hour': nsrdb_data['Hour'],
        'minute': nsrdb_data['Minute'],
        'second': 0,
    }, utc=True).dt.tz_convert(timezone(timedelta(hours=tz_offset))))

    nsrdb_data.drop(
        columns=['Year', 'Month', 'Day', 'Hour', 'Minute'],
        inplace=True
    )

    nsrdb_data.insert(
        loc=1,
        column='Time of Day',
        value=[
            'Day' if val < 90 else 'Night'
            for val in nsrdb_data['Solar Zenith Angle']
        ]
    )

    return nsrdb_meta, nsrdb_data, location


if __name__ == "__main__":
    main()
