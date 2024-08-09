"""タスク処理の前後でログを出力する機能に関するクラスが記載されたモジュールです。"""
import functools
from typing import Callable

from .models import UserActivityLog


class TaskLog:
    """タスクの実行時にログを出力する機能を記載したクラスです。

    Attributes:
        instance:
            log(UserActivityLog):UserActivityLogクラスのインスタンス

    """

    def __init__(self, nb_working_file_path: str, notebook_name: str) -> None:
        """クラスのインスタンスの初期化を行うメソッドです。コンストラクタ

        Args:
            nb_working_file (str): ノートブック名を含む絶対パス
            notebook_name(str):ノートブック名

        """
        self.log = UserActivityLog(nb_working_file_path, notebook_name)

    ###################################
    # 継承したクラスで呼ぶ為のデコレータ #
    ###################################
    @staticmethod
    def task_cell(cell_id: str, start_message:str="", finish_message:str="") -> Callable:
        """タスクセルに必須の処理を行うメソッドです。

        タスクセルの実行状況をトレースするため、実行の前後でログの出力を行います。

        Args:
            cell_id(str):ノートブックのセル番号
            start_message(str):タスクの開始時に出力するメッセージ。デフォルトは空文字。
            finish_message(str):タスクの終了時に出力するメッセージ。デフォルトは空文字。

        Return:
            callable:wrapper関数

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
    def callback_form(event_name:str) -> Callable:
        """フォームの処理に必須の処理を行うメソッドです。

        フォームの処理の実行状況をトレースするため、実行の前後でログの出力を行います。

        Args:
            event_name (str): 処理が行われるイベントの名前

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
