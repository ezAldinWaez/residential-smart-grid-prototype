"""Time simulator."""

from ..config import settings

from datetime import datetime, timedelta


class TimeSimulator:
    """Time simulator."""
    started: bool  #: bool: Whether the simulation is started or not.

    def __init__(self):
        self.started = False

        self._start_at: float = None
        self._paused_at: float = None
        self._pause_duration = .0

    def get_elapsed(self) -> float:
        """Get simulation elapsed time - simulation time that the time simulator still running.

        Returns:
            float: The simulation elapsed time. [sec]
        """
        assert self.started

        end_at = self._paused_at if self._paused_at else datetime.now().timestamp()
        elapsed_time = end_at - self._start_at - self._pause_duration
        elapsed_sim_time = elapsed_time * settings.TIME_FACTOR
        return elapsed_sim_time

    def get_timestamp(self, start_point: datetime, elapsed: float = None) -> datetime:
        """Get current simulation datetime, assuming we spent `elapsed` seconds in the simulation
        starting at `start_point` datetime.

        Args:
            start_point (datetime): <...>
            elapsed (float, optional): The elapsed simulation time, if it was not given, the
                current simulation elapsed time will be used.

        Returns:
            datetime: The current simulation datetime, in simulation timezone.
        """
        assert self.started

        if not elapsed:
            elapsed = self.get_elapsed()

        return start_point + timedelta(seconds=elapsed)

    def start(self) -> None:
        """Start the simulation."""
        self.started = True
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
