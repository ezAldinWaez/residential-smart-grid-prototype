import tkinter as tk
import ttkbootstrap as ttk

from rsg_prototype.sim_time_loc import SimulationOfTimeLocation
from rsg_prototype.sim_houses_loads import SimulationOfHousesLoads
from rsg_prototype.sim_solar_system import SimulationOfSolarSystem

from .views import MainView


class App:
    def __init__(self, stl: SimulationOfTimeLocation, shl: SimulationOfHousesLoads, sss: SimulationOfSolarSystem):
        self.stl = stl
        self.shl = shl
        self.sss = sss

        self.root = tk.Tk()
        self.root.title("Residential Smart Grid Simulator")
        self.root.attributes('-fullscreen', True)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        ttk.Style().theme_use('darkly')

        MainView(self)

    def mainloop(self):
        self.root.mainloop()

    def _on_closing(self):
        self.pause_sim()
        self.root.destroy()

    def pause_sim(self):
        self.stl.pause()
        self.shl.pause()
        self.sss.pause()

    def resume_sim(self):
        self.stl.resume()
        self.shl.resume()
        self.sss.resume()
