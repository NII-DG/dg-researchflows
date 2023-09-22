from ..utils.config import path_config, message as msg_config
import panel as pn
import os
import traceback
from IPython.display import display, Javascript
from ..subflow.status import StatusFile, SubflowStatus, TaskStatus
from ..task_interface import TaskInterface

# 本ファイルのファイル名
script_file_name = os.path.splitext(os.path.basename(__file__))[0]

class CollaboratorManager(TaskInterface):

    def __init__(self, working_path:str) -> None:
        super().__init__(working_path)
        # 絶対rootディレクトリを取得する

    @classmethod
    def generateFormScetion(cls, working_path:str):
        col_mng = CollaboratorManager(working_path)
        # タスク開始によるサブフローステータス管理JSONの更新
        col_mng.doing_task(script_file_name)

        # フォーム定義
        # フォーム表示


    @classmethod
    def completed_task(cls, working_path:str):
        # タスク実行の完了情報を該当サブフローステータス管理JSONに書き込む
        col_mng = CollaboratorManager(working_path)
        col_mng.done_task(script_file_name)
        # sf = StatusFile(col_mng._sub_flow_status_file_path)
        # sf_status: SubflowStatus = sf.read()
        # sf_status.completed_task_by_task_name(script_file_name, os.environ["JUPYTERHUB_SERVER_NAME"])
        # sf.write(sf_status)


    @classmethod
    def return_subflow_menu(cls, working_path:str):
        pn.extension()
        col_mng = CollaboratorManager(working_path)
        sub_flow_menu_link_button  = col_mng.return_subflow_menu_button_object()
        display(sub_flow_menu_link_button)
        display(Javascript('IPython.notebook.save_checkpoint();'))
