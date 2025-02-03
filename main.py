from rsg_prototype.time_loc_sim import TimeLocSimulator, Location
from rsg_prototype.houses_loads_sim import HousesLoadsSimulator
from rsg_prototype.solar_system_sim import SolarSystemSimulator, PVConf
from app_tk import App


def main():
    tls = TimeLocSimulator(
        time_factor=3600,
        location=Location.ALEPPO,
    )
    tls.start()

    hls = HousesLoadsSimulator(
        tls=tls,
        num_houses=12,
        log=True,
    )
    hls.start()

    sss = SolarSystemSimulator(
        tls=tls,
        pv_conf=PVConf(
            panels_count=10,
            panel_area=1.6,  # [m**2]
            panel_efficiency=.15,  # [0->1]
        ),
        log=True,
    )
    sss.start()



    app = App(tls, hls, sss)
    app.mainloop()


if __name__ == "__main__":
    main()
