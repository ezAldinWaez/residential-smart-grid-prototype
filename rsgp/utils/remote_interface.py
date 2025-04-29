from ..config.settings import settings
from ..solar_system_sim.simulator import SolarSystemSimulator
from ..houses_loads_sim.simulator import HousesLoadsSimulator
from ..power_mng.manager import PowerManager
from ..time_sim.simulator import TimeSimulator

import Pyro5.api


def start_remote_interface(
    time_sim: TimeSimulator,
    houses_loads_sim: HousesLoadsSimulator,
    solar_system_sim: SolarSystemSimulator,
    power_manager: PowerManager,
) -> None:
    """Start the remote object interface using `Pyro5`.

    Args:
        time_sim (TimeSimulator): Time simulator.
        houses_loads_sim (HousesLoadsSimulator): Houses loads simulator.
        solar_system_sim (SolarSystemSimulator): Solar system simulator.
        power_manager (PowerManager): Power manager.
    """
    daemon = Pyro5.api.Daemon(
        host=settings.REMOTE_INTERFACE_HOST,
        port=settings.REMOTE_INTERFACE_PORT,
    )
    daemon.register(time_sim, "time_sim")
    daemon.register(houses_loads_sim, "houses_loads_sim")
    for house in houses_loads_sim.houses:
        daemon.register(house, f"houses_loads_sim.house_{house.idx}")
        for device in house.devices.values():
            daemon.register(
                device, f"houses_loads_sim.house_{house.idx}.device_{device.name}")
    daemon.register(solar_system_sim, "solar_system_sim")
    daemon.register(power_manager, "power_manager")
    daemon.requestLoop()
