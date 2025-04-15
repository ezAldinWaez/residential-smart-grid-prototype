from admin_dashboard import AdminDashboardApp
from rsgp import rsgp_main


def main():
    """Main."""
    (
        time_sim,
        houses_loads_sim,
        solar_system_sim,
        power_mng
    ) = rsgp_main()

    app = AdminDashboardApp(
        time_sim,
        houses_loads_sim,
        solar_system_sim,
        power_mng
    )
    app.mainloop()


if __name__ == "__main__":
    main()
