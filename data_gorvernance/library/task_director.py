"""サブフローステータス更新を行うモジュールです。

ここは全てのタスクに共通の処理をまとめます。
"""
import os

from IPython.display import display
from IPython.core.display import Javascript
import panel as pn
from panel.pane import HTML

from library.utils.config import path_config, message as msg_config
from library.utils.html import create_button
from library.utils.save import TaskSave
from library.utils.setting import get_subflow_type_and_id, SubflowStatusFile, SubflowStatus


def get_return_sub_flow_menu_relative_url_path(working_file_path: str) -> str:
    """サブフローメニューNotebookへのパス、ファイルパスを取得するメソッドです。

    Args:
        working_file_path(str):作業ファイルのパス

    Returns:
        str:サブフローメニューのパスを返す。

    """

    subflow_type, subflow_id = get_subflow_type_and_id(working_file_path)
    if not subflow_type:
            raise ValueError('don\'t get subflow type.')
    if not subflow_id:
        menu_path = path_config.get_sub_flow_menu_path(subflow_type)
        return os.path.join('../../../../..', menu_path)
    else:
        menu_path = path_config.get_sub_flow_menu_path(subflow_type, subflow_id)
        return os.path.join('../../../../../..', menu_path)


class TaskDirector(TaskSave):
    """タスクの基底クラスです。

    Attributes:
        instance:
            nb_working_file_path (str): 実行Notebookのファイルパス
            _abs_root_path(str):リサーチフローのルートディレクトリ
            _script_file_name(str):実行Notebookのファイル名
            _sub_flow_status_file_path(str):サブフローステータスファイルのパス
    """

    def __init__(self, nb_working_file_path:str, notebook_name:str) -> None:
        """TaskDirector コンストラクタのメソッドです。

        Notebookファイルのオペレーションするための共通クラス

        Args:
            nb_working_file_path (str): 実行Notebookのファイルパス

        Raise:
            ValueError:値が不適切の時のエラー
        """
        super().__init__(nb_working_file_path, notebook_name)
        # 実行Notebookのファイルパス
        self.nb_working_file_path = nb_working_file_path
        # 絶対rootディレクトリを取得・設定する
        self._abs_root_path = path_config.get_abs_root_form_working_dg_file_path(nb_working_file_path)
        self._script_file_name = os.path.splitext(notebook_name)[0]

        # サブフローステータス管理JSONパス
        # 想定値：data_gorvernance\researchflow\plan\status.json
        # 想定値：data_gorvernance\researchflow\サブフロー種別\サブフローID\status.json
        subflow_type, subflow_id = get_subflow_type_and_id(nb_working_file_path)
        if not subflow_type:
            raise ValueError('don\'t get subflow type.')
        if not subflow_id:
            # 研究準備の場合
            self._sub_flow_status_file_path = os.path.join(self._abs_root_path, path_config.get_sub_flow_status_file_path(subflow_type))
        else:
            # 研究準備以外の場合
            self._sub_flow_status_file_path = os.path.join(self._abs_root_path, path_config.get_sub_flow_status_file_path(subflow_type, subflow_id))

    ########################
    #  update task status  #
    ########################
    def doing_task(self):
        """タスク開始によるサブフローステータス管理JSONの更新をするメソッドです。"""
        # タスク開始によるサブフローステータス管理JSONの更新
        sf = SubflowStatusFile(self._sub_flow_status_file_path)
        sf_status: SubflowStatus = sf.read()
        sf_status.doing_task_by_task_name(self._script_file_name, os.environ["JUPYTERHUB_SERVER_NAME"])
        # 更新内容を記録する。
        sf.write(sf_status)

    def done_task(self):
        """タスク完了によるサブフローステータス管理JSONの更新をするメソッドです。"""
        sf = SubflowStatusFile(self._sub_flow_status_file_path)
        sf_status: SubflowStatus = sf.read()
        sf_status.completed_task_by_task_name(self._script_file_name, os.environ["JUPYTERHUB_SERVER_NAME"])
        sf.write(sf_status)

    #########################
    #  return subflow menu  #
    #########################
    def get_subflow_menu_button_object(self)-> pn.pane.HTML:
        """サブフローメニューへのボタンpanel.HTMLオブジェクトの取得するメソッドです。

        Returns:
            panel.pane.HTML: HTMLオブジェクト
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

    # ここではログを吐かない
    def return_subflow_menu(self):
        """サブフローメニューへのボタン表示を行うメソッドです。"""
        pn.extension()
        sub_flow_menu_link_button  = self.get_subflow_menu_button_object()
        display(sub_flow_menu_link_button)
        display(Javascript('IPython.notebook.save_checkpoint();'))

    ##########
    #  save  #
    ##########

    # override
    def _save(self):
        """ファイルをストレージへ保存するメソッドです。"""
        # uploadしたときにタスク完了とするため
        super()._save()
        self.done_task()
