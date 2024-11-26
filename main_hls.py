from houses_loads_sim.sim import HousesLoadsSimulator
from sim_time_loc.sim_time_loc import SimulationTimeLocation
from houses_loads_sim_app.gui import App


if __name__ == "__main__":
    sim = HousesLoadsSimulator(
        sim_time_loc=SimulationTimeLocation(
            time_factor=60,   # every one real second equals one simulation minute
        ),
        num_houses=9,
        log=True,
    )
    sim.start()

    app = App(sim)
    app.root.mainloop()
