import tkinter as tk
import ttkbootstrap as ttk

from rsg_prototype.time_loc_sim import TimeLocSimulator
from rsg_prototype.houses_loads_sim import HousesLoadsSimulator
from rsg_prototype.solar_system_sim import SolarSystemSimulator

from .views import MainView


class App:
    def __init__(self, tls: TimeLocSimulator, hls: HousesLoadsSimulator, sss: SolarSystemSimulator):
        self.root = tk.Tk()

        # also try 'superhero' and 'solar', and if you want light mode, try 'simplex'.
        # you can see all possible themes by running `tkk.Style().theme_names()`.
        ttk.Style().theme_use('darkly')

        MainView(self.root, tls, hls, sss)

    def mainloop(self):
        self.root.mainloop()
