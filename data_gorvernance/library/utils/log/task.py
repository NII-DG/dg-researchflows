"""タスク処理の前後でログを出力する機能に関するクラスが記載されています。"""
import functools

from .models import UserActivityLog


class TaskLog:
    """タスクログのクラスです。

    タスク処理の前後でログを出力する機能に関するメソッドを記載しています。

     Attributes:
            instance:
                log(UserActivityLog):UserActivityLogクラスのインスタンス

    """
    def __init__(self, nb_working_file_path, notebook_name) -> None:
        """クラスのインスタンスの初期化を行うメソッドです。コンストラクタ

        引数として受け取ったパスとノートブックからUserActivityLogクラスのインスタンスを生成し、保存します。

        Args:
            nb_working_file (Any): ノートブック名を含む絶対パス
            notebook_name(Any):ノートブック名

        """
        self.log = UserActivityLog(nb_working_file_path, notebook_name)

    ###################################
    # 継承したクラスで呼ぶ為のデコレータ #
    ###################################
    @staticmethod
    def task_cell(cell_id: str, start_message="", finish_message=""):
        """タスクセルに必須の処理を行うメソッドです。

        静的なメソッドとして機能し、funcメソッドをデコレートすることで実行されれる前後にログを出力する。

        Args:
            cell_id(str):ノートブックのセル番号
            start_message(str, optional):タスクの開始時に出力するメッセージ。デフォルトは空文字。
            finish_message(str, optional):タスクの終了時に出力するメッセージ。デフォルトは空文字。

        Return:
           Callable:wrapper関数

        """
        def wrapper(func):
            @functools.wraps(func)
            def decorate(self, *args, **kwargs):
                self.log.cell_id = cell_id
                self.log.start(note=start_message)
                result = func(self, *args, **kwargs)
                self.log.finish(note=finish_message)
                return result
            return decorate
        return wrapper

    @staticmethod
    def callback_form(event_name):
        """フォームの処理に必須の処理を行うメソッドです。

         静的なメソッドとして機能し、funcメソッドをデコレートすることで実行されれる前後にログを出力する。

        Args:
            event_name (Any): 処理が行われるイベントの名前

        Return:
            Callable:wrapper関数

        """
        def wrapper(func):
            @functools.wraps(func)
            def decorate(self, *args, **kwargs):
                self.log.start(detail=event_name)
                result = func(self, *args, **kwargs)
                self.log.finish(detail=event_name)
                return result
            return decorate
        return wrapper