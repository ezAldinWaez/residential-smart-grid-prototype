# pylint: disable=locally-disabled, missing-module-docstring, missing-function-docstring

from rsg_prototype.time_loc_sim import TimeLocSimulator, Location
from rsg_prototype.houses_loads_sim import HousesLoadsSimulator
from rsg_prototype.solar_system_sim import BattConf, SolarSystemSimulator, PVConf
from rsg_prototype.power_mng import PowerManager
from admin_dashboard import AdminDashboardApp


TIME_FACTOR = 3600  # [sim_sec/real_sec]
LOCATION = Location.ALEPPO

NUM_HOUSES = 12

NUM_PANELS = 80
PANEL_AREA = 1.6  # [m^2]
PANEL_EFFICIENCY = .15  # [%]

BATTERY_CAPACITY = 100_000  # [Wh]
BATTERY_CHARGE_EFFICIENCY = .95  # [%]
BATTERY_MAX_CHARGE_POWER = 40_000  # [W]
BATTERY_MAX_DISCHARGE_POWER = 10_000  # [W]

LOG = True


def main():
    """Main."""
    time_loc_sim = TimeLocSimulator(
        time_factor=TIME_FACTOR,
        location=LOCATION,
    )
    time_loc_sim.start()

    houses_loads_sim = HousesLoadsSimulator(
        tls=time_loc_sim,
        num_houses=NUM_HOUSES,
        log=LOG,
    )
    houses_loads_sim.start(dt=100)

    solar_system_sim = SolarSystemSimulator(
        tls=time_loc_sim,
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
        tls=time_loc_sim,
        hls=houses_loads_sim,
        sss=solar_system_sim,
        pm=power_mng,
    )
    app.mainloop()


if __name__ == "__main__":
    main()
