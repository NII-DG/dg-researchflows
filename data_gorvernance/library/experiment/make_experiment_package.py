import panel as pn
import os
from IPython.display import display, Javascript
from ..task_director import TaskDirector


# 本ファイルのファイル名
script_file_name = os.path.splitext(os.path.basename(__file__))[0]

class ExperimentPackageMaker(TaskDirector):

    def __init__(self, nb_working_file_path:str) -> None:
        """ExperimentPackageMaker コンストラクタ

        Args:
            nb_working_file_path (str): [実行Notebookファイルパス]
        """
        super().__init__(nb_working_file_path)

    @classmethod
    def generateFormScetion(cls, working_path:str):
        task_director = ExperimentPackageMaker(working_path)
        # タスク開始によるサブフローステータス管理JSONの更新
        task_director.doing_task(script_file_name)

        # フォーム定義
        # フォーム表示


    @classmethod
    def completed_task(cls, working_path:str):
        # タスク実行の完了情報を該当サブフローステータス管理JSONに書き込む
        task_director = ExperimentPackageMaker(working_path)
        task_director.done_task(script_file_name)


    @classmethod
    def return_subflow_menu(cls, working_path:str):
        pn.extension()
        task_director = ExperimentPackageMaker(working_path)
        sub_flow_menu_link_button  = task_director.get_subflow_menu_button_object()
        display(sub_flow_menu_link_button)
        display(Javascript('IPython.notebook.save_checkpoint();'))