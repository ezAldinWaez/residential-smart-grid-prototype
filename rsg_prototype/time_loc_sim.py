"""Time and location simulation."""

from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import time
import pytz


@dataclass
class LocationConf:
    """Location configuration."""

    lat: float  #: float: Location latitude. [°]
    lng: float  #: float: Location longitude. [°]
    alt: float  #: float: Location altitude. [m]
    tz_name: str  #: str: Location timezone name.

    @property
    def tz(self) -> pytz.BaseTzInfo:
        """pytz.BaseTzInfo: Location timezone."""
        return pytz.timezone(self.tz_name)

    def __post_init__(self):
        assert -90 <= self.lat <= 90
        assert -180 <= self.lng <= 180
        assert 0 <= self.alt <= 20000


class Location(Enum):
    """Some important places on Earth.

    Note:
        All members are from type :class:`LocationConf`.

    """

    ALEPPO = LocationConf(
        lat=36.2022,
        lng=37.1343,
        alt=380,
        tz_name='Asia/Damascus',
    )

    MEXICO = LocationConf(
        lat=19.4326,
        lng=-99.1332,
        alt=2250,
        tz_name='America/Mexico_City',
    )

    NEW_YORK = LocationConf(
        lat=40.7128,
        lng=-74.006,
        alt=10,
        tz_name='America/New_York',
    )

    ANTARCTICA = LocationConf(
        lat=-90,
        lng=0,
        alt=0,
        tz_name='Antarctica',
    )

    SAHARA_DESERT = LocationConf(
        lat=23.4162,
        lng=25.6628,
        alt=500,
        tz_name='Africa/Khartoum',
    )


class TimeLocSimulator:
    """Time and locaiton simulator.

    Args:
        time_factor (float): Time acceleration factor. [sec]
        location (Location): Location, including latitude, longitude, altitude, and timezone.

    """

    time_factor: float  #: float: Time acceleration factor. [sec]
    loc_name: str  #: str: Location name.
    loc_conf: LocationConf  #: LocationConf: The location configuration.
    #: bool: Whether the simulation is started or not.
    started: bool = False

    def __init__(self, time_factor: float, location: Location):
        self.time_factor = time_factor
        self.loc_name = location.name.replace('_', ' ').title()
        self.loc_conf = location.value

        self._paused_at: float = None
        self._pause_duration = .0
        self._start_time: datetime = None

    def get_elapsed(self) -> float:
        """Calculates the real elapsed time and multiplies it with the time factor.

        Returns:
            float: The elapsed simulation time (number of seconds). [sec]

        """
        assert self.started

        if self._paused_at:
            end_time = self._paused_at
        else:
            end_time = datetime.now(tz=self.loc_conf.tz).timestamp()

        elapsed_time = end_time - self._start_time - self._pause_duration
        elapsed_sim_time = elapsed_time * self.time_factor
        return elapsed_sim_time

    def get_time(self, elapsed: float = None) -> datetime:
        """Convert the elapsed time to datetime in current location timezone.

        Args:
            elapsed (float, optional): The elapsed simulation time, if it was not given, the
                current elapsed time will be used.

        Returns:
            datatiem: The current simulation datetime in current location timezone.

        """
        assert self.started

        if not elapsed:
            elapsed = self.get_elapsed()

        timestamp = self._start_time + elapsed
        return datetime.fromtimestamp(timestamp, tz=self.loc_conf.tz)

    def start(self):
        """Start the simulation."""
        self.started = True
        self._start_time = datetime.now(tz=self.loc_conf.tz).timestamp()

    def pause(self):
        """Pause the simulation."""
        if self._paused_at is None:
            self._paused_at = time.time()

    def resume(self):
        """Resume the simulation."""
        if self._paused_at is not None:
            last_pause_duration = time.time() - self._paused_at
            self._pause_duration += last_pause_duration
            self._paused_at = None
