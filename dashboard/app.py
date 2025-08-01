"""Dashboard app."""

import os
from dotenv import load_dotenv

from .views import MainWindowView

import tkinter as tk
import ttkbootstrap as ttk
from Pyro5.api import Proxy


class DashboardApp:
    """Dashboard app to browse and control the system."""

    rsgp_ts: Proxy  #: Proxy: Remote object proxy for `TimeSimulator` remote object.
    rsgp_hs: Proxy  #: Proxy: Remote object proxy for `HousesSimulator` remote object.
    rsgp_sss: Proxy  #: Proxy: Remote object proxy for `SolarSystemSimulator` remote object.
    rsgp_pm: Proxy  #: Proxy: Remote object proxy for `PowerManager` remote object.

    def __init__(self):
        load_dotenv()

        HOST = os.getenv("REMOTE_OBJECT_HOST")
        PORT = int(os.getenv("REMOTE_OBJECT_PORT"))

        BASE = f"PYRO:{{name}}@{HOST}:{PORT}"

        self.rsgp_ts = Proxy(BASE.format(name="time_sim"))
        self.rsgp_hs = Proxy(BASE.format(name="houses_sim"))
        self.rsgp_sss = Proxy(BASE.format(name="solar_system_sim"))
        self.rsgp_pm = Proxy(BASE.format(name="power_manager"))

        self.root = tk.Tk()

        style = ttk.Style()
        style.theme_use('darkly')  # try 'darkly', 'superhero', 'solar', 'simplex'.

        MainWindowView(
            root=self.root,
            rsgp_ts=self.rsgp_ts,
            rsgp_hs=self.rsgp_hs,
            rsgp_sss=self.rsgp_sss,
            rsgp_pm=self.rsgp_pm,
        )

    def mainloop(self):
        """Start tkinter app mainloop."""
        self.root.mainloop()
