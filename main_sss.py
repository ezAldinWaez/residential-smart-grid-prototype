from solar_system_sim.sim import SolarSystemSimulator
from sim_time_loc.sim_time_loc import SimulationTimeLocation
from sim_time_loc.data import Location
from solar_system_sim_app.gui import App


if __name__ == "__main__":
    solar_sim = SolarSystemSimulator(
        sim_time_loc=SimulationTimeLocation(
            time_factor=3600,  # every one real second equals one simulation hour
            location=Location.ALEPPO,
        ),
        panels_count=10,
        panel_area=1.6,  # [m**2]
        panel_efficiency=.15,  # [0->1]
        log=True,
    )
    solar_sim.start()

    app = App(solar_sim)
    app.root.mainloop()
