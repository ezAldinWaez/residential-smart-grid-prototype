from rsg_prototype.sim_time_loc import SimulationOfTimeLocation, Location
from rsg_prototype.sim_houses_loads import SimulationOfHousesLoads
from rsg_prototype.sim_solar_system import SimulationOfSolarSystem, PVConf
from app_tk import App


def main():
    stl = SimulationOfTimeLocation(
        time_factor=3600,
        location=Location.ALEPPO,
    )

    shl = SimulationOfHousesLoads(
        stl=stl,
        num_houses=12,
        log=True,
    )
    shl.start()

    sss = SimulationOfSolarSystem(
        stl=stl,
        pv_conf=PVConf(
            panels_count=10,
            panel_area=1.6,  # [m**2]
            panel_efficiency=.15,  # [0->1]
        ),
        log=True,
    )
    sss.start()

    app = App(stl, shl, sss)
    app.mainloop()


if __name__ == "__main__":
    main()
