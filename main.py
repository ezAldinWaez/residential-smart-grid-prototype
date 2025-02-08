# pylint: disable=locally-disabled, missing-module-docstring, missing-function-docstring

from rsg_prototype.time_loc_sim import TimeLocSimulator, Location
from rsg_prototype.houses_loads_sim import HousesLoadsSimulator
from rsg_prototype.solar_system_sim import Battery, SolarSystemSimulator, PVConf
from rsg_prototype.power_mng import PowerManager
from app_tk import App

TIME_FACTOR = 3600
LOCATION = Location.ALEPPO
NUM_HOUSES = 12

NUM_PANELS = 10
PANEL_AREA = 1.6
PANEL_EFFICIENCY = .15

LOG = True


def main():
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
    houses_loads_sim.start()

    solar_system_sim = SolarSystemSimulator(
        tls=time_loc_sim,
        pv_conf=PVConf(
            num_panels=NUM_PANELS,
            panel_area=PANEL_AREA,
            panel_efficiency=PANEL_EFFICIENCY,
        ),
        battery_conf=Battery(
            capacity=50000,
            charge_level=25000,
            charge_efficiency=0.95,
            max_charge_rate=50000,
            max_discharge_rate=10000,
        ),
        log=LOG,
    )
    solar_system_sim.start()

    power_mng = PowerManager(
        hls=houses_loads_sim,
        sss=solar_system_sim,
        log=LOG,
    )
    power_mng.start()

    app = App(
        tls=time_loc_sim,
        hls=houses_loads_sim,
        sss=solar_system_sim,
        pm=power_mng,
    )
    app.mainloop()


if __name__ == "__main__":
    main()
