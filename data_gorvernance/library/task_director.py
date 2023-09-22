from .utils.config import path_config, message as msg_config
from .subflow.subflow import get_return_sub_flow_menu_relative_url_path, get_subflow_type_and_id
import os
from .subflow.status import StatusFile, SubflowStatus
import panel as pn
from panel.pane import HTML
from .utils.html.button import create_button
from IPython.display import display, Javascript

class TaskDirector():

    def __init__(self, nb_working_file_path:str) -> None:
        """TaskInterface コンストラクタ

        Notebookファイルのオペレーションするための共通クラス

        Args:
            nb_working_file_path (str): [実行Notebookのファイルパス]
        """
        # 実行Notebookのファイルパス
        self.nb_working_file_path = nb_working_file_path
        # 絶対rootディレクトリを取得・設定する
        self._abs_root_path = path_config.get_abs_root_form_working_dg_file_path(nb_working_file_path)

        # サブフローステータス管理JSONパス
        # 想定値：data_gorvernance\researchflow\plan\status.json
        # 想定値：data_gorvernance\researchflow\サブフロー種別\サブフローID\status.json
        subflow_type, subflow_id = get_subflow_type_and_id(nb_working_file_path)
        if subflow_id is None:
            # 研究準備の場合
            self._sub_flow_status_file_path = os.path.join(self._abs_root_path, path_config.get_sub_flow_status_file_path(subflow_type))
        else:
            # 研究準備以外の場合
            self._sub_flow_status_file_path = os.path.join(self._abs_root_path, path_config.get_sub_flow_status_file_path(subflow_type, subflow_id))

    def doing_task(self, task_name:str):
        """タスク開始によるサブフローステータス管理JSONの更新

        Args:
            task_name (str): [タスク名]
        """
        # タスク開始によるサブフローステータス管理JSONの更新
        sf = StatusFile(self._sub_flow_status_file_path)
        sf_status: SubflowStatus = sf.read()
        sf_status.doing_task_by_task_name(task_name, os.environ["JUPYTERHUB_SERVER_NAME"])
        # 更新内容を記録する。
        sf.write(sf_status)

    def done_task(self, task_name:str):
        """タスク完了によるサブフローステータス管理JSONの更新

        Args:
            script_file_name (str): [タスク名]
        """
        sf = StatusFile(self._sub_flow_status_file_path)
        sf_status: SubflowStatus = sf.read()
        sf_status.completed_task_by_task_name(task_name, os.environ["JUPYTERHUB_SERVER_NAME"])
        sf.write(sf_status)

    def get_subflow_menu_button_object(self)-> HTML:
        """サブフローメニューへのボタンpanel.HTMLオブジェクトの取得
        Returns:
            [panel.pane.HTML]: [HTMLオブジェクト]
        """
        button_width = 500
        sub_flow_menu_relative_url = get_return_sub_flow_menu_relative_url_path(self.nb_working_file_path)
        sub_flow_menu_link_button = pn.pane.HTML()
        sub_flow_menu_link_button.object = create_button(
            url=f'{sub_flow_menu_relative_url}?init_nb=true',
            msg=msg_config.get('task', 'retun_sub_flow_menu'),
            button_width=f'{button_width}px'
        )
        sub_flow_menu_link_button.width = button_width
        return sub_flow_menu_link_button


    @classmethod
    def return_subflow_menu(cls, working_path:str):
        pn.extension()
        task_director = TaskDirector(working_path)
        sub_flow_menu_link_button  = task_director.get_subflow_menu_button_object()
        display(sub_flow_menu_link_button)
        display(Javascript('IPython.notebook.save_checkpoint();'))
