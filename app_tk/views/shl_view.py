import tkinter as tk
import ttkbootstrap as ttk

# from app_tk.main import App
from app_tk.views.shl_controls_view import SHLControlsView


class SHLView:
    def __init__(self, root: tk.Tk, app):
        self.root = root
        self.app = app

        self.shl_sim = app.shl_sim

        self.root.title("Houses Load Simulator")
        self.root.attributes('-fullscreen', True)

        main_container = ttk.Frame(self.root, padding="20")
        main_container.pack(fill="both", expand=True)
        self._build_header(main_container)
        self._build_body(main_container)

        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        self._update_ui(100)  # Update UI every 100 ms

    def _build_header(self, root: ttk.Frame):
        # Header Frame
        header_frame = ttk.Frame(root)
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

    def _build_body(self, root: ttk.Frame):
        # Body Frame
        body_frame = ttk.Frame(root)
        body_frame.pack(fill="both", expand=True, pady=20, padx=20)
        body_frame.place(relx=.5, rely=.5, anchor='center')

        self.houses_windows: dict[int, SHLControlsView] = {}

        self.houses_total_load = [
            ttk.StringVar(value="Total Load: - Watts")
            for _ in range(self.shl_sim.num_houses)
        ]

        # Configure grid columns to be 3 in row.
        for i in range(3):
            body_frame.columnconfigure(i, weight=1)

        for i in range(self.shl_sim.num_houses):
            # Create card-like frame for each house
            house_card = ttk.Frame(body_frame, style="Card.TFrame")
            house_card.grid(row=i//3, column=i %
                            3, ipadx=40, pady=20, sticky="nsew")

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
            self.houses_windows[idx] = SHLControlsView(
                root=ttk.Toplevel(self.root),
                idx=idx,
                parent=self
            )

    def _on_closing(self):
        self.shl_sim.pause()

        # Close all house control windows
        for window in self.houses_windows.values():
            if window.root.winfo_exists():
                window.root.destroy()

        # Close Main Window
        self.root.destroy()

    def _update_ui(self, dt: int):
        self.time_display.set(
            f"Simulation Time: {self.shl_sim.sim_time_loc.get_time().strftime('%H:%M:%S')}")
        self.total_power.set(
            f"Total Power: {self.shl_sim.system_load/1000:.3f} kW")
        for idx, house_total_load in enumerate(self.houses_total_load):
            house_total_load.set(
                f"Total Load: {self.shl_sim.houses_loads[idx]:.1f} Watts")
        for idx, window in enumerate(self.houses_windows.values()):
            if window.root.winfo_exists():
                for device_name, device_load in window.device_loads.items():
                    device_load.set(
                        f"{self.shl_sim.houses_device_states[idx][device_name].total_load:.1f} Watt")

        self.root.after(dt, self._update_ui, dt)
