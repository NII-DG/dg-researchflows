import os
from ..task_director import TaskDirector


# 本ファイルのファイル名
script_file_name = os.path.splitext(os.path.basename(__file__))[0]
notebook_name = script_file_name+'.ipynb'

class Validator(TaskDirector):

    def __init__(self, working_path:str) -> None:
        """ExperimentEnvBuilder コンストラクタ

        Args:
            working_path (str): [実行Notebookファイルパス]
        """
        super().__init__(working_path, notebook_name)

    @TaskDirector.task_cell("1")
    def generateFormScetion(self):
        # タスク開始によるサブフローステータス管理JSONの更新
        self.doing_task(script_file_name)

        # フォーム定義
        # フォーム表示


    TaskDirector.task_cell("2")
    def completed_task(self):
        # タスク実行の完了情報を該当サブフローステータス管理JSONに書き込む
        self.done_task(script_file_name)