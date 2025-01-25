import ttkbootstrap as ttk


class SHLControlsView:
    def __init__(self, root, parent_view, idx: int):
        self.root = root
        self.parent_view = parent_view
        self.idx = idx

        self.total_load = self.parent_view.houses_total_load[self.idx]
        self.device_states = self.parent_view.app.shl_sim.houses_device_states[self.idx]

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
                    elapsed=self.parent_view.app.sim_time_loc.get_elapsed(),
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
