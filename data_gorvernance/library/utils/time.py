""" 処理時間を計測するためのモジュールです。
"""
import time


class TimeDiff:
    """ 処理時間を計測するためのクラスです。

    Attributes:
        instance:
            time_diff(float):
            start_time(float):
            end_time(float):
    """
    def __init__(self) -> None:
        """ クラスのインスタンスの初期化処理を実行するメソッドです。"""
        self.time_diff = None

    def start(self):
        """ パフォーマンスカウンタの開始時間を記録するメソッドです。"""
        self.start_time = time.perf_counter()

    def end(self):
        """ パフォーマンスカウンタを終了時間を記録するメソッドです。

        startメソッドとendメソッドの呼び出し間の経過時間をtime_diffに保存します。
        """
        self.end_time = time.perf_counter()
        self.time_diff = self.end_time - self.start_time

    def get_diff_minute(self):
        """ 処理時間を分と秒に変換して返すメソッドです。

        Returns:
            int: 処理時間の秒を返す。
            float: 処理時間の分を返す。
        """
        if self.time_diff is None:
            return None, None
        return self._format_time(self.time_diff)

    def _format_time(self, seconds):
        """ 与えられた秒数を分と秒に変換するメソッドです。

        Args:
            seconds (float): 変換したい秒数を設定します。

        Returns:
            int: 処理時間の秒を返す。
            float: 処理時間の分を返す。
        """
        minutes, seconds = divmod(seconds, 60)
        return int(minutes), round(seconds, 2)
