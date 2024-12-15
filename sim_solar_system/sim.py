import threading
import time
import pvlib
from pvlib import irradiance

from sim_time_loc.sim_time_loc import SimulationTimeLocation


class SolarSystemSimulator:
    def __init__(self, sim_time_loc: SimulationTimeLocation, panels_count: int, panel_area: float, panel_efficiency: float, log=False):
        self.sim_time_loc = sim_time_loc
        self.panels_count = panels_count
        self.panel_area = panel_area
        self.panel_efficiency = panel_efficiency

        self.total_power = .0

        self.running = False
        self.log = log

    def start(self):
        """Start the Simulation"""
        self.running = True

        if (self.log):
            self.data_file = open(
                f"logs\\sss\\log_{self.sim_time_loc.get_time().strftime(f'%Y-%m-%d_%H-%M-%S')}.csv", "w")
            self.data_file.write("elapsed,total_power\n")

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
            curr_elapsed = self.sim_time_loc.get_elapsed()
            curr_utc_time = self.sim_time_loc.get_utc_time(curr_elapsed)

            # Create a location object
            pvloc = pvlib.location.Location(
                latitude=self.sim_time_loc.loc_lat,
                longitude=self.sim_time_loc.loc_lng,
                altitude=self.sim_time_loc.loc_alt
            )

            # Get solar position (elevation and azimuth)
            solar_pos = pvloc.get_solarposition(curr_utc_time)

            # Calculate the solar zenith angle
            self.zenith_angle = solar_pos['zenith'][0]

            if self.zenith_angle > 90:
                poa_irradiance = 0
            else:
                # Use a simplified clear-sky model for daytime irradiance
                poa_irradiance = irradiance.get_total_irradiance(
                    surface_tilt=30,  # Assumed fixed tilt for simplicity
                    surface_azimuth=180,  # Facing south
                    solar_zenith=self.zenith_angle,  # Zenith angle from solar position
                    dni=1000,  # Direct normal irradiance (clear sky)
                    ghi=1000,  # Global horizontal irradiance (clear sky)
                    dhi=100,  # Diffuse horizontal irradiance
                    # Azimuth angle from solar position
                    solar_azimuth=solar_pos['azimuth'],
                    dni_extra=1367  # Extra-terrestrial irradiance
                )['poa_global'].iloc[0]

            # Calculate the wattage output of each panel
            self.panel_power = poa_irradiance * self.panel_area * self.panel_efficiency
            self.total_power = self.panel_power * self.panels_count

            if (self.log):
                self.data_file.write(
                    f"{curr_elapsed:.2f},{self.total_power:.2f}\n")

            time.sleep(dt/1000)
