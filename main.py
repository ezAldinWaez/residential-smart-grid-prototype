from app.gui import App
from houses_loads_sim.sim import HousesLoadsSimulator

NUM_HOUSES = 9
SIM_TIME_FACTOR = 1.0

if __name__ == "__main__":
    sim = HousesLoadsSimulator(NUM_HOUSES, SIM_TIME_FACTOR, log=True)
    sim.start()

    app = App(sim)
    app.root.mainloop()
