"""Dashboard app."""

import tkinter as tk
import ttkbootstrap as ttk
from Pyro5.api import Proxy

from .views import MainWindowView


class DashboardApp:
    """Dashboard app to browse and control the system."""

    rsgp_ts: Proxy  #: Proxy: Remote object proxy for `TimeSimulator` remote object.
    rsgp_hls: Proxy  #: Proxy: Remote object proxy for `HousesLoadsSimulator` remote object.
    rsgp_sss: Proxy  #: Proxy: Remote object proxy for `SolarSystemSimulator` remote object.
    rsgp_pm: Proxy  #: Proxy: Remote object proxy for `PowerManager` remote object.

    def __init__(self):
        HOST = "localhost"
        PORT = 41991
        BASE = f"PYRO:{{name}}@{HOST}:{PORT}"

        self.rsgp_ts = Proxy(BASE.format(name="time_sim"))
        self.rsgp_hls = Proxy(BASE.format(name="houses_loads_sim"))
        self.rsgp_sss = Proxy(BASE.format(name="solar_system_sim"))
        self.rsgp_pm = Proxy(BASE.format(name="power_manager"))

        self.root = tk.Tk()

        style = ttk.Style()
        style.theme_use('solar')  # try 'darkly', 'superhero', 'solar', 'simplex'.

        MainWindowView(
            root=self.root,
            rsgp_ts=self.rsgp_ts,
            rsgp_hls=self.rsgp_hls,
            rsgp_sss=self.rsgp_sss,
            rsgp_pm=self.rsgp_pm,
        )

    def mainloop(self):
        """Start tkinter app mainloop."""
        self.root.mainloop()
