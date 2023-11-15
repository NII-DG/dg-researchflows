import os
import functools

from .models import UserActivityLog

class TaskLog:

    def __init__(self, nb_working_file_path, notebook_name) -> None:
        self.log = UserActivityLog(nb_working_file_path, notebook_name)

    ###################################
    # 継承したクラスで呼ぶ為のデコレータ #
    ###################################
    @staticmethod
    def task_cell(cell_id: str, start_message="", finish_message=""):
        """タスクセルに必須の処理"""
        def wrapper(func):
            @functools.wraps(func)
            def decorate(self, *args, **kwargs):
                self.log.cell_id = cell_id
                self.log.start_cell(start_message)
                result = func(self, *args, **kwargs)
                self.log.finish_cell(finish_message)
                return result
            return decorate
        return wrapper

    @staticmethod
    def callback_form(event_name):
        """フォームの処理に必須の処理"""
        def wrapper(func):
            @functools.wraps(func)
            def decorate(self, *args, **kwargs):
                self.log.info("-- " + event_name + "開始 --")
                result = func(self, *args, **kwargs)
                self.log.info("-- " + event_name + "終了 --")
                return result
            return decorate
        return wrapper