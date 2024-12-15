import tkinter as tk
import ttkbootstrap as ttk

from sim_time_loc.sim_time_loc import SimulationTimeLocation
from houses_loads_sim.sim import HousesLoadsSimulator
from solar_system_sim.sim import SolarSystemSimulator

from houses_loads_sim_app.gui import HLSApp
from solar_system_sim_app.gui import SSSApp


class App:
    def __init__(self, sim_time_loc: SimulationTimeLocation, hls_sim: HousesLoadsSimulator, sss_sim: SolarSystemSimulator):
        self.sim_time_loc = sim_time_loc
        self.hls_sim = hls_sim
        self.sss_sim = sss_sim

        self.root = tk.Tk()
        self.root.title("...")
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

        # Buttons Menue Frame
        buttons_menue_frame = ttk.Frame(header_frame)
        buttons_menue_frame.pack(anchor="center", padx=10)

        # Pause Simulation Button
        ttk.Button(
            buttons_menue_frame,
            text="Pause Simulation",
            command=self.pause_sim
        ).pack(side="left", padx=10)

        # Resume Simulation Button
        ttk.Button(
            buttons_menue_frame,
            text="Resume Simulation",
            command=self.resume_sim
        ).pack(side="left", padx=10)

    def _build_body(self, root: ttk.Frame):
        # Body Frame
        body_frame = ttk.Frame(root)
        body_frame.pack(fill="both", expand=True, pady=20, padx=20)
        body_frame.place(relx=.5, rely=.5, anchor='center')

        # Open HLS Button
        ttk.Button(
            body_frame,
            text="Open Houses Loads Simulator",
            command=lambda: HLSApp(tk.Toplevel(self.root), self.hls_sim),
            style="Accent.TButton"
        ).pack(pady=10, padx=10)

        # Open SSS Button
        ttk.Button(
            body_frame,
            text="Open Solar System Simulator",
            command=lambda: SSSApp(tk.Toplevel(self.root), self.sss_sim),
            style="Accent.TButton"
        ).pack(pady=10, padx=10)

    def pause_sim(self):
        self.sim_time_loc.pause()
        self.hls_sim.pause()
        self.sss_sim.pause()

    def resume_sim(self):
        self.sim_time_loc.resume()
        self.hls_sim.resume()
        self.sss_sim.resume()

    def _on_closing(self):
        self.pause_sim()
        self.root.destroy()


    def _update_ui(self, dt: int):
        self.time_display.set(
            f"Simulation Time: {self.sim_time_loc.get_time().strftime('%H:%M:%S')}")

        self.root.after(dt, self._update_ui, dt)
