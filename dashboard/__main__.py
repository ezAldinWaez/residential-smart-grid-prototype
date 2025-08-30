"""Dashboard main."""

from .app import DashboardApp

app = DashboardApp()

try:
    app.mainloop()
except KeyboardInterrupt:
    app.destroy()
