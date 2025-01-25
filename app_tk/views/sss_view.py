import ttkbootstrap as ttk


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

        self.app.root.after(dt, self._update_ui, dt)
