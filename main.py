from sim_houses_loads.sim import HousesLoadsSimulator
from sim_solar_system.sim import SolarSystemSimulator
from sim_time_loc.sim_time_loc import SimulationTimeLocation
from sim_time_loc.data import Location
from app_tk.main import App


def main():
    sim_time_loc = SimulationTimeLocation(
        time_factor=3600,  # every one real second equals one simulation hour
        location=Location.ALEPPO,
    )

    shl_sim = HousesLoadsSimulator(
        sim_time_loc=sim_time_loc,
        num_houses=9,
        log=True,
    )
    shl_sim.start()

    sss_sim = SolarSystemSimulator(
        sim_time_loc=sim_time_loc,
        panels_count=10,
        panel_area=1.6,  # [m**2]
        panel_efficiency=.15,  # [0->1]
        log=True,
    )
    sss_sim.start()

    app = App(sim_time_loc, shl_sim, sss_sim)
    app.mainloop()


if __name__ == "__main__":
    main()
