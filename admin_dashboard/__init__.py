"""Admin dashboard package.

Todos:
    - Make ``Admin Dashboard`` run on a separate proccess, or even a separate computer, and
      comunicate to the ``RSG Prototype`` process; since it should be run on admin laptop while
      ``RSG Protytype`` process should be run on Raspberry Pi.
"""

import tkinter as tk
import ttkbootstrap as ttk

from rsg_prototype.time_sim import TimeSimulator
from rsg_prototype.houses_loads_sim import HousesLoadsSimulator
from rsg_prototype.solar_system_sim import SolarSystemSimulator
from rsg_prototype.power_mng import PowerManager

from .views import MainWindowView


class AdminDashboardApp:
    """Admin dashboard app to browse and control the system."""

    def __init__(self, time_sim: TimeSimulator, houses_loads_sim: HousesLoadsSimulator, solar_system_sim: SolarSystemSimulator,
                 power_mng: PowerManager):
        self.root = tk.Tk()

        style = ttk.Style()
        style.theme_use('darkly')  # try 'superhero', 'solar', 'simplex'.

        MainWindowView(
            root=self.root,
            time_sim=time_sim,
            houses_loads_sim=houses_loads_sim,
            solar_system_sim=solar_system_sim,
            power_manager=power_mng,
        )

    def mainloop(self):
        """Start tkinter app mainloop."""
        self.root.mainloop()
