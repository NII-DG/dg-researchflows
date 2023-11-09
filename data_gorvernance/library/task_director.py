import os
import functools
from requests.exceptions import RequestException

import panel as pn
from panel.pane import HTML
from IPython.display import display
from IPython.core.display import Javascript

from .utils.html.button import create_button
from .subflow.status import StatusFile, SubflowStatus
from .utils.config import path_config, message as msg_config
from .subflow.subflow import get_return_sub_flow_menu_relative_url_path, get_subflow_type_and_id
from .utils.log import UserActivityLog
from .utils.widgets import Alert, Button
from .utils.storage_provider import grdm
from .utils.error import UnauthorizedError


class TaskDirector():

    def __init__(self, nb_working_file_path:str, notebook_name:str) -> None:
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
        # ログ
        self.log = UserActivityLog(nb_working_file_path, notebook_name)
        # メッセージ用ボックス
        self._msg_output = pn.WidgetBox()
        self._msg_output.width = 900

    # 継承したクラスで呼ぶ為のデコレータ
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

    ########################
    #  update task status  #
    ########################
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

    #########################
    #  return subflow menu  #
    #########################
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

    # ここではログを吐かない
    def return_subflow_menu(self):
        pn.extension()
        sub_flow_menu_link_button  = self.get_subflow_menu_button_object()
        display(sub_flow_menu_link_button)
        display(Javascript('IPython.notebook.save_checkpoint();'))

    ####################
    #  change message  #
    ####################
    def update_msg_info(self, msg):
        self._msg_output.clear()
        alert = Alert.info(msg)
        self._msg_output.append(alert)

    def update_msg_success(self, msg):
        self._msg_output.clear()
        alert = Alert.success(msg)
        self._msg_output.append(alert)

    def update_msg_warning(self, msg):
        self._msg_output.clear()
        alert = Alert.warning(msg)
        self._msg_output.append(alert)

    def update_msg_error(self, msg):
        self._msg_output.clear()
        alert = Alert.error(msg)
        self._msg_output.append(alert)

    def update_msg_exception(self):
        self._msg_output.clear()
        alert = Alert.exception()
        self._msg_output.append(alert)

    ##################
    #  save to GRDM  #
    ##################
    def save_define_form(self, source, script_file_name):
        """source is str or list."""

        # validate source path
        if isinstance(source, str):
            source = [source]
        if not isinstance(source, list):
            raise TypeError
        self._source = source

        # config
        self._script_file_name = script_file_name

        # フォーム用ボックス
        self._save_form_box = pn.WidgetBox()
        self._save_form_box.width = 900
        # 入力フォーム
        self._save_form = pn.widgets.TextInput(name="GRDM Token", width=600)
        self._save_form_box.append(self._save_form)
        # 確定ボタン
        self._save_submit_button = Button(width=600)
        self._save_submit_button.set_looks_init()
        self._save_submit_button.on_click(self._save_token_callback)
        self._save_form_box.append(self._save_submit_button)

    def _save_token_callback(self, event):
        self._msg_output.clear()
        self._save_submit_button.set_looks_processing()

        token = self._save_form.value_input
        if not self._validate_token(token):
            return

        self.grdm_token = token
        project_id = grdm.get_project_id()
        if project_id:
            self.project_id = project_id
            self._save()
        else:
            # grdmから起動しない場合（開発用？）
            self._save_input_project_id()

    def _validate_token(self, token):
        if len(token) <= 0:
            message = "入力されていません。入力してから再度クリックしてください。"
            self.log.warning(message)
            self._save_submit_button.set_looks_warning(message)
            return False

        try:
            grdm.get_projects(
                grdm.SCHEME, grdm.DOMAIN, token
            )
        except UnauthorizedError:
            message = "正しいトークンを入力してください。"
            self.log.warning(message)
            self._save_submit_button.set_looks_warning(message)
            return False
        except RequestException:
            message = "通信不良"
            self.log.error(message)
            self._save_submit_button.set_looks_error(message)
            return False
        except Exception:
            message = "想定外のエラー"
            self.log.error(message)
            self._save_submit_button.set_looks_error(message)
            return False

        return True

    def _save_input_project_id(self):
        self._msg_output.clear()
        projects = grdm.get_projects(
            grdm.SCHEME, grdm.DOMAIN, self.grdm_token
        )

        options =  dict()
        options[msg_config.get('form', 'selector_default')] = False
        for id, name in projects.items():
            options[name] = id

        self._save_form_box.clear()

        self._save_form = pn.widgets.Select(options=options, value=False)
        self._save_form.param.watch(self._save_project_select_callback, 'value')
        self._save_form_box.append(self._save_form)

        self._save_submit_button.disabled = True
        self._save_submit_button.set_looks_init()
        self._save_submit_button.on_click(self._save_id_callback)
        self._save_form_box.append(self._save_submit_button)

    def _save_project_select_callback(self):
        if self._save_form.value:
            self._save_submit_button.disabled = False

    def _save_id_callback(self, event):
        self.project_id = self._save_form.value
        self._save()

    def _save(self):
        self._save_form_box.clear()
        self.update_msg_info("同期中です。しばらくお待ちください。")
        for path in self._source:
            grdm.sync(
                token=self.grdm_token,
                base_url=grdm.BASE_URL,
                project_id=self.project_id,
                abs_source = path,
                abs_root=self._abs_root_path
            )
        # タスク実行の完了情報を該当サブフローステータス管理JSONに書き込む
        self.update_msg_success("GRDMへの同期が完了しました。")
        self.done_task(self._script_file_name)