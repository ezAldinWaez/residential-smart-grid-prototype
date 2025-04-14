"""Time simulation."""

from datetime import datetime
import pandas as pd


class TimeSimulator:
    """Time and locaiton simulator.

    Args:
        time_factor (float): Time acceleration factor. [sec]
        dataset_start (pd.Timestamp): ...
        location (dict): Location basic info: 'lat', 'lng', and 'tz'.

    """

    time_factor: float  #: float: Time acceleration factor. [sec]
    dataset_start: pd.Timestamp  #: Timestamp: ...
    started: bool = False  #: bool: Whether the simulation is started or not.

    def __init__(self, time_factor: float, dataset_start: pd.Timestamp, location: dict):
        self.time_factor = time_factor
        self.dataset_start = dataset_start
        self.location = location

        self._start_at: float = None
        self._paused_at: float = None
        self._pause_duration = .0

    def get_elapsed(self) -> float:
        """Calculates the real elapsed time and multiplies it with the time factor.

        Returns:
            float: The elapsed simulation time (number of seconds). [sec]

        """
        assert self.started

        if self._paused_at:
            end_time = self._paused_at
        else:
            end_time = datetime.now().timestamp()

        elapsed_time = end_time - self._start_at - self._pause_duration
        elapsed_sim_time = elapsed_time * self.time_factor
        return elapsed_sim_time

    def get_time(self, elapsed: float = None) -> pd.Timestamp:
        """Get current simulation timestamp, assuming that we spend `elapsed` seconds in the simulation.

        Args:
            elapsed (float, optional): The elapsed simulation time, if it was not given, the
                current elapsed time will be used.

        Returns:
            Timestamp: The current simulation timestamp in current location timezone.

        """
        assert self.started

        if not elapsed:
            elapsed = self.get_elapsed()

        return self.dataset_start + pd.Timedelta(seconds=elapsed)

    def start(self):
        """Start the simulation."""
        self.started = True
        self._start_at = datetime.now().timestamp()

    def pause(self):
        """Pause the simulation."""
        if self._paused_at is None:
            self._paused_at = datetime.now().timestamp()

    def resume(self):
        """Resume the simulation."""
        if self._paused_at is not None:
            last_pause_duration = datetime.now().timestamp() - self._paused_at
            self._pause_duration += last_pause_duration
            self._paused_at = None
