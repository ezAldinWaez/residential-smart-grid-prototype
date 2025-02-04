"""Tkinter app package."""

import tkinter as tk
import ttkbootstrap as ttk

from rsg_prototype.time_loc_sim import TimeLocSimulator
from rsg_prototype.houses_loads_sim import HousesLoadsSimulator
from rsg_prototype.solar_system_sim import SolarSystemSimulator
from rsg_prototype.power_mng import PowerManager

from .views import MainWindowView


class App:
    """Tkinter app to browse and control the system."""

    def __init__(self, tls: TimeLocSimulator, hls: HousesLoadsSimulator, sss: SolarSystemSimulator,
                 pm: PowerManager):
        self.root = tk.Tk()

        style = ttk.Style()
        style.theme_use('darkly')  # try 'superhero', 'solar', 'simplex'.

        MainWindowView(
            root=self.root,
            tls=tls,
            hls=hls,
            sss=sss,
            pm=pm,
        )

    def mainloop(self):
        """Start tkinter app mainloop."""
        self.root.mainloop()
