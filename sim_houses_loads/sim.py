import threading
import time

from sim_time_loc.sim_time_loc import SimulationTimeLocation

from .device_state import DeviceState
from .data import DEVICES_CONFIG


class HousesLoadsSimulator:
    def __init__(self, num_houses: int, sim_time_loc: SimulationTimeLocation, log=False):
        self.num_houses: int = num_houses
        self.sim_time_loc = sim_time_loc

        self.houses_device_states = [
            {
                device_name: DeviceState(device_config)
                for device_name, device_config in DEVICES_CONFIG.items()
            }
            for _ in range(self.num_houses)
        ]

        self.system_load = .0
        self.houses_loads = [.0 for _ in range(self.num_houses)]

        self.running = False
        self.log = log

    def start(self):
        """Start the Simulation"""
        self.running = True

        if (self.log):
            self.data_file = open(
                f"logs\\shl\\log_{self.sim_time_loc.get_time().strftime(f'%Y-%m-%d_%H-%M-%S')}.csv", "w")
            self.data_file.write("elapsed,system_load\n")

        threading.Thread(
            target=self.update_sim,
            args=[100],  # Update the simulation every 100 ms
            daemon=True
        ).start()

    def pause(self):
        if self.running:
            self.running = False

            if (self.log):
                self.data_file.close()

    def resume(self):
        if not self.running:
            self.start()

    def update_sim(self, dt: int):
        while self.running:
            elapsed = self.sim_time_loc.get_elapsed()

            for idx in range(self.num_houses):
                house_load = 0.0
                for device_name in self.houses_device_states[idx].keys():
                    self.houses_device_states[idx][device_name].filter_active_envelopes(
                        elapsed)
                    device_load = self.houses_device_states[idx][device_name].calc_device_load(
                        elapsed)
                    house_load += device_load

                self.houses_loads[idx] = house_load

            self.system_load = sum(self.houses_loads)

            if (self.log):
                self.data_file.write(f"{elapsed:.2f},{self.system_load:.2f}\n")

            time.sleep(dt/1000)
