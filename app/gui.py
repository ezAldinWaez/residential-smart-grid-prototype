import tkinter as tk
import ttkbootstrap as ttk

from houses_loads_sim.sim import HousesLoadsSimulator


class App:
    def __init__(self, sim: HousesLoadsSimulator):
        self.sim = sim

        self.houses_windows: dict[int, HouseControlWindow] = {}

        self.root = tk.Tk()
        self.root.title("Houses Load Simulator")
        self.root.attributes('-fullscreen', True)

        ttk.Style().theme_use('darkly')

        # Main Container
        main_container = ttk.Frame(self.root, padding="20")
        main_container.pack(fill="both", expand=True)

        # Header Frame
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill="x", pady=(0, 20))

        # Simulation Time Display
        self.time_display = ttk.StringVar(value="Simulation Time: --:--:--")
        ttk.Label(
            header_frame,
            textvariable=self.time_display,
            font=("Calibri", 14)
        ).pack(side="left")

        # Total Power Consumption Display
        self.total_power = ttk.StringVar(value="Total Power: - kW")
        ttk.Label(
            header_frame,
            textvariable=self.total_power,
            font=("Calibri", 14)
        ).pack(side="right")

        # Buttons Menue Frame
        buttons_menue_frame = ttk.Frame(header_frame)
        buttons_menue_frame.pack(anchor="center", padx=10)

        # Pause Simulation Button
        ttk.Button(
            buttons_menue_frame,
            text="Pause Simulation",
            command=self.sim.pause
        ).pack(side="left", padx=10)

        # Resume Simulation Button
        ttk.Button(
            buttons_menue_frame,
            text="Resume Simulation",
            command=self.sim.resume
        ).pack(side="left", padx=10)

        # Houses Frame
        houses_frame = ttk.Frame(main_container)
        houses_frame.pack(fill="both", expand=True)

        self.houses_total_load = [
            ttk.StringVar(value="Total Load: - Watts")
            for _ in range(self.sim.num_houses)
        ]

        # Configure grid columns to be 3 in row.
        for i in range(3):
            houses_frame.columnconfigure(i, weight=1)

        for i in range(self.sim.num_houses):
            # Create card-like frame for each house
            house_card = ttk.Frame(houses_frame, style="Card.TFrame")
            house_card.grid(row=i//3, column=i %
                            3, padx=10, pady=20, sticky="nsew")

            # House Title
            ttk.Label(
                house_card,
                text=f"House {i + 1}",
                font=("Calibri", 16, "bold")
            ).pack(pady=10)

            # Total Load Display
            ttk.Label(
                house_card,
                textvariable=self.houses_total_load[i],
                font=("Calibri", 12)
            ).pack(pady=10)

            # Control Panel Button
            ttk.Button(
                house_card,
                text="Open Control Panel",
                command=lambda idx=i: self.open_house_control(idx),
                style="Accent.TButton"
            ).pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.update_ui()

    def open_house_control(self, idx: int):
        if idx in self.houses_windows and self.houses_windows[idx].root.winfo_exists():
            self.houses_windows[idx].root.focus()
        else:
            self.houses_windows[idx] = HouseControlWindow(self, idx=idx)

    def on_closing(self):
        self.sim.pause()

        # Close all house control windows
        for window in self.houses_windows.values():
            if window.root.winfo_exists():
                window.root.destroy()

        # Close Main Window
        self.root.destroy()

    def update_ui(self):
        self.time_display.set(
            f"Simulation Time: {self.sim.current_sim_time.strftime('%H:%M:%S')}")
        self.total_power.set(
            f"Total Power: {self.sim.system_load/1000:.3f} kW")
        for idx, house_total_load in enumerate(self.houses_total_load):
            house_total_load.set(
                f"Total Load: {self.sim.houses_loads[idx]:.1f} Watts")
        for idx, window in enumerate(self.houses_windows.values()):
            if window.root.winfo_exists():
                for device_name, device_load in window.device_loads.items():
                    device_load.set(
                        f"{self.sim.houses_device_states[idx][device_name].total_load:.1f} Watt")

        self.root.after(100, self.update_ui)


class HouseControlWindow:
    def __init__(self, app: App, *, idx: int):
        self.app = app
        self.idx = idx
        self.total_load = self.app.houses_total_load[self.idx]
        self.device_states = self.app.sim.houses_device_states[self.idx]

        # Root
        self.root = ttk.Toplevel(self.app.root)
        self.root.title(f"House {self.idx + 1} Controls")
        self.root.geometry("600x600")
        self.root.minsize(600, 600)

        self.device_loads = {
            device_name: ttk.StringVar(value="- Watt")
            for device_name in self.device_states.keys()
        }

        # Canvas and Scrollbar
        container = ttk.Frame(self.root)
        container.pack(fill="both", expand=True)
        self.canvas = ttk.Canvas(container)
        scrollbar = ttk.Scrollbar(
            container,
            orient="vertical",
            command=self.canvas.yview)

        # Main Frame
        self.main_frame = ttk.Frame(self.canvas, padding="20")

        # Configure scrolling and canvas
        self.main_frame.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.canvas.bind_all(
            "<MouseWheel>", lambda e: self.canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        self.canvas.create_window(
            (0, 0), window=self.main_frame, anchor="nw", width=580)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # House Title
        ttk.Label(
            self.main_frame,
            text=f"House {self.idx + 1} Control Panel",
            font=("Calibri", 16, "bold")
        ).pack(pady=(0, 20))

        # Total Load Display
        total_frame = ttk.Frame(self.main_frame)
        total_frame.pack(fill="x", pady=20)
        ttk.Label(
            total_frame,
            textvariable=self.total_load,
            font=("Calibri", 12, "bold")
        ).pack()

        # Devices Controls
        for device_name, device_state in self.device_states.items():

            # Device Frame
            device_frame = ttk.LabelFrame(
                self.main_frame,
                text=f' {device_name} Controls ',
                padding="10"
            )
            device_frame.pack(fill="x", pady=10)

            # Control Frame
            control_frame = ttk.Frame(device_frame)
            control_frame.pack(fill="x", pady=(0, 10))

            # Device Base Wattage Label
            ttk.Label(
                control_frame,
                text=f"Base Power: {device_state.base_wattage}W",
                width=20
            ).pack(side="left", padx=5)

            # Device Count Spinbox
            spinbox = ttk.Spinbox(
                control_frame,
                from_=0,
                to=device_state.max_count,
                width=5,
            )
            spinbox.pack(side="left", padx=10)
            spinbox.insert(0, device_state.count)

            def update_count_value(wid: ttk.Spinbox, dn: str):
                self.device_states[dn].update_count_and_active_envelopes(
                    elapsed=self.app.sim.sim_time.get_elapsed(),
                    value=wid.get().strip()
                )

            spinbox.configure(
                command=lambda wid=spinbox, dn=device_name: update_count_value(wid, dn))

            # Device Load Label
            load_label = ttk.Label(
                control_frame,
                textvariable=self.device_loads[device_name],
                width=15)
            load_label.pack(side="left", padx=5)

            # Settings Controls
            if device_state.settings:
                # Setting Frame
                settings_frame = ttk.LabelFrame(
                    device_frame,
                    text=f" {device_name} Settings ",
                    padding=5)
                settings_frame.pack(fill="x", pady=(10, 0))

                # Power Factor Frame
                factor_frame = ttk.Frame(settings_frame)
                factor_frame.pack(fill="x", pady=(10, 0))

                # Power Factor Label
                power_factor = ttk.StringVar(value="Current Power Factor: ---")
                ttk.Label(
                    factor_frame,
                    textvariable=power_factor
                ).pack(side="left")

                def update_power_factor_label(wid: ttk.StringVar, dn: str):
                    factor = self.device_states[dn].calc_settings_multiplier()
                    wid.set(f"Current Power Factor: {factor:.2f}x")

                # Initial update
                update_power_factor_label(power_factor, device_name)

                # Create controls for each setting
                for setting_name, possible_values in device_state.settings.options.items():
                    # Setting Frame
                    setting_frame = ttk.Frame(settings_frame)
                    setting_frame.pack(fill="x", pady=2)

                    # Setting Label
                    ttk.Label(
                        setting_frame,
                        text=setting_name.replace('_', ' ').title()
                    ).pack(side="left", padx=5)

                    # Setting Var
                    setting = ttk.StringVar()
                    # Setting Combobox
                    combo = ttk.Combobox(
                        setting_frame,
                        values=possible_values,
                        state="readonly",
                        width=15,
                        textvariable=setting
                    )
                    combo.set(device_state.current_settings[setting_name])
                    combo.pack(side="right", padx=5)

                    def update_setting(wid: ttk.Combobox, dn: str, sn: str):
                        self.device_states[dn].update_setting(sn, wid.get())

                    setting.trace_add('write', lambda *args, wid=setting,
                                      dn=device_name, sn=setting_name: update_setting(wid, dn, sn))
                    combo.bind('<<ComboboxSelected>>', lambda e, wid=setting,
                               dn=device_name, sn=setting_name: update_setting(wid, dn, sn))

                    combo.bind('<<ComboboxSelected>>', lambda e, wid=power_factor,
                               dn=device_name: update_power_factor_label(wid, dn))

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.canvas.unbind_all("<MouseWheel>")
        self.root.destroy()
