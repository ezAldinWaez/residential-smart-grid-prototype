import tkinter as tk
import ttkbootstrap as ttk

from device_state import DeviceState
from sim_time import SimulationTime
from data import DEVICES_CONFIG


class HouseControlWindow:
    def __init__(self, parent, *, house_index: int, total_load: tk.StringVar,
                 device_states: dict[str, DeviceState], sim_time: SimulationTime):

        self.parent = parent
        self.idx = house_index
        self.total_load = total_load
        self.device_states = device_states
        self.sim_time = sim_time

        self.init_ui()

    def init_ui(self):
        # Control Panel Window
        self.window = ttk.Toplevel(self.parent)
        self.window.title(f"House {self.idx + 1} Controls")
        self.window.geometry("600x600")
        self.window.minsize(600, 600)

        # Store references to prevent garbage collection
        self.device_widgets = {}

        # Canvas and Scrollbar
        container = ttk.Frame(self.window)
        container.pack(fill="both", expand=True)
        self.canvas = ttk.Canvas(container)
        scrollbar = ttk.Scrollbar(
            container,
            orient="vertical",
            command=self.canvas.yview)

        # Main Frame
        self.main_frame = ttk.Frame(self.canvas, padding="20")

        # Configure scrolling and canvas
        self.main_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        self.canvas.create_window(
            (0, 0),
            window=self.main_frame,
            anchor="nw",
            width=580)
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
            self.device_widgets[device_name] = {}

            self.create_device_section(
                device_name=device_name,
                device_state=device_state,
            )

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.canvas.unbind_all("<MouseWheel>")
        self.window.destroy()

    def create_device_section(self, device_name: str, device_state: DeviceState):
        """Create a section for each device with its controls"""
        config = DEVICES_CONFIG[device_name]

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
            text=f"Base Power: {config['wattage']}W",
            width=20
        ).pack(side="left", padx=5)

        # Device Count Spinbox
        spinbox = ttk.Spinbox(
            control_frame,
            from_=0,
            to=config['max_count'],
            width=5,
        )
        spinbox.pack(side="left", padx=10)
        spinbox.insert(0, device_state.count)
        self.device_widgets[device_name]['spinbox'] = spinbox

        def update_count_value():
            device_state.update_count_and_active_envelopes(
                sim_time=self.sim_time,
                value=spinbox.get().strip())

        spinbox.configure(command=update_count_value)

        # Device Load Label
        load_label = ttk.Label(
            control_frame,
            textvariable=device_state.loadStr,
            width=15)
        load_label.pack(side="left", padx=5)
        self.device_widgets[device_name]['load_label'] = load_label

        # Settings Controls
        if device_state.settings:
            # Setting Frame
            settings_frame = ttk.LabelFrame(
                device_frame,
                text=f" {device_name} Settings ",
                padding=5)
            settings_frame.pack(fill="x", pady=(10, 0))

            self.device_widgets[device_name]['settings'] = {}

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

                # Store combo reference
                self.device_widgets[device_name]['settings'][setting_name] = combo
                device_state.settings_controls[setting_name] = combo

                setting.trace_add('write', lambda *args, name=setting_name, widget=setting: device_state.update_setting(name, widget.get()))
                combo.bind(
                    '<<ComboboxSelected>>',
                    lambda e, name=setting_name: device_state.update_setting(name, e.get()))

            # Power Factor Frame
            factor_frame = ttk.Frame(device_frame)
            factor_frame.pack(fill="x", pady=(10, 0))

            # Power Factor Label
            power_factor = ttk.StringVar(value="Current Power Factor: ---")
            ttk.Label(
                factor_frame,
                textvariable=power_factor
            ).pack(side="left")
            self.device_widgets[device_name]['power_factor'] = power_factor

            # Update power factor label when settings change
            def update_power_factor_label():
                factor = device_state.get_settings_multiplier()
                power_factor.set(f"Current Power Factor: {factor:.2f}x")

            # Bind updates to each settings control
            for combo in device_state.settings_controls.values():
                combo.bind('<<ComboboxSelected>>',
                           lambda e: update_power_factor_label())

            # Initial update
            update_power_factor_label()
