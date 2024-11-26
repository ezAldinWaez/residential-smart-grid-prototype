import tkinter as tk
import ttkbootstrap as ttk

from solar_system_sim.sim import SolarSystemSimulator


class App:
    def __init__(self, sim: SolarSystemSimulator):
        self.sim = sim

        self.root = tk.Tk()
        self.root.title("Solar System Simulator")
        self.root.attributes('-fullscreen', True)

        ttk.Style().theme_use('darkly')

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
        self.sim.pause()
        self.root.destroy()

    def _update_ui(self, dt: int):
        self.time_display.set(
            f"Simulation Time: {self.sim.sim_time_loc.get_time().strftime('%H:%M:%S')}")
        self.total_power.set(
            f"Total Power: {self.sim.total_power/1000:.3f} kW")

        # Display real-time wattage output
        self.output_text.delete(1.0, tk.END)  # Clear previous output
        self.output_text.insert(
            tk.END, f"Location: {self.sim.sim_time_loc.loc_name} (lat: {self.sim.sim_time_loc.loc_lat}, lng: {self.sim.sim_time_loc.loc_lng}, alt: {self.sim.sim_time_loc.loc_alt})\n")
        self.output_text.insert(
            tk.END, f"Timezone: {self.sim.sim_time_loc.loc_tz}\n")
        self.output_text.insert(
            tk.END, f"Panel Area: {self.sim.panel_area} m²\n")
        self.output_text.insert(
            tk.END, f"Panel Efficiency: {self.sim.panel_efficiency:.1%}\n")
        self.output_text.insert(
            tk.END, f"Number of Panels: {self.sim.panels_count}\n")
        self.output_text.insert(
            tk.END, f"Zenith Angle: {self.sim.zenith_angle:.2f}°\n")
        self.output_text.insert(
            tk.END, f"Panel Power: {self.sim.panel_power:.2f} W\n")
        self.output_text.insert(
            tk.END, f"Total Power: {self.sim.total_power/1000:.3f} KW\n")

        self.root.after(dt, self._update_ui, 100)
