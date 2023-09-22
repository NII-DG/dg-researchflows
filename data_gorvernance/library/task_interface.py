from .utils.config import path_config, message as msg_config
from .subflow.subflow import get_return_sub_flow_menu_relative_url_path, get_subflow_type_and_id
import os
from .subflow.status import StatusFile, SubflowStatus, TaskStatus
import panel as pn
from .utils.html.button import create_button

class TaskInterface():

    def __init__(self, working_path:str) -> None:
        # 実行Notebookのファイルパス
        self.working_path = working_path
        # 絶対rootディレクトリを取得・設定する
        self._abs_root_path = path_config.get_abs_root_form_working_dg_file_path(working_path)

        # サブフローステータス管理JSONパス
        # 想定値：data_gorvernance\researchflow\plan\status.json
        # 想定値：data_gorvernance\researchflow\サブフロー種別\サブフローID\status.json
        subflow_type, subflow_id = get_subflow_type_and_id(working_path)
        if subflow_id is None:
            # 研究準備の場合
            self._sub_flow_status_file_path = os.path.join(self._abs_root_path, path_config.get_sub_flow_status_file_path(subflow_type))
        else:
            # 研究準備以外の場合
            self._sub_flow_status_file_path = os.path.join(self._abs_root_path, path_config.get_sub_flow_status_file_path(subflow_type, subflow_id))

    def completed_task(self, script_file_name):
        sf = StatusFile(self._sub_flow_status_file_path)
        sf_status: SubflowStatus = sf.read()
        sf_status.completed_task_by_task_name(script_file_name, os.environ["JUPYTERHUB_SERVER_NAME"])
        sf.write(sf_status)

    def return_subflow_menu_button_object(self):
        button_width = 500
        sub_flow_menu_relative_url = get_return_sub_flow_menu_relative_url_path(self.working_path)
        sub_flow_menu_link_button = pn.pane.HTML()
        sub_flow_menu_link_button.object = create_button(
            url=sub_flow_menu_relative_url,
            msg=msg_config.get('task', 'retun_sub_flow_menu'),
            button_width=f'{button_width}px'
        )
        sub_flow_menu_link_button.width = button_width
        return sub_flow_menu_link_button
