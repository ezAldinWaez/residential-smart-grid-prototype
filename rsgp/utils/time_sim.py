"""RSGP Time simulator."""

from datetime import datetime, timedelta

from .nsrdb_data import nsrdb_start_point
from ..config.settings import settings

from Pyro5.api import expose


@expose
class TimeSimulator:
    """Time simulator for RSGP."""

    def __init__(self) -> None:
        self._started = False
        self._start_at: float = None
        self._paused_at: float = None
        self._pause_duration = 0.0
        self._start_point = nsrdb_start_point

    def get_elapsed(self) -> float:
        """Get the elapsed time in seconds.

        Returns:
            float: The elapsed time in seconds.

        """
        assert self._started

        end_at = self._paused_at if self._paused_at else datetime.now().timestamp()
        elapsed_time = end_at - self._start_at - self._pause_duration
        elapsed_sim_time = elapsed_time * settings.TIME_FACTOR
        return elapsed_sim_time

    def get_timestamp(self, elapsed: float = None) -> datetime:
        """Get the current timestamp.

        Args:
            elapsed (float, optional): The elapsed time in seconds. Defaults to None, if so, it
                will be calculated automatically.

        Returns:
            datetime: The current timestamp.

        """
        assert self._started

        if not elapsed:
            elapsed = self.get_elapsed()

        return self._start_point + timedelta(seconds=elapsed)

    def start(self) -> None:
        """Start the time simulation."""
        if not self._started:
            self._started = True
            self._start_at = datetime.now().timestamp()

    def pause(self) -> None:
        """Pause the time simulation."""
        if self._paused_at is None:
            self._paused_at = datetime.now().timestamp()

    def resume(self) -> None:
        """Resume the time simulation."""
        if self._paused_at is not None:
            last_pause_duration = datetime.now().timestamp() - self._paused_at
            self._pause_duration += last_pause_duration
            self._paused_at = None


time_sim = TimeSimulator()  #: TimeSimulator: Global time simulator instance.
time_sim.start()
