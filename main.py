from houses_loads_sim.sim import HousesLoadsSimulator
from houses_loads_sim_app.gui import App

if __name__ == "__main__":
    sim = HousesLoadsSimulator(
        num_houses=9,
        sim_time_factor=60, # every one real second equals one simulation minute
        log=True
    )
    sim.start()

    app = App(sim)
    app.root.mainloop()
