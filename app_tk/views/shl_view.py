import ttkbootstrap as ttk

from app_tk.views.shl_controls_view import SHLControlsView


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
            for _ in range(self.app.shl_sim.num_houses)
        ]

        # Configure grid columns to be 4 in row.
        for i in range(4):
            body_frame.columnconfigure(i, weight=1)

        # Configure grid rows to be 3 in column.
        for i in range(3):
            body_frame.rowconfigure(i, weight=1)

        for i in range(self.app.shl_sim.num_houses):
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
            f"Total Load Power: {self.app.shl_sim.system_load/1000:.3f} kW")
        for idx, house_total_load in enumerate(self.houses_total_load):
            house_total_load.set(
                f"Total Load Power: {self.app.shl_sim.houses_loads[idx]/1000:.3f} KW")
        for idx, window in enumerate(self.houses_windows.values()):
            if window.root.winfo_exists():
                for device_name, device_load in window.device_loads.items():
                    device_load.set(
                        f"{self.app.shl_sim.houses_device_states[idx][device_name].total_load:.1f} Watt")

        self.app.root.after(dt, self._update_ui, dt)
