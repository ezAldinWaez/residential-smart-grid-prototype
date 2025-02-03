import tkinter as tk
import ttkbootstrap as ttk

from rsg_prototype.sim_time_loc import SimulationOfTimeLocation
from rsg_prototype.sim_houses_loads import SimulationOfHousesLoads
from rsg_prototype.sim_solar_system import SimulationOfSolarSystem

from .views import MainView


class App:
    def __init__(self, stl: SimulationOfTimeLocation, shl: SimulationOfHousesLoads, sss: SimulationOfSolarSystem):
        self.root = tk.Tk()

        # also try 'superhero' and 'solar', and if you want light mode, try 'simplex'.
        # you can see all possible themes by running `tkk.Style().theme_names()`.
        ttk.Style().theme_use('darkly')

        MainView(self.root, stl, shl, sss)

    def mainloop(self):
        self.root.mainloop()
