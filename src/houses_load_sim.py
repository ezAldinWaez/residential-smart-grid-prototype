import tkinter as tk
import ttkbootstrap as ttk
import time
import threading

from data import DEVICES_CONFIG
from sim_time import SimulationTime

from device_state import DeviceState
from house_control import HouseControlWindow


# Time acceleration factor (1 second real time = TIME_FACTOR seconds simulation time)
TIME_FACTOR = 1


class HousesLoadSimulator:
    def __init__(self, parent: tk.Tk, *, num_houses: int):
        """
        Parameters
        ----------
        - master : tkinter app root.
        - num_houses : number of houses in the simulation.
        """

        self.parent = parent
        self.num_houses = num_houses
        self.sim_time = SimulationTime(TIME_FACTOR)
        self.houses_windows: dict[int, HouseControlWindow] = {}
        self.houses_devices = [
            {
                device_name: DeviceState(
                    base_wattage=config["wattage"],
                    adsr=config["adsr"],
                    settings=config.get('settings', None))
                for device_name, config in DEVICES_CONFIG.items()
            }
            for _ in range(self.num_houses)
        ]

        self.init_ui()

        self.running = True
        self.update_thread = threading.Thread(
            target=self.update_loads_periodically)
        self.update_thread.daemon = True
        self.update_thread.start()

    def init_ui(self):
        # Main Window
        self.parent.title("Houses Load Simulator")
        self.parent.attributes('-fullscreen', True)

        ttk.Style().theme_use('darkly')

        # Main Container
        main_container = ttk.Frame(self.parent, padding="20")
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

        # Houses Frame
        houses_frame = ttk.Frame(main_container)
        houses_frame.pack(fill="both", expand=True)

        self.houses_total_load = [
            ttk.StringVar(value="Total Load: - Watts")
            for _ in range(self.num_houses)
        ]

        # Configure grid columns to be 3 in row.
        for idx in range(3):
            houses_frame.columnconfigure(idx, weight=1)

        for idx in range(self.num_houses):
            # Create card-like frame for each house
            house_card = ttk.Frame(houses_frame, style="Card.TFrame")
            house_card.grid(row=idx//3, column=idx %
                            3, padx=10, pady=20, sticky="nsew")

            # House Title
            ttk.Label(
                house_card,
                text=f"House {idx + 1}",
                font=("Calibri", 16, "bold")
            ).pack(pady=10)

            # Total Load Display
            ttk.Label(
                house_card,
                textvariable=self.houses_total_load[idx],
                font=("Calibri", 12)
            ).pack(pady=10)

            # Control Panel Button
            ttk.Button(
                house_card,
                text="Open Control Panel",
                command=lambda idx=idx: self.open_house_control(idx),
                style="Accent.TButton"
            ).pack(pady=10)

        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

    def open_house_control(self, idx: int):
        if idx in self.houses_windows and self.houses_windows[idx].window.winfo_exists():
            self.houses_windows[idx].window.focus()
            return

        self.houses_windows[idx] = HouseControlWindow(
            self.parent,
            house_index=idx,
            total_load=self.houses_total_load[idx],
            device_states=self.houses_devices[idx],
            sim_time=self.sim_time
        )

    def on_closing(self):
        self.running = False

        # Close all house control windows
        for window in self.houses_windows.values():
            if window.window.winfo_exists():
                window.window.destroy()

        # Close Main Window
        self.parent.destroy()

    def update_loads_periodically(self):
        while self.running:
            current_sim_time = self.sim_time.get_time()
            self.time_display.set(
                f"Simulation Time: {current_sim_time.strftime('%H:%M:%S')}")

            total_system_load = 0
            for house_index in range(self.num_houses):
                total_house_load = 0
                for device_state in self.houses_devices[house_index].values():
                    curr_time = self.sim_time.get_elapsed()

                    device_state.active_envelopes = [
                        (state_toggle_time, state_toggle_load, is_active) for state_toggle_time, state_toggle_load, is_active in device_state.active_envelopes
                        if is_active or (curr_time - state_toggle_time <= device_state.adsr.r)
                    ]

                    curr_wattage = device_state.calc_current_wattage(self.sim_time)
                    device_state.setLoad(int(curr_wattage))
                    total_house_load += curr_wattage

                self.houses_total_load[house_index].set(f"Total Load: {int(total_house_load)} Watts")
                total_system_load += total_house_load

            self.total_power.set(f"Total Power: {total_system_load/1000:.2f} kW")
            time.sleep(0.1)
