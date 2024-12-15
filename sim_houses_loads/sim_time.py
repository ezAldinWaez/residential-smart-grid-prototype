from datetime import datetime
import time


class SimulationTime:
    def __init__(self, time_factor: float):
        """
        Parameters
        ----------
        - timeFactor : Time acceleration factor (in sec).
        """
        self.time_factor = time_factor
        self.start_real_time: float = time.time()
        self.paused_at: float | None = None
        self.pause_duration: float = 0

    def get_elapsed(self) -> float:
        """
        Return the elapsed simulation time (number of seconds).
        """
        return ((self.paused_at if self.paused_at else time.time()) - self.start_real_time - self.pause_duration) * self.time_factor

    def get_time(self, elapsed=None) -> datetime:
        """
        Return the current simulation datetime.
        """
        if not elapsed:
            elapsed = self.get_elapsed()
        return datetime.fromtimestamp(self.start_real_time + elapsed)

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
