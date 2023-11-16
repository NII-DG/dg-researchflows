import time


class TimeDiff:

    def __init__(self) -> None:
        self.time_diff = None

    def start(self):
        self.start_time = time.perf_counter()

    def end(self):
        self.end_time = time.perf_counter()
        self.time_diff = self.end_time - self.start_time

    def get_diff_minute(self):
        if self.time_diff is None:
            return None, None
        return self._format_time(self.time_diff)

    def _format_time(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        return int(minutes), round(seconds, 2)
