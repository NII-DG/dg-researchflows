import panel as pn
import os
from IPython.display import display, Javascript
from ..task_director import TaskDirector


# 本ファイルのファイル名
script_file_name = os.path.splitext(os.path.basename(__file__))[0]

class DataSaver(TaskDirector):

    def __init__(self, nb_working_file_path:str) -> None:
        """DataSaver コンストラクタ

        Args:
            nb_working_file_path (str): [実行Notebookファイルパス]
        """
        super().__init__(nb_working_file_path)

    @classmethod
    def generateFormScetion(cls, working_path:str):
        task_director = DataSaver(working_path)
        # タスク開始によるサブフローステータス管理JSONの更新
        task_director.doing_task(script_file_name)

        # フォーム定義
        # フォーム表示


    @classmethod
    def completed_task(cls, working_path:str):
        # タスク実行の完了情報を該当サブフローステータス管理JSONに書き込む
        task_director = DataSaver(working_path)
        task_director.done_task(script_file_name)
