"""Time simulator."""

from ..config.settings import settings

from datetime import datetime, timedelta

from Pyro5.api import expose as remote_interface_expose


@remote_interface_expose
class TimeSimulator:
    """Time simulator."""

    def __init__(self):
        self._started = False
        self._start_at: float = None
        self._paused_at: float = None
        self._pause_duration = .0

    def get_elapsed(self) -> float:
        """Get simulation elapsed time - simulation time that the time simulator still running.

        Returns:
            float: The simulation elapsed time. [sec]
        """
        assert self._started

        end_at = self._paused_at if self._paused_at else datetime.now().timestamp()
        elapsed_time = end_at - self._start_at - self._pause_duration
        elapsed_sim_time = elapsed_time * settings.TIME_FACTOR
        return elapsed_sim_time

    def get_timestamp(self, start_point: datetime | str, elapsed: float = None) -> datetime:
        """Get current simulation datetime, assuming we spent `elapsed` seconds in the simulation
        starting at `start_point` datetime.

        Args:
            start_point (datetime | str): The start point datetime.
            elapsed (float, optional): The elapsed simulation time, if it was not given, the
                current simulation elapsed time will be used.

        Returns:
            datetime: The current simulation datetime, in simulation timezone.
        """
        assert self._started

        if not elapsed:
            elapsed = self.get_elapsed()

        start_point_datetime = start_point if isinstance(
            start_point, datetime) else datetime.fromisoformat(start_point)

        return start_point_datetime + timedelta(seconds=elapsed)

    def start(self) -> None:
        """Start the simulation."""
        self._started = True
        self._start_at = datetime.now().timestamp()

    def pause(self) -> None:
        """Pause the simulation."""
        if self._paused_at is None:
            self._paused_at = datetime.now().timestamp()

    def resume(self) -> None:
        """Resume the simulation."""
        if self._paused_at is not None:
            last_pause_duration = datetime.now().timestamp() - self._paused_at
            self._pause_duration += last_pause_duration
            self._paused_at = None
