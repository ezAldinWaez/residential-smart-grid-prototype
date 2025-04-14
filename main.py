from admin_dashboard import AdminDashboardApp
from rsg_prototype import rsg_prototype_main


def main():
    """Main."""
    (
        time_sim,
        houses_loads_sim,
        solar_system_sim,
        power_mng
    ) = rsg_prototype_main()

    app = AdminDashboardApp(
        time_sim,
        houses_loads_sim,
        solar_system_sim,
        power_mng
    )
    app.mainloop()


if __name__ == "__main__":
    main()
