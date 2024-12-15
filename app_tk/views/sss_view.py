import tkinter as tk
import ttkbootstrap as ttk

# from app_tk.main import App


class SSSView:
    def __init__(self, root: tk.Tk, app):
        self.root = root
        self.app = app

        self.root.title("Solar System Simulator")
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

        # Total Power Gerenated Display
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

        # Output Area
        self.output_text = ttk.Text(
            body_frame, height=12, width=60, font=("Calibri", 14))
        self.output_text.pack(fill='both')

    def _on_closing(self):
        self.app.sss_sim.pause()
        self.root.destroy()

    def _update_ui(self, dt: int):
        self.time_display.set(
            f"Simulation Time: {self.app.sss_sim.sim_time_loc.get_time().strftime('%H:%M:%S')}")
        self.total_power.set(
            f"Total Power: {self.app.sss_sim.total_power/1000:.3f} kW")

        # Display real-time wattage output
        self.output_text.delete(1.0, ttk.END)  # Clear previous output
        self.output_text.insert(
            ttk.END, f"Location: {self.app.sss_sim.sim_time_loc.loc_name} (lat: {self.app.sss_sim.sim_time_loc.loc_lat}, lng: {self.app.sss_sim.sim_time_loc.loc_lng}, alt: {self.app.sss_sim.sim_time_loc.loc_alt})\n")
        self.output_text.insert(
            ttk.END, f"Timezone: {self.app.sss_sim.sim_time_loc.loc_tz}\n")
        self.output_text.insert(
            ttk.END, f"Panel Area: {self.app.sss_sim.panel_area} m²\n")
        self.output_text.insert(
            ttk.END, f"Panel Efficiency: {self.app.sss_sim.panel_efficiency:.1%}\n")
        self.output_text.insert(
            ttk.END, f"Number of Panels: {self.app.sss_sim.panels_count}\n")
        self.output_text.insert(
            ttk.END, f"Zenith Angle: {self.app.sss_sim.zenith_angle:.2f}°\n")
        self.output_text.insert(
            ttk.END, f"Panel Power: {self.app.sss_sim.panel_power:.2f} W\n")
        self.output_text.insert(
            ttk.END, f"Total Power: {self.app.sss_sim.total_power/1000:.3f} KW\n")

        self.root.after(dt, self._update_ui, dt)
