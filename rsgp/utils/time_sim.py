"""Time simulator."""

# TODO: Document this module.

from datetime import datetime, timedelta, timezone

from ..remote_object import expose
from ..config.settings import settings
from .nsrdb_data import nsrdb_location, nsrdb_start_point


@expose
class TimeSimulator:
    """Time simulator."""

    tz: timezone  #: timezone: ...
    start_point: datetime  #: datetime: ...

    def __init__(self):
        self._started = False
        self._start_at: float = None
        self._paused_at: float = None
        self._pause_duration = 0.0

        self.tz = nsrdb_location["timezone"]
        self.start_point = nsrdb_start_point

    def get_elapsed(self) -> float:
        assert self._started

        end_at = self._paused_at if self._paused_at else datetime.now().timestamp()
        elapsed_time = end_at - self._start_at - self._pause_duration
        elapsed_sim_time = elapsed_time * settings.TIME_FACTOR
        return elapsed_sim_time

    def get_timestamp(self, elapsed: float = None) -> datetime:
        assert self._started

        if not elapsed:
            elapsed = self.get_elapsed()

        return self.start_point + timedelta(seconds=elapsed)

    def start(self) -> None:
        self._started = True
        self._start_at = datetime.now().timestamp()

    def pause(self) -> None:
        if self._paused_at is None:
            self._paused_at = datetime.now().timestamp()

    def resume(self) -> None:
        if self._paused_at is not None:
            last_pause_duration = datetime.now().timestamp() - self._paused_at
            self._pause_duration += last_pause_duration
            self._paused_at = None

time_sim = TimeSimulator()
time_sim.start()
