"""Admin dashboard package."""


from .views import MainWindowView

import Pyro5.api
import tkinter as tk
import ttkbootstrap as ttk


class AdminDashboardApp:
    """Admin dashboard app to browse and control the system."""

    def __init__(self):
        base = "PYRO:{name}@{host}:{port}"
        host = "localhost"
        port = "41991"

        self.time_sim = Pyro5.api.Proxy(
            base.format(name="time_sim", host=host, port=port))
        self.houses_loads_sim = Pyro5.api.Proxy(
            base.format(name="houses_loads_sim", host=host, port=port))
        self.solar_system_sim = Pyro5.api.Proxy(
            base.format(name="solar_system_sim", host=host, port=port))
        self.power_manager = Pyro5.api.Proxy(
            base.format(name="power_manager", host=host, port=port))

        self.root = tk.Tk()

        style = ttk.Style()
        style.theme_use('darkly')  # try 'superhero', 'solar', 'simplex'.

        MainWindowView(
            root=self.root,
            time_sim=self.time_sim,
            houses_loads_sim=self.houses_loads_sim,
            solar_system_sim=self.solar_system_sim,
            power_manager=self.power_manager,
        )

    def mainloop(self):
        """Start tkinter app mainloop."""
        self.root.mainloop()
