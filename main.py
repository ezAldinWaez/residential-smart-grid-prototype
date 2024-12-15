from houses_loads_sim.sim import HousesLoadsSimulator
from solar_system_sim.sim import SolarSystemSimulator
from sim_time_loc.sim_time_loc import SimulationTimeLocation
from sim_time_loc.data import Location
from app.gui import App


def main():
    sim_time_loc = SimulationTimeLocation(
        time_factor=3600,  # every one real second equals one simulation hour
        location=Location.ALEPPO,
    )

    hls_sim = HousesLoadsSimulator(
        sim_time_loc=sim_time_loc,
        num_houses=9,
        log=True,
    )
    hls_sim.start()

    sss_sim = SolarSystemSimulator(
        sim_time_loc=sim_time_loc,
        panels_count=10,
        panel_area=1.6,  # [m**2]
        panel_efficiency=.15,  # [0->1]
        log=True,
    )
    sss_sim.start()

    app = App(sim_time_loc, hls_sim, sss_sim)
    app.root.mainloop()


if __name__ == "__main__":
    main()
