"""Dashboard application."""

import os
from dotenv import load_dotenv

from .views import MainWindowView

import tkinter as tk
import ttkbootstrap as ttk
from Pyro5.api import Proxy


class DashboardApp:
    """Dashboard app to browse and control the system."""

    def __init__(self) -> None:
        load_dotenv()

        HOST = os.getenv('RSGP_REMOTE_OBJECT_HOST', 'localhost')
        PORT = int(os.getenv('RSGP_REMOTE_OBJECT_PORT', 41991))

        BASE = f'PYRO:{{name}}@{HOST}:{PORT}'

        self._rsgp_ts = Proxy(BASE.format(name='time_sim'))
        self._rsgp_hs = Proxy(BASE.format(name='houses_sim'))
        self._rsgp_sss = Proxy(BASE.format(name='solar_system_sim'))
        self._rsgp_pm = Proxy(BASE.format(name='power_manager'))

        self._root = tk.Tk()

        style = ttk.Style()
        style.theme_use('yeti')  # try 'darkly', 'superhero', 'solar', 'simplex'.

        MainWindowView(
            root=self._root,
            rsgp_ts=self._rsgp_ts,
            rsgp_hs=self._rsgp_hs,
            rsgp_sss=self._rsgp_sss,
            rsgp_pm=self._rsgp_pm,
        )

    def mainloop(self) -> None:
        """Start tkinter app mainloop."""
        self._root.mainloop()

    def destroy(self) -> None:
        """Destroy tkinter app and release pyro proxies."""
        self._root.destroy()
        self._rsgp_ts._pyroRelease()
        self._rsgp_hs._pyroRelease()
        self._rsgp_sss._pyroRelease()
        self._rsgp_pm._pyroRelease()
