import tkinter as tk
import ttkbootstrap as ttk

# from app_tk.main import App
from app_tk.views.shl_view import SHLView
from app_tk.views.sss_view import SSSView


class MainView:
    def __init__(self, root: tk.Tk, app):
        self.root = root
        self.app = app

        self.root.title("Residential Smart Grid Simulator")
        self.root.attributes('-fullscreen', True)

        ttk.Style().theme_use('darkly')

        main_container = ttk.Frame(self.root, padding="20")
        main_container.pack(fill="both", expand=True)
        self._build_header(main_container)
        self._build_body(main_container)

        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        self._update_ui(100)

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
            command=self.app.pause_sim
        ).pack(side="left", padx=10)

        # Resume Simulation Button
        ttk.Button(
            buttons_menue_frame,
            text="Resume Simulation",
            command=self.app.resume_sim
        ).pack(side="left", padx=10)

    def _build_body(self, root: ttk.Frame):
        # Body Frame
        body_frame = ttk.Frame(root)
        body_frame.pack(fill="both", expand=True, pady=20, padx=20)
        body_frame.place(relx=.5, rely=.5, anchor='center')

        # Open SHL Button
        ttk.Button(
            body_frame,
            text="Open Houses Loads Simulator",
            command=lambda: SHLView(tk.Toplevel(self.root), self.app),
            style="Accent.TButton"
        ).pack(pady=10, padx=10)

        # Open SSS Button
        ttk.Button(
            body_frame,
            text="Open Solar System Simulator",
            command=lambda: SSSView(tk.Toplevel(self.root), self.app),
            style="Accent.TButton"
        ).pack(pady=10, padx=10)

    def _on_closing(self):
        self.app.pause_sim()
        self.root.destroy()

    def _update_ui(self, dt: int):
        self.time_display.set(
            f"Simulation Time: {self.app.sim_time_loc.get_time().strftime('%H:%M:%S')}")

        self.root.after(dt, self._update_ui, dt)
