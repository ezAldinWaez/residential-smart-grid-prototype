from .time_sim import TimeSimulator
from .houses_loads_sim import HousesLoadsSimulator
from .solar_system_sim import SolarSystemSimulator
from .power_mng import PowerManager


def main():
    """Main."""
    time_sim = TimeSimulator()
    time_sim.start()

    houses_loads_sim = HousesLoadsSimulator(time_sim)
    houses_loads_sim.start(dt=100)

    solar_system_sim = SolarSystemSimulator(time_sim)
    solar_system_sim.start(dt=100)

    power_mng = PowerManager(time_sim, houses_loads_sim, solar_system_sim)
    power_mng.start(dt=100)

    return (
        time_sim,
        houses_loads_sim,
        solar_system_sim,
        power_mng
    )


if __name__ == "__main__":
    main()
