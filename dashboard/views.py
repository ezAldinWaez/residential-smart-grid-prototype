"""Dashboard views."""

from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime

import tkinter as tk
import ttkbootstrap as ttk

from .utils import build_scrollable_frame
if TYPE_CHECKING:
    from ..rsgp.time_sim.simulator import TimeSimulator
    from ..rsgp.houses_loads_sim.simulator import HousesLoadsSimulator
    from ..rsgp.solar_system_sim.simulator import SolarSystemSimulator
    from ..rsgp.power_mng.manager import PowerManager


class MainWindowView:
    """Main window view.

    Args:
        root (tk.Tk): Tk window root.
        rsgp_ts (TimeSimulator): Time simulator instance.
        rsgp_hls (HousesLoadsSimulator): Houses loads simulator instance.
        rsgp_sss (SolarSystemSimulator): Solar system simulator instance.
        rsgp_pm (PowerManager): Power manager instance.

    """

    def __init__(self, root: tk.Tk, rsgp_ts: TimeSimulator, rsgp_hls: HousesLoadsSimulator,
                 rsgp_sss: SolarSystemSimulator, rsgp_pm: PowerManager):
        self._root = root
        self._root.title("Residential Smart Grid Prototype")
        self._root.attributes('-fullscreen', True)
        self._root.protocol("WM_DELETE_WINDOW", self._on_closing)

        self._rsgp_ts = rsgp_ts
        self._rsgp_hls = rsgp_hls
        self._rsgp_sss = rsgp_sss
        self._rsgp_pm = rsgp_pm

        self._sv_time = ttk.StringVar(value="Time: ??:??:??")
        self._sv_toggle_sim = ttk.StringVar(value="Toggle")

        f_main = ttk.Frame(self._root, padding=10)
        f_main.pack(fill="both", expand=True)

        self.resume_sim()

        self._build_header(f_main)
        self._build_body(f_main)

        self._update_ui(dt=100)

    def _build_header(self, f_parent: ttk.Frame):
        f_main = ttk.Frame(f_parent)
        f_main.pack(fill="x", pady=(0, 10))

        ttk.Label(
            f_main,
            text="Residential Smart Grid Prototype",
            font=("Arial", 24),
        ).pack(side="left")

        f_right = ttk.Frame(f_main)
        f_right.pack(side="right")

        ttk.Label(
            f_right,
            textvariable=self._sv_time,
            font=("Arial", 12),
        ).pack(side="left", padx=(0, 10))

        ttk.Button(
            f_right,
            textvariable=self._sv_toggle_sim,
            command=self.toggle_sim,
            width=10,
        ).pack(side='left', padx=(0, 10))

        ttk.Button(
            f_right,
            text="Set Utilities",
            command=lambda: self.set_all_utilities(True),
            width=10,
        ).pack(side='left', padx=(0, 10))

        ttk.Button(
            f_right,
            text="Reset Utilities",
            command=lambda: self.set_all_utilities(False),
            width=10,
        ).pack(side='left', padx=(0, 10))

        ttk.Button(
            f_right,
            text="Set Loads",
            command=lambda: self.set_all_loads(True),
            width=10,
        ).pack(side='left', padx=(0, 10))

        ttk.Button(
            f_right,
            text="Reset Loads",
            command=lambda: self.set_all_loads(False),
            width=10,
        ).pack(side='left')

    def _build_body(self, f_parent: ttk.Frame):
        n_main = ttk.Notebook(
            f_parent,
            style="Primary.TNotebook",
        )
        n_main.pack(fill='both', expand=True)

        f_houses_loads_sim = ttk.Frame(n_main)
        n_main.add(f_houses_loads_sim, text='Houses Load Simulation')

        HLSTabView(
            root=self._root,
            f_parent=f_houses_loads_sim,
            _rsgp_hls=self._rsgp_hls,
        )

        f_solar_system_sim = ttk.Frame(n_main)
        n_main.add(f_solar_system_sim, text='Solar System Simulation')

        SSSTabView(
            root=self._root,
            f_parent=f_solar_system_sim,
            rsgp_sss=self._rsgp_sss,
        )

        f_power_manager = ttk.Frame(n_main)
        n_main.add(f_power_manager, text='Power Management')

        PMTabView(
            root=self._root,
            f_parent=f_power_manager,
            rsgp_pm=self._rsgp_pm,
        )

    def _on_closing(self):
        self.pause_sim()
        self._root.destroy()

    def _update_ui(self, dt: int):
        self._sv_time.set(
            f"Time: {datetime.fromisoformat(self._rsgp_ts.get_timestamp()).strftime('%H:%M:%S')}")
        self._sv_toggle_sim.set(
            "Pause" if self._rsgp_hls.is_running() or self._rsgp_sss.is_running() or self._rsgp_pm.is_running()
            else "Resume")
        self._root.after(dt, self._update_ui, dt)

    def toggle_sim(self):
        """Toggle simulation state."""
        if self._rsgp_hls.is_running() or self._rsgp_sss.is_running() or self._rsgp_pm.is_running():
            self.pause_sim()
        else:
            self.resume_sim()

    def pause_sim(self):
        """Pause simulation."""
        self._rsgp_ts.pause()
        self._rsgp_hls.pause()
        self._rsgp_sss.pause()
        self._rsgp_pm.pause()

    def resume_sim(self):
        """Resume simulation."""
        self._rsgp_ts.resume()
        self._rsgp_hls.resume()
        self._rsgp_sss.resume()
        self._rsgp_pm.resume()

    def set_all_utilities(self, state: bool):
        """Turn all utility lines for all houses to `state`."""
        for house in self._rsgp_hls.get_houses():
            house.set_utility_line(state)

    def set_all_loads(self, state: bool):
        """Turn all utility lines for all houses to `state`."""
        for house in self._rsgp_hls.get_houses():
            house.set_load_line(state)


class HLSTabView:
    """Houses loads simulation tab view.

    Args:
        root (tk.Tk): Tk window root.
        f_parent (ttk.Frame): Parent fram, master of the main frame.
        rsgp_hls (HousesLoadsSimulator): Houses loads simulator instance.

    """

    def __init__(self, root: tk.Tk, f_parent: ttk.Frame, rsgp_hls: HousesLoadsSimulator):
        self._root = root
        self._rsgp_hls = rsgp_hls

        self._hc_windows: dict[int, HouseControlsWindowView] = {}

        self._sv_system_load = ttk.StringVar(value="System Load: ? kW")
        self._sv_houses_loads = [
            ttk.StringVar(value="Load: ? KW")
            for _ in range(self._rsgp_hls.get_num_houses())]
        self._iv_utility_lines = [
            ttk.IntVar(value=0)
            for _ in range(self._rsgp_hls.get_num_houses())]
        self._iv_load_lines = [
            ttk.IntVar(value=0)
            for _ in range(self._rsgp_hls.get_num_houses())]

        if self._rsgp_hls.get_num_houses() > 10:
            f_main = build_scrollable_frame(f_parent, padding=10)
        else:
            f_main = ttk.Frame(f_parent, padding=10)
            f_main.pack(fill="both", expand=True)

        self._build_header(f_main)
        self._build_body(f_main)

        self._update_ui(dt=100)

    def _build_header(self, f_parent: ttk.Frame):
        f_main = ttk.Frame(f_parent)
        f_main.pack(fill="x", pady=(0, 10))

        ttk.Label(
            f_main,
            text="Houses Loads Simulation",
            font=("Arial", 18),
        ).pack(side="left")

        ttk.Label(
            f_main,
            textvariable=self._sv_system_load,
            font=("Arial", 12),
        ).pack(side="right")

    def _build_body(self, f_parent: ttk.Frame):
        f_main = ttk.Frame(f_parent)
        f_main.pack(fill="both", expand=True)
        f_main.columnconfigure(list(range(5)), weight=1)

        for idx in range(self._rsgp_hls.get_num_houses()):
            f_house = ttk.Labelframe(
                f_main,
                padding=20,
                labelwidget=ttk.Label(
                    f_main,
                    text=f" House {idx + 1:02d} ",
                    font=("Arial", 12),
                ),
            )
            f_house.grid(row=idx // 5, column=idx % 5, pady=(0, 20), padx=36)

            ttk.Label(
                f_house,
                textvariable=self._sv_houses_loads[idx],
                font=("Arial", 12),
            ).pack(fill='x', pady=(0, 10))

            ttk.Checkbutton(
                f_house,
                text="Utility Line",
                variable=self._iv_utility_lines[idx],
                command=lambda idx=idx: self._rsgp_hls.get_house(
                    idx).toggle_utility_line(),
                style="Primary.Roundtoggle.Toolbutton",
            ).pack(fill='x')

            ttk.Checkbutton(
                f_house,
                text="Load Line",
                variable=self._iv_load_lines[idx],
                command=lambda idx=idx: self._rsgp_hls.get_house(
                    idx).toggle_load_line(),
                style="Primary.Roundtoggle.Toolbutton",
            ).pack(fill='x', pady=(0, 10))

            ttk.Button(
                f_house,
                text="Open Control Panel",
                command=lambda idx=idx: self.open_hc_window(idx),
                style="Primary.TButton",
            ).pack(fill='x')

    def _update_ui(self, dt: int):
        if self._rsgp_hls.is_running():
            self._sv_system_load.set(
                f"System Load: {self._rsgp_hls.get_system_load()/1000:,.3f} kW")
            for idx, load in enumerate(self._sv_houses_loads):
                load.set(
                    f"Load: {self._rsgp_hls.get_house(idx).get_load()/1000:07,.3f} KW")
            for idx, line in enumerate(self._iv_utility_lines):
                line.set(
                    int(self._rsgp_hls.get_house(idx).get_utility_line()))
            for idx, line in enumerate(self._iv_load_lines):
                line.set(
                    int(self._rsgp_hls.get_house(idx).get_load_line()))

        self._root.after(dt, self._update_ui, dt)

    def open_hc_window(self, idx: int):
        """Open house controls window.

        Args:
            idx (int): House index.

        """
        if idx in self._hc_windows and self._hc_windows[idx]._root.winfo_exists():
            self._hc_windows[idx]._root.focus()
        else:
            self._hc_windows[idx] = HouseControlsWindowView(
                root=ttk.Toplevel(self._root),
                idx=idx,
                rsgp_hls=self._rsgp_hls,
                variables={
                    'total_load': self._sv_houses_loads[idx],
                    'utility_line': self._iv_utility_lines[idx],
                    'load_line': self._iv_load_lines[idx],
                }
            )


class HouseControlsWindowView:
    """House controls window view.

    Args:
        root (tk.Tk): Tk window root.
        idx (int): House index.
        houses_loads_sim (HousesLoadsSimulator): Houses loads simulator instance.
        variables (dict[str, ttk.Variable]): Passed UI variables, including:

                - "total_load" (ttk.StringVar): Total house load label text.
                - "utility_line" (ttk.IntVar): Utility line status (0 or 1).
                - "load_line" (ttk.IntVar): Load line status (0 or 1).

    """

    idx: int  #: int: House index.

    def __init__(self, root: tk.Tk, idx: int, rsgp_hls: HousesLoadsSimulator,
                 variables: dict[str, ttk.Variable]):
        self.idx = idx

        self._root = root
        self._root.title(f"House {idx + 1} Controls")
        self._root.geometry("600x600")
        self._root.resizable(False, False)

        self._rsgp_hls = rsgp_hls
        self._rsgp_hls_house = self._rsgp_hls.get_house(self.idx)

        self._sv_total_load: ttk.StringVar = variables['total_load']
        self._iv_utility_line: ttk.IntVar = variables['utility_line']
        self._iv_load_line: ttk.IntVar = variables['load_line']

        self._iv_all_envelopes = {
            dn: [
                ttk.IntVar(value=0)
                for _ in range(self._rsgp_hls_house.get_device(dn).get_conf_max_count())
            ]
            for dn in self._rsgp_hls_house.get_devices().keys()
        }

        self._sv_devices_loads = {
            device_name: ttk.StringVar(value="Load: ? Watt")
            for device_name in self._rsgp_hls_house.get_devices().keys()
        }

        f_main = build_scrollable_frame(self._root, width=580, padding=10)

        self._build_header(f_main)
        self._build_body(f_main)

        self._update_ui(dt=100)

    def _build_header(self, f_parent: ttk.Frame):
        f_main = ttk.Frame(f_parent)
        f_main.pack(fill="x", pady=(0, 10))

        ttk.Label(
            f_main,
            text=f"House {self.idx + 1:02d} Control Panel",
            font=("Arial", 24),
        ).pack()

        ttk.Label(
            f_main,
            textvariable=self._sv_total_load,
            font=("Arial", 12),
        ).pack(side="left")

        f_right = ttk.Frame(f_main)
        f_right.pack(side="right")

        ttk.Checkbutton(
            f_right,
            text="Utility Line",
            variable=self._iv_utility_line,
            command=lambda: self._rsgp_hls_house.toggle_utility_line(),
            style="Primary.Roundtoggle.Toolbutton",
        ).pack(side="left", padx=(0, 10))

        ttk.Checkbutton(
            f_right,
            text="Load Line",
            variable=self._iv_load_line,
            command=lambda: self._rsgp_hls_house.toggle_load_line(),
            style="Primary.Roundtoggle.Toolbutton",
        ).pack(side="left", padx=(0, 10))

    def _build_body(self, f_parent: ttk.Frame):
        f_main = ttk.Frame(f_parent)
        f_main.pack(fill="both")

        for dn, device in self._rsgp_hls_house.get_devices().items():

            f_device = ttk.Labelframe(
                f_main,
                padding=(10, 0),
                labelwidget=ttk.Label(
                    f_main,
                    text=f' {dn.replace(
                        '_', ' ').title()} Device Controls ',
                    font=("Arial", 12),
                ),
            )
            f_device.pack(fill="x", pady=(0, 10))

            f_control = ttk.Frame(f_device)
            f_control.pack(fill="x", pady=(0, 10))

            f_envelopes = ttk.Frame(f_control)
            f_envelopes.pack(side="left")

            for idx in range(device.get_conf_max_count()):
                ttk.Checkbutton(
                    f_envelopes,
                    variable=self._iv_all_envelopes[dn][idx],
                    command=lambda idx=idx, device=device: device.toggle_envelope_state(
                        idx=idx,
                        elapsed=self._rsgp_hls.get_time_sim_elapsed()
                    ),
                    style="Primary.Squaretoggle.Toolbutton",
                ).pack(side="left", padx=(0, 10))

            ttk.Label(
                f_control,
                textvariable=self._sv_devices_loads[dn],
                font=("Arial", 12),
            ).pack(side="right")

            ttk.Label(
                f_device,
                text=device.get_conf_summary(),
                font=("Arial", 8),
                style="Secondary.TLabel",
            ).pack(fill="x", pady=(0, 10))

    def _update_ui(self, dt):
        if self._rsgp_hls.is_running():
            for device_name, load in self._sv_devices_loads.items():
                load.set(
                    f"Load: {self._rsgp_hls_house.get_device(device_name).get_load():,.1f} Watt")

            for dn, _iv_envelopes in self._iv_all_envelopes.items():
                for idx, _iv_envelope in enumerate(_iv_envelopes):
                    _iv_envelope.set(
                        int(self._rsgp_hls_house.get_device(dn).get_envelopes()[idx][2]))

        self._root.after(dt, self._update_ui, dt)


class SSSTabView:
    """Solar system simulation tab view.

    Args:
        root (tk.Tk): Tk window root.
        f_parent (ttk.Frame): Parent fram, master of the main frame.
        rsgp_sss (SolarSystemSimulator): Solar system simulator instance.

    """

    def __init__(self, root: tk.Tk, f_parent: ttk.Frame, rsgp_sss: SolarSystemSimulator):
        self._root = root
        self._rsgp_sss = rsgp_sss

        f_main = ttk.Frame(f_parent, padding=10)
        f_main.pack(fill="both", expand=True)

        self._build_header(f_main)
        self._build_body(f_main)

        self._update_ui(100)

    def _build_header(self, f_parent: ttk.Frame):
        f_main = ttk.Frame(f_parent)
        f_main.pack(fill="x", pady=(0, 10))

        ttk.Label(
            f_main,
            text="Solar System Simulation",
            font=("Arial", 18),
        ).pack(side="left")

    def _build_body(self, f_parent: ttk.Frame):
        f_main = ttk.Frame(f_parent)
        f_main.pack(fill="both", expand=True, pady=20, padx=20)
        f_main.place(relx=.5, rely=.5, anchor='center')

        self.output_text = ttk.Text(
            f_main,
            height=50,
            width=80,
            font=("Arial", 12),
        )
        self.output_text.pack(fill='both')

    def _update_ui(self, dt: int):
        if self._rsgp_sss.is_running():
            # Display real-time wattage output
            self.output_text.delete(1.0, ttk.END)
            self.output_text.insert(
                ttk.END, chars=self._rsgp_sss.summary())
        self._root.after(dt, self._update_ui, dt)


class PMTabView:
    """Power management tab view.

    Args:
        root (tk.Tk): Tk window root.
        f_parent (ttk.Frame): Parent fram, master of the main frame.
        rsgp_pm (PowerManager): Power manager instance.

    """

    def __init__(self, root: tk.Tk, f_parent: ttk.Frame, rsgp_pm: PowerManager):
        self.root = root
        self._rsgp_pm = rsgp_pm

        f_main = ttk.Frame(f_parent, padding=10)
        f_main.pack(fill="both", expand=True)

        self._build_header(f_main)
        self._build_body(f_main)

        self._update_ui(100)

    def _build_header(self, f_parent: ttk.Frame):
        f_main = ttk.Frame(f_parent)
        f_main.pack(fill="x", pady=(0, 10))

        ttk.Label(
            f_main,
            text="Power Management",
            font=("Arial", 18),
        ).pack(side="left")

    def _build_body(self, f_parent: ttk.Frame):
        f_main = ttk.Frame(f_parent)
        f_main.pack(fill="both", expand=True, pady=20, padx=20)
        f_main.place(relx=.5, rely=.5, anchor='center')

        self.output_text = ttk.Text(
            f_main,
            height=5,
            width=80,
            font=("Arial", 12),
        )
        self.output_text.pack(fill='both')

    def _update_ui(self, dt: int):
        if self._rsgp_pm.is_running():
            self.output_text.delete(1.0, ttk.END)
            self.output_text.insert(
                ttk.END, chars=self._rsgp_pm.summary())

        self.root.after(dt, self._update_ui, dt)
