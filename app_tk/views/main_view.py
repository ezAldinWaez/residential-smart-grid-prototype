import ttkbootstrap as ttk
from ttkbootstrap.widgets import Notebook

from app_tk.views.shl_view import SHLView
from app_tk.views.sss_view import SSSView


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
            f"Simulation Time: {self.app.sim_time_loc.get_time().strftime('%H:%M:%S')}")

        self.app.root.after(dt, self._update_ui, dt)
