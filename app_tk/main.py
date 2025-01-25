import tkinter as tk
import ttkbootstrap as ttk

from sim_time_loc.sim_time_loc import SimulationTimeLocation
from sim_houses_loads.sim import HousesLoadsSimulator
from sim_solar_system.sim import SolarSystemSimulator

from app_tk.views.main_view import MainView


class App:
    def __init__(self, sim_time_loc: SimulationTimeLocation, shl_sim: HousesLoadsSimulator, sss_sim: SolarSystemSimulator):
        self.sim_time_loc = sim_time_loc
        self.shl_sim = shl_sim
        self.sss_sim = sss_sim

        self.root = tk.Tk()
        ttk.Style().theme_use('darkly')
        self.root.title("Residential Smart Grid Simulator")
        self.root.attributes('-fullscreen', True)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        MainView(self)

    def mainloop(self):
        self.root.mainloop()

    def _on_closing(self):
        self.pause_sim()
        self.root.destroy()

    def pause_sim(self):
        self.sim_time_loc.pause()
        self.shl_sim.pause()
        self.sss_sim.pause()

    def resume_sim(self):
        self.sim_time_loc.resume()
        self.shl_sim.resume()
        self.sss_sim.resume()
