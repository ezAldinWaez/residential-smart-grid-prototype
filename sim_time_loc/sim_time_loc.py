from datetime import datetime
import time
import pytz

from .data import Location

class SimulationTimeLocation:
    def __init__(self, time_factor: float, location = Location.ALEPPO):
        """
        Parameters
        ----------
        - time_factor : Time acceleration factor (in sec).
        - location_info : LocationInfo object, incluting location latitude, longitude, altitude, and timezone.
        """
        self.time_factor = time_factor
        self.loc_name = location.name 
        self.loc_lat = location.value.lat
        self.loc_lng = location.value.lng
        self.loc_alt = location.value.alt
        self.loc_tz = pytz.timezone(location.value.tz_name)

        self.paused_at: float | None = None
        self.pause_duration: float = 0

        self.start_real_time = datetime.now(tz=self.loc_tz).timestamp()

    def get_elapsed(self) -> float:
        """
        Return the elapsed simulation time (number of seconds).
        """
        return ((self.paused_at if self.paused_at else datetime.now(tz=self.loc_tz).timestamp()) - self.start_real_time - self.pause_duration) * self.time_factor

    def get_time(self, elapsed=None) -> datetime:
        """
        Return the current simulation datetime.
        """
        if not elapsed:
            elapsed = self.get_elapsed()
        return datetime.fromtimestamp(self.start_real_time + elapsed, tz=self.loc_tz)


    def get_utc_time(self, elapsed=None) -> datetime:
        """
        Return the current simulation datetime in utc timezone.
        """
        return self.get_time(elapsed).astimezone(pytz.utc)


    def pause(self):
        """
        Pause the simulation time.
        """
        if self.paused_at is None:
            self.paused_at = time.time()

    def resume(self):
        """
        Resume the simulation time.
        """
        if self.paused_at is not None:
            self.pause_duration += time.time() - self.paused_at
            self.paused_at = None
