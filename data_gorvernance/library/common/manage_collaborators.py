
import os
from ..task_director import TaskDirector

# 本ファイルのファイル名
script_file_name = os.path.splitext(os.path.basename(__file__))[0]

class CollaboratorManager(TaskDirector):

    def __init__(self, working_path:str) -> None:
        super().__init__(working_path)

    @classmethod
    def generateFormScetion(cls, working_path:str):
        task_director = CollaboratorManager(working_path)
        # タスク開始によるサブフローステータス管理JSONの更新
        task_director.doing_task(script_file_name)

        # フォーム定義
        # フォーム表示


    @classmethod
    def completed_task(cls, working_path:str):
        # タスク実行の完了情報を該当サブフローステータス管理JSONに書き込む
        task_director = CollaboratorManager(working_path)
        task_director.done_task(script_file_name)
