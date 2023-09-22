from ..utils.config import path_config, message as msg_config
import panel as pn
import os
import traceback
from IPython.display import display, Javascript
from ..subflow.status import StatusFile, SubflowStatus, TaskStatus
from ..subflow.subflow import get_return_sub_flow_menu_relative_url_path, get_subflow_type_and_id
from ..utils.html.button import create_button

# 本ファイルのファイル名
script_file_name = os.path.splitext(os.path.basename(__file__))[0]

class CollaboratorManager():

    def __init__(self, working_path:str) -> None:
        # 絶対rootディレクトリを取得する
        self._abs_root_path = path_config.get_abs_root_form_working_dg_file_path(working_path)

        # 研究準備のサブフローステータス管理JSONパス
        # 想定値：data_gorvernance\researchflow\plan\status.json
        # 想定値：data_gorvernance\researchflow\サブフロー種別\サブフローID\status.json
        subflow_type, subflow_id = get_subflow_type_and_id(working_path)
        if subflow_id is None:
            # 研究準備の場合
            self._sub_flow_status_file_path = os.path.join(self._abs_root_path, path_config.get_sub_flow_status_file_path(subflow_type))
        else:
            # 研究準備以外の場合
            self._sub_flow_status_file_path = os.path.join(self._abs_root_path, path_config.get_sub_flow_status_file_path(subflow_type, subflow_id))

    @classmethod
    def generateFormScetion(cls, working_path:str):
        col_mng = CollaboratorManager(working_path)
        # サブフローステータス管理JSONの更新
        sf = StatusFile(col_mng._sub_flow_status_file_path)
        sf_status: SubflowStatus = sf.read()
        sf_status.doing_task_by_task_name(script_file_name, os.environ["JUPYTERHUB_SERVER_NAME"])
        # 更新内容を記録する。
        sf.write(sf_status)

        # フォーム定義
        # フォーム表示


    @classmethod
    def completed_task(cls, working_path:str):
        # タスク実行の完了情報を該当サブフローステータス管理JSONに書き込む
        col_mng = CollaboratorManager(working_path)
        sf = StatusFile(col_mng._sub_flow_status_file_path)
        sf_status: SubflowStatus = sf.read()
        sf_status.completed_task_by_task_name(script_file_name, os.environ["JUPYTERHUB_SERVER_NAME"])
        sf.write(sf_status)


    @classmethod
    def return_subflow_menu(cls, working_path:str):
        pn.extension()
        sub_flow_menu_relative_url = get_return_sub_flow_menu_relative_url_path(working_path)
        sub_flow_menu_link_button = pn.pane.HTML()
        sub_flow_menu_link_button.object = create_button(
            url=sub_flow_menu_relative_url,
            msg=msg_config.get('task', 'retun_sub_flow_menu'),
            button_width='500px'
        )
        sub_flow_menu_link_button.width = 500
        display(sub_flow_menu_link_button)
        display(Javascript('IPython.notebook.save_checkpoint();'))
