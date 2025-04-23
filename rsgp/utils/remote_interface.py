from ..solar_system_sim import SolarSystemSimulator
from ..houses_loads_sim import HousesLoadsSimulator
from ..power_mng import PowerManager
from ..time_sim import TimeSimulator

import Pyro5.api


def start_pyro5_server(
    time_sim: TimeSimulator,
    houses_loads_sim: HousesLoadsSimulator,
    solar_system_sim: SolarSystemSimulator,
    power_manager: PowerManager,
):
    daemon = Pyro5.api.Daemon(host="localhost", port=41991)

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
