"""Tkinter app views."""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.widgets import Notebook

from rsg_prototype.time_loc_sim import TimeLocSimulator
from rsg_prototype.houses_loads_sim import HousesLoadsSimulator
from rsg_prototype.solar_system_sim import SolarSystemSimulator
from rsg_prototype.power_mng import PowerManager


class MainWindowView:
    """Main window view.

    Args:
        root (tk.Tk): Tk window root.
        tls (TimeLocSimulator): Time and location simulator instance.
        hls (HousesLoadsSimulator): Houses loads simulator instance.
        sss (SolarSystemSimulator): Solar system simulator instance.
        pm (PowerManager): Power manager instance.

    """

    def __init__(self, root: tk.Tk, tls: TimeLocSimulator, hls: HousesLoadsSimulator,
                 sss: SolarSystemSimulator, pm: PowerManager):
        self.root = root
        self.root.title("Residential Smart Grid Prototype")
        self.root.attributes('-fullscreen', True)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self._tls = tls
        self._hls = hls
        self._sss = sss
        self._pm = pm

        self._sv_time = ttk.StringVar(value="Time: ??:??:??")

        f_main = ttk.Frame(self.root, padding=10)
        f_main.pack(fill="both", expand=True)

        self._build_header(f_main)
        self._build_body(f_main)

        self._update_ui(dt=100)

    def _build_header(self, f_parent: ttk.Frame):
        f_main = ttk.Frame(f_parent)
        f_main.pack(fill="x", pady=(0, 10))

        ttk.Label(
            f_main,
            text="Residential Smart Grid Prototype",
            font=("Calibri", 24),
        ).pack(side="left")

        f_right = ttk.Frame(f_main)
        f_right.pack(side="right")

        ttk.Label(
            f_right,
            textvariable=self._sv_time,
            font=("Calibri", 12),
        ).pack(side="left", padx=(0, 10))

        ttk.Label(
            f_right,
            text=f"Location: {self._tls.loc_name}",
            font=("Calibri", 12),
        ).pack(side="left", padx=(0, 10))

        ttk.Button(
            f_right,
            text="Pause Simulation",
            command=self.pause_sim,
        ).pack(side="left", padx=(0, 10))

        ttk.Button(
            f_right,
            text="Resume Simulation",
            command=self.resume_sim,
        ).pack(side="left")

    def _build_body(self, f_parent: ttk.Frame):
        n_main = Notebook(
            f_parent,
            style="Primary.TNotebook",
        )
        n_main.pack(fill='both', expand=True)

        f_hls = ttk.Frame(n_main)
        n_main.add(f_hls, text='Houses Load Simulation')

        HLSTabView(
            root=self.root,
            f_parent=f_hls,
            hls=self._hls,
        )

        f_sss = ttk.Frame(n_main)
        n_main.add(f_sss, text='Solar System Simulation')

        SSSTabView(
            root=self.root,
            f_parent=f_sss,
            sss=self._sss,
        )

        f_pm = ttk.Frame(n_main)
        n_main.add(f_pm, text='Power Management')

        PMTabView(
            root=self.root,
            f_parent=f_pm,
            pm=self._pm,
        )

    def _on_closing(self):
        self.pause_sim()
        self.root.destroy()

    def _update_ui(self, dt: int):
        self._sv_time.set(f"Time: {self._tls.get_time().strftime('%H:%M:%S')}")
        self.root.after(dt, self._update_ui, dt)

    def pause_sim(self):
        """Pause simulation."""
        self._tls.pause()
        self._hls.pause()
        self._sss.pause()
        self._pm.pause()

    def resume_sim(self):
        """Resume simulation."""
        self._tls.resume()
        self._hls.resume()
        self._sss.resume()
        self._pm.resume()


class HLSTabView:
    """Houses loads simulation tab view.

    Args:
        root (tk.Tk): Tk window root.
        f_parent (ttk.Frame): Parent fram, master of the main frame.
        hls (HousesLoadsSimulator): Houses loads simulator instance.

    """

    def __init__(self, root: tk.Tk, f_parent: ttk.Frame, hls: HousesLoadsSimulator):
        self.root = root
        self._hls = hls

        self._hc_windows: dict[int, HouseControlsWindowView] = {}

        self._sv_system_load = ttk.StringVar(value="System Load: ? kW")
        self._sv_houses_loads = [
            ttk.StringVar(value="Load: ? KW")
            for _ in range(self._hls.num_houses)]
        self._iv_grid_lines = [
            ttk.IntVar(value=0)
            for _ in range(self._hls.num_houses)]
        self._iv_load_lines = [
            ttk.IntVar(value=0)
            for _ in range(self._hls.num_houses)]

        if self._hls.num_houses > 10:
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
            font=("Calibri", 18),
        ).pack(side="left")

        ttk.Label(
            f_main,
            textvariable=self._sv_system_load,
            font=("Calibri", 12),
        ).pack(side="right")

    def _build_body(self, f_parent: ttk.Frame):
        f_main = ttk.Frame(f_parent)
        f_main.pack(fill="both", expand=True)
        f_main.columnconfigure(list(range(5)), weight=1)

        for idx in range(self._hls.num_houses):
            f_house = ttk.Labelframe(
                f_main,
                padding=20,
                labelwidget=ttk.Label(
                    f_main,
                    text=f" House {idx + 1:02d} ",
                    font=("Calibri", 12),
                ),
            )
            f_house.grid(row=idx // 5, column=idx % 5, pady=(0, 20), padx=36)

            ttk.Label(
                f_house,
                textvariable=self._sv_houses_loads[idx],
                font=("Calibri", 12),
            ).pack(fill='x', pady=(0, 10))

            ttk.Checkbutton(
                f_house,
                text="Grid Line",
                variable=self._iv_grid_lines[idx],
                command=self._hls.houses[idx].toggle_grid_line,
                style="Primary.Roundtoggle.Toolbutton",
            ).pack(fill='x')

            ttk.Checkbutton(
                f_house,
                text="Load Line",
                variable=self._iv_load_lines[idx],
                command=self._hls.houses[idx].toggle_load_line,
                style="Primary.Roundtoggle.Toolbutton",
            ).pack(fill='x', pady=(0, 10))

            ttk.Button(
                f_house,
                text="Open Control Panel",
                command=lambda idx=idx: self.open_hc_window(idx),
                style="Primary.TButton",
            ).pack(fill='x')

    def _update_ui(self, dt: int):
        self._sv_system_load.set(
            f"System Load: {self._hls.system_load/1000:,.3f} kW")
        for idx, load in enumerate(self._sv_houses_loads):
            load.set(f"Load: {self._hls.houses[idx].load/1000:07,.3f} KW")
        for idx, line in enumerate(self._iv_grid_lines):
            line.set(int(self._hls.houses[idx].grid_line))
        for idx, line in enumerate(self._iv_load_lines):
            line.set(int(self._hls.houses[idx].load_line))

        self.root.after(dt, self._update_ui, dt)

    def open_hc_window(self, idx: int):
        """Open house controls window.

        Args:
            idx (int): House index.

        """
        if idx in self._hc_windows and self._hc_windows[idx].root.winfo_exists():
            self._hc_windows[idx].root.focus()
        else:
            self._hc_windows[idx] = HouseControlsWindowView(
                root=ttk.Toplevel(self.root),
                idx=idx,
                hls=self._hls,
                variables={
                    'total_load': self._sv_houses_loads[idx],
                    'grid_line': self._iv_grid_lines[idx],
                    'load_line': self._iv_load_lines[idx],
                }
            )


class HouseControlsWindowView:
    """House controls window view.

    Args:
        root (tk.Tk): Tk window root.
        idx (int): House index.
        hls (HousesLoadsSimulator): Houses loads simulator instance.
        variables (dict[str, ttk.Variable]): Passed UI variables, including:

                - "total_load" (ttk.StringVar): Total house load label text.
                - "grid_line" (ttk.IntVar): Grid line status (0 or 1).
                - "load_line" (ttk.IntVar): Load line status (0 or 1).

    """

    def __init__(self, root: tk.Tk, idx: int, hls: HousesLoadsSimulator,
                 variables: dict[str, ttk.Variable]):
        self.root = root
        self.root.title(f"House {idx + 1} Controls")
        self.root.geometry("600x600")
        self.root.resizable(False, False)
        self.idx = idx
        self._hls = hls
        self._house = self._hls.houses[self.idx]

        self._total_load: ttk.StringVar = variables['total_load']
        self._grid_line: ttk.IntVar = variables['grid_line']
        self._load_line: ttk.IntVar = variables['load_line']

        self._sv_devices_loads = {
            device_name: ttk.StringVar(value="Device Load: ? Watt")
            for device_name in self._house.devices.keys()
        }
        self._sv_devices_settings_multipliers = {
            device_name: ttk.StringVar(value="Setting Multiplier: ?")
            for device_name in self._house.devices.keys()
        }

        f_main = build_scrollable_frame(self.root, width=580, padding=10)

        self._build_header(f_main)
        self._build_body(f_main)

        self._update_ui(dt=100)

    def _build_header(self, f_parent: ttk.Frame):
        f_main = ttk.Frame(f_parent)
        f_main.pack(fill="x", pady=(0, 10))

        ttk.Label(
            f_main,
            text=f"House {self.idx + 1:02d} Control Panel",
            font=("Calibri", 24),
        ).pack()

        ttk.Label(
            f_main,
            textvariable=self._total_load,
            font=("Calibri", 12),
        ).pack(side="left")

        f_right = ttk.Frame(f_main)
        f_right.pack(side="right")

        ttk.Checkbutton(
            f_right,
            text="Grid Line",
            variable=self._grid_line,
            command=self._house.toggle_grid_line,
            style="Primary.Roundtoggle.Toolbutton",
        ).pack(side="left", padx=(0, 10))

        ttk.Checkbutton(
            f_right,
            text="Load Line",
            variable=self._load_line,
            command=self._house.toggle_load_line,
            style="Primary.Roundtoggle.Toolbutton",
        ).pack(side="left", padx=(0, 10))

    def _build_body(self, f_parent: ttk.Frame):
        f_main = ttk.Frame(f_parent)
        f_main.pack(fill="both")

        for dn, device in self._house.devices.items():

            f_device = ttk.Labelframe(
                f_main,
                padding=(10, 0),
                labelwidget=ttk.Label(
                    f_main,
                    text=f' {dn.replace(
                        '_', ' ').title()} Device Controls ',
                    font=("Calibri", 12),
                ),
            )
            f_device.pack(fill="x", pady=(0, 10))

            f_control = ttk.Frame(f_device)
            f_control.pack(fill="x", pady=(0, 10))

            ttk.Label(
                f_control,
                text="Number of Instances: ",
                font=("Calibri", 12),
            ).pack(side="left")

            spinbox = ttk.Spinbox(
                f_control,
                from_=0,
                to=device.conf.max_count,
                width=5,
                font=("Calibri", 8),
                style="Primary.TSpinbox",
            )
            spinbox.insert(0, device.count)
            spinbox.pack(side="left")
            spinbox.configure(
                command=lambda wid=spinbox, dn=dn:
                    self._house.devices[dn].update_count(
                        elapsed=self._hls.get_tls_elapsed(),
                        new_count=int(float(wid.get()))
                        if wid.get().strip() else 0,
                    ),
            )

            ttk.Label(
                f_control,
                textvariable=self._sv_devices_loads[dn],
                font=("Calibri", 12),
            ).pack(side="right")

            ttk.Label(
                f_device,
                text=device.conf,
                font=("Calibri", 8),
                style="Secondary.TLabel",
            ).pack(fill="x", pady=(0, 10))

            if device.conf.settings:
                f_settings = ttk.Labelframe(
                    f_device,
                    padding=(10, 0),
                    labelwidget=ttk.Label(
                        f_device,
                        text=" Settings ",
                        font=("Calibri", 12),
                    ),
                )
                f_settings.pack(fill="x", pady=(0, 10))

                for setting, all_options in device.conf.settings.options.items():
                    f_setting = ttk.Frame(f_settings)
                    f_setting.pack(fill="x", pady=(0, 10))

                    ttk.Label(
                        f_setting,
                        text=setting.replace('_', ' ').title()
                    ).pack(side="left")

                    sv_combo = ttk.StringVar()
                    combo = ttk.Combobox(
                        f_setting,
                        values=all_options,
                        state="readonly",
                        width=15,
                        textvariable=sv_combo,
                        style="Primary.TCombobox",
                    )
                    combo.set(device.current_settings[setting])
                    combo.pack(side="right")

                    sv_combo.trace_add(
                        'write',
                        lambda *_, wid=sv_combo, dn=dn, sn=setting:
                            self._house.devices[dn].update_setting(
                                setting_name=sn,
                                new_option=wid.get(),
                            ),
                    )

                    combo.bind(
                        '<<ComboboxSelected>>',
                        lambda *_, wid=sv_combo, dn=dn, sn=setting:
                            self._house.devices[dn].update_setting(
                                setting_name=sn,
                                new_option=wid.get(),
                            ),
                    )

                ttk.Label(
                    f_settings,
                    textvariable=self._sv_devices_settings_multipliers[dn],
                    font=("Calibri", 8),
                    style="Secondary.TLabel",
                ).pack(fill="x", pady=(0, 10))

    def _update_ui(self, dt):
        for device_name, load in self._sv_devices_loads.items():
            load.set(
                f"Device Load: {self._house.devices[device_name].load:,.1f} Watt")
        for device_name, multiplier in self._sv_devices_settings_multipliers.items():
            multiplier.set(
                f"Setting Multiplier: {self._house.devices[device_name].settings_multiplier:.1%}")

        self.root.after(dt, self._update_ui, dt)


class SSSTabView:
    """Solar system simulation tab view.

    Args:
        root (tk.Tk): Tk window root.
        f_parent (ttk.Frame): Parent fram, master of the main frame.
        sss (SolarSystemSimulator): Solar system simulator instance.

    """

    def __init__(self, root: tk.Tk, f_parent: ttk.Frame, sss: SolarSystemSimulator):
        self.root = root
        self.f_parent = f_parent
        self._sss = sss

        f_main = ttk.Frame(self.f_parent, padding=10)
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
            font=("Calibri", 18),
        ).pack(side="left")

    def _build_body(self, f_parent: ttk.Frame):
        f_main = ttk.Frame(f_parent)
        f_main.pack(fill="both", expand=True, pady=20, padx=20)
        f_main.place(relx=.5, rely=.5, anchor='center')

        self.output_text = ttk.Text(
            f_main,
            height=23,
            width=80,
            font=("Calibri", 12),
        )
        self.output_text.pack(fill='both')

    def _update_ui(self, dt: int):
        if self._sss.running:
            # Display real-time wattage output
            self.output_text.delete(1.0, ttk.END)
            self.output_text.insert(
                ttk.END, chars=f"{self._sss.pv_loc}\n\n")
            self.output_text.insert(
                ttk.END, chars=f"{self._sss.pv_conf}\n\n")
            self.output_text.insert(
                ttk.END, chars=f"{self._sss.batt.conf}\n\n")
            self.output_text.insert(
                ttk.END, chars=f"{self._sss.batt}\n\n")
            self.output_text.insert(
                ttk.END, chars=f"Zenith angle: {self._sss.zenith_angle:.2f}°\n")
            self.output_text.insert(
                ttk.END, chars=f"POA Irradiance: {self._sss.poa_irradiance:.2f}\n")
            self.output_text.insert(
                ttk.END, chars=f"Panel Power: {self._sss.panel_power:.2f} W\n")
            self.output_text.insert(
                ttk.END, chars=f"Total Power: {self._sss.total_power/1000:.3f} KW\n")

        self.root.after(dt, self._update_ui, dt)


class PMTabView:
    """Power management tab view.

    Args:
        root (tk.Tk): Tk window root.
        f_parent (ttk.Frame): Parent fram, master of the main frame.
        pm (PowerManager): Power manager instance.

    """

    def __init__(self, root: tk.Tk, f_parent: ttk.Frame, pm: PowerManager):
        self.root = root
        self.f_parent = f_parent
        self._pm = pm

        f_main = ttk.Frame(self.f_parent, padding=10)
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
            font=("Calibri", 18),
        ).pack(side="left")

    def _build_body(self, f_parent: ttk.Frame):
        f_main = ttk.Frame(f_parent)
        f_main.pack(fill="both", expand=True, pady=20, padx=20)
        f_main.place(relx=.5, rely=.5, anchor='center')

        self.output_text = ttk.Text(
            f_main,
            height=5,
            width=80,
            font=("Calibri", 12),
        )
        self.output_text.pack(fill='both')

    def _update_ui(self, dt: int):
        if self._pm.running:
            self.output_text.delete(1.0, ttk.END)
            self.output_text.insert(
                ttk.END, chars=f"Battery exchange power: {self._pm.batt_exchange_power:.2f} W\n")

        self.root.after(dt, self._update_ui, dt)


def build_scrollable_frame(f_parent: ttk.Frame, width=None, **kwargs) -> ttk.Frame:
    """Build and return a scrollable frame.

    Args:
        f_parent (ttk.Frame): Parent fram, master of the main frame.
        width (int): Minimum width for the scrollable frame.
        **kwargs: Keyword arguments to pass to scrollable frame when init.

    Returns:
        ttk.Frame: The scrollable frame.

    """
    f_main = ttk.Frame(f_parent)
    f_main.pack(fill="both", expand=True)

    canvas = ttk.Canvas(f_main)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(f_main, command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    f_scrollable = ttk.Frame(canvas, **kwargs)

    f_scrollable.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=f_scrollable, anchor="nw", width=width)
    canvas.configure(yscrollcommand=scrollbar.set)

    return f_scrollable
