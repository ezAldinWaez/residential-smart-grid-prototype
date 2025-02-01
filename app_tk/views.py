import ttkbootstrap as ttk
from ttkbootstrap.widgets import Notebook


class MainView:
    def __init__(self, app):
        self.app = app

        main_frame = ttk.Frame(self.app.root, padding="10")
        main_frame.pack(fill="both", expand=True)

        self._build_header(main_frame)
        self._build_body(main_frame)

        self._update_ui(100)  # Update view every 100 ms

    def _build_header(self, main_frame: ttk.Frame):
        # Header Frame
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 10))

        # Simulation Time Display
        self.time_display = ttk.StringVar(value="Simulation Time: --:--:--")
        ttk.Label(
            header_frame,
            textvariable=self.time_display,
            font=("Calibri", 14)
        ).pack(side="left")

        # Buttons Menue Frame
        buttons_menue_frame = ttk.Frame(header_frame)
        buttons_menue_frame.pack(side="right")

        # Pause Simulation Button
        ttk.Button(
            buttons_menue_frame,
            text="Pause Simulation",
            command=self.app.pause_sim
        ).pack(side="left", padx=10)

        # Resume Simulation Button
        ttk.Button(
            buttons_menue_frame,
            text="Resume Simulation",
            command=self.app.resume_sim
        ).pack(side="left", padx=10)

    def _build_body(self, main_frame: ttk.Frame):
        # Body Notebook (Tabbed Interface)
        body_notebook = Notebook(main_frame, style='primary')
        body_notebook.pack(fill='both', expand=True)

        # Houses Loads Tab
        houses_load_frame = ttk.Frame(body_notebook)
        SHLView(houses_load_frame, self.app)
        body_notebook.add(houses_load_frame, text='Houses Load Simulation')

        # Solar System Tab
        solar_system_frame = ttk.Frame(body_notebook)
        SSSView(solar_system_frame, self.app)
        body_notebook.add(solar_system_frame, text='Solar System Simulation')

    def _update_ui(self, dt: int):
        self.time_display.set(
            f"Simulation Time: {self.app.stl.get_time().strftime('%H:%M:%S')}")

        self.app.root.after(dt, self._update_ui, dt)


class SHLView:
    def __init__(self, parent_frame: ttk.Frame, app):
        self.parent_frame = parent_frame
        self.app = app

        main_frame = ttk.Frame(self.parent_frame, padding=10)
        main_frame.pack(fill="both", expand=True)

        self._build_header(main_frame)
        self._build_body(main_frame)

        self._update_ui(100)  # Update view every 100 ms

    def _build_header(self, main_frame: ttk.Frame):
        # Header Frame
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 10))

        # Total Power Consumption Display
        self.total_power = ttk.StringVar(value="Total Load Power: - kW")
        ttk.Label(
            header_frame,
            textvariable=self.total_power,
            font=("Calibri", 14)
        ).pack(side="left")

    def _build_body(self, main_frame: ttk.Frame):
        # Body Frame
        body_frame = ttk.Frame(main_frame)
        body_frame.pack(fill="both", expand=True, pady=10, padx=10)

        self.houses_windows: dict[int, SHLControlsView] = {}

        self.houses_total_load = [
            ttk.StringVar(value="Total Load Power: - KW")
            for _ in range(self.app.shl.num_houses)
        ]

        # Configure grid columns to be 4 in row.
        for i in range(4):
            body_frame.columnconfigure(i, weight=1)

        # Configure grid rows to be 3 in column.
        for i in range(3):
            body_frame.rowconfigure(i, weight=1)

        for i in range(self.app.shl.num_houses):
            # Create card-like frame for each house
            house_card = ttk.Frame(body_frame, style="Card.TFrame")
            house_card.grid(row=i // 4, column=i % 4)

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
                command=lambda idx=i: self._open_house_control(idx),
                style="Accent.TButton"
            ).pack(pady=10)

    def _open_house_control(self, idx: int):
        if idx in self.houses_windows and self.houses_windows[idx].root.winfo_exists():
            self.houses_windows[idx].root.focus()
        else:
            toplevel_window = ttk.Toplevel(self.app.root)
            toplevel_window.title(f"House {idx + 1} Controls")
            toplevel_window.geometry("600x600")
            toplevel_window.minsize(600, 600)

            self.houses_windows[idx] = SHLControlsView(
                root=toplevel_window,
                parent_view=self,
                idx=idx)

    def _update_ui(self, dt: int):
        self.total_power.set(
            f"Total Load Power: {self.app.shl.system_load/1000:.3f} kW")
        for house_idx, house_total_load in enumerate(self.houses_total_load):
            house_total_load.set(
                f"Total Load Power: {self.app.shl.houses_loads[house_idx]/1000:.3f} KW")
        for house_idx, window in self.houses_windows.items():
            if window.root.winfo_exists():
                for device_name, device_load in window.device_loads.items():
                    device_load.set(
                        f"{self.app.shl.houses_devices_states[house_idx][device_name].total_load:.1f} Watt")

        self.app.root.after(dt, self._update_ui, dt)


class SHLControlsView:
    def __init__(self, root, parent_view, idx: int):
        self.root = root
        self.parent_view = parent_view
        self.idx = idx

        self.total_load = self.parent_view.houses_total_load[self.idx]
        self.device_states = self.parent_view.app.shl.houses_devices_states[self.idx]

        main_frame = self._build_scrollable_container(self.root)

        self._build_dody(main_frame)

    def _build_scrollable_container(self, root: ttk.Frame) -> ttk.Frame:
        # Canvas and Scrollbar
        container = ttk.Frame(root)
        container.pack(fill="both", expand=True)
        self.canvas = ttk.Canvas(container)
        scrollbar = ttk.Scrollbar(
            container,
            orient="vertical",
            command=self.canvas.yview)

        # Main Container
        main_container = ttk.Frame(self.canvas, padding="20")

        # Configure scrolling and canvas
        main_container.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window(
            (0, 0), window=main_container, anchor="nw", width=580)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        return main_container

    def _build_dody(self, main_frame: ttk.Frame):
        # House Title
        ttk.Label(
            main_frame,
            text=f"House {self.idx + 1} Control Panel",
            font=("Calibri", 16, "bold")
        ).pack(pady=(0, 20))

        # Total Load Display
        total_frame = ttk.Frame(main_frame)
        total_frame.pack(fill="x", pady=20)
        ttk.Label(
            total_frame,
            textvariable=self.total_load,
            font=("Calibri", 12, "bold")
        ).pack()

        self.device_loads = {
            device_name: ttk.StringVar(value="- Watt")
            for device_name in self.device_states.keys()
        }

        # Devices Controls
        for device_name, device_state in self.device_states.items():

            # Device Frame
            device_frame = ttk.LabelFrame(
                main_frame,
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
                text=f"Base Power: {device_state.device_info.max_watt}W",
                width=20
            ).pack(side="left", padx=5)

            # Device Count Spinbox
            spinbox = ttk.Spinbox(
                control_frame,
                from_=0,
                to=device_state.device_info.max_count,
                width=5,
            )
            spinbox.pack(side="left", padx=10)
            spinbox.insert(0, device_state.count)

            def update_count_value(wid: ttk.Spinbox, dn: str):
                self.device_states[dn].update_count(
                    elapsed=self.parent_view.app.stl.get_elapsed(),
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
            if device_state.device_info.settings:
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
                    factor = self.device_states[dn].settings_multiplier
                    wid.set(f"Current Power Factor: {factor:.2f}x")

                # Initial update
                update_power_factor_label(power_factor, device_name)

                # Create controls for each setting
                for setting_name, possible_values in device_state.device_info.settings.options.items():
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


class SSSView:
    def __init__(self, parent_frame: ttk.Frame, app):
        self.parent_frame = parent_frame
        self.app = app

        main_frame = ttk.Frame(self.parent_frame, padding="10")
        main_frame.pack(fill="both", expand=True)

        self._build_body(main_frame)

        self._update_ui(100)  # Update view every 100 ms

    def _build_body(self, main_frame: ttk.Frame):
        # Body Frame
        body_frame = ttk.Frame(main_frame)
        body_frame.pack(fill="both", expand=True, pady=20, padx=20)
        body_frame.place(relx=.5, rely=.5, anchor='center')

        # Output Area
        self.output_text = ttk.Text(
            body_frame, height=20, width=80, font=("Calibri", 14))
        self.output_text.pack(fill='both')

    def _update_ui(self, dt: int):
        # Display real-time wattage output
        self.output_text.delete(1.0, ttk.END)  # Clear previous output
        self.output_text.insert(
            ttk.END, f"Location: {self.app.stl.loc_name} (lat: {self.app.stl.loc_info.lat}, lng: {self.app.stl.loc_info.lng}, alt: {self.app.stl.loc_info.alt})\n")
        self.output_text.insert(
            ttk.END, f"Timezone: {self.app.stl.loc_info.tz_name}\n")
        self.output_text.insert(
            ttk.END, f"Panel Area: {self.app.sss.pv_conf.panel_area} m²\n")
        self.output_text.insert(
            ttk.END, f"Panel Efficiency: {self.app.sss.pv_conf.panel_efficiency:.1%}\n")
        self.output_text.insert(
            ttk.END, f"Number of Panels: {self.app.sss.pv_conf.panels_count}\n")
        self.output_text.insert(
            ttk.END, f"Zenith Angle: {self.app.sss.zenith_angle:.2f}°\n")
        self.output_text.insert(
            ttk.END, f"Panel Power: {self.app.sss.panel_power:.2f} W\n")
        self.output_text.insert(
            ttk.END, f"Total Power: {self.app.sss.total_power/1000:.3f} KW\n")

        self.app.root.after(dt, self._update_ui, dt)
