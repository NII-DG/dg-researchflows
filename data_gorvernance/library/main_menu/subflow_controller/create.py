"""サブフローの新規作成を行うモジュールです。

このモジュールはサブフロー新規作成クラスを始め、新しいサブフローのデータを用意したり、データの検証を行うメソッドなどがあります。
"""
import json
import os
import traceback
import datetime

from dg_drawer.research_flow import PhaseStatus
import panel as pn
from requests.exceptions import RequestException

from library.utils import file
from library.utils.config import path_config, message as msg_config, connect as con_config
from library.utils.error import InputWarning, UnusableVault, ProjectNotExist, RepoPermissionError, UnauthorizedError
from library.utils.string import StringManager
from library.utils.widgets import MessageBox, Button
from library.main_menu.subflow_controller import utils
from library.utils.storage_provider import grdm
from library.utils.vault import Vault
from .base import BaseSubflowForm


class CreateSubflowForm(BaseSubflowForm):
    """サブフロー新規作成クラスです。

    Attributes:
        instance:
            abs_root (str): リサーチフローのルートディレクトリ
            submit_button(Button):ボタンの設定
            reserch_flow_status_operater(ResearchFlowStatusOperater):リサーチフロー図を生成
            _sub_flow_type_selector(pn.widgets.Select):サブフロー種別(フェーズ)
            _err_output(MessageBox):エラーの出力
            _parent_sub_flow_type_selector(pn.widgets.Select): 親サブフロー種別(フェーズ)
            _parent_sub_flow_selector(pn.widgets.Select):親サブフロー選択
            _sub_flow_name_form(TextInput):サブフロー名のフォーム
            _data_dir_name_form(TextInput):データディレクトリ名のフォーム
    """

    def __init__(self, abs_root: str, widget_box: pn.WidgetBox, message_box: MessageBox) -> None:
        """CreateSubflowForm コンストラクタのメソッドです。

        Args:
            abs_root (str): リサーチフローのルートディレクトリ
            widget_box (pn.WidgetBox): ウィジェットボックスを格納する。
            message_box (MessageBox): メッセージを格納する。
        """
        super().__init__(abs_root, message_box)
        # 処理開始ボタン
        self.change_submit_button_init(msg_config.get('main_menu', 'create_sub_flow'))

        self.grdm = grdm.Grdm()
        self.grdm_url = con_config.get('GRDM', 'BASE_URL')
        self.remote_path = con_config.get('DG_WEB', 'GOVSHEET_PATH')
        self._sub_flow_widget_box = widget_box
        self.govsheet_rf_path = utils.get_govsheet_rf_path(self.abs_root)

        # パーソナルアクセストークンとプロジェクトID入力欄
        self.token_input, self.project_id_input = utils.input_widget()
        self.token_input.param.watch(self.callback_menu_form, 'value_input')
        self.project_id_input.param.watch(self.callback_menu_form, 'value_input')

        # FloatPanelと適用する/しないボタン
        self.float_panel, self.apply_button, self.cancel_button = utils.create_float_panel()
        self.apply_button.on_click(self.callback_apply_button)
        self.cancel_button.on_click(self.callback_cancel_button)

        # 研究準備以外に存在しているフェーズとサブフローIDとサブフロー名の辞書
        self.research_flow_dict = self.reserch_flow_status_operater.get_phase_subflow_id_name()

    def generate_sub_flow_type_options(self, research_flow_status: list[PhaseStatus]) -> dict[str, int]:
        """サブフロー種別(フェーズ)を表示するメソッドです。

        Args:
            research_flow_status (list[PhaseStatus]): リサーチフローステータス管理情報

        Returns:
            dict: フェーズ表示名を返す。
        """
    # サブフロー種別(フェーズ)オプション(表示名をKey、順序値をVauleとする)
        pahse_options = {}
        pahse_options['--'] = 0
        for phase_status in research_flow_status:
            if phase_status._seq_number == 1:
                continue
            else:
                # plan以外の全てのフェーズ
                pahse_options[msg_config.get('research_flow_phase_display_name', phase_status._name)] = phase_status._seq_number
        return pahse_options

    def change_submit_button_init(self, name: str):
        """ボタンの状態を初期化するメソッドです。

        Args:
            name (str): メッセージ
        """
        self.submit_button.set_looks_init(name)
        self.submit_button.icon = 'plus'

    def is_display_widgets(self):
        """入力欄の表示切り替えを行うメソッドです。"""
        try:
            token = utils.get_token()
            project_id = utils.get_project_id()
            if token is None and project_id is None:
                self.token_input.visible = True
                self.project_id_input.visible = True
            elif project_id is None:
                self.project_id_input.visible = True
                self.token = token
            elif token is None:
                self.token_input.visible = True
                self.project_id = project_id
            else:
                if utils.check_grdm_token(self.grdm_url, token):
                    if utils.check_grdm_access(self.grdm_url, token, project_id):
                        self.token = token
                        self.project_id = project_id
                    else:
                        self._err_output.update_error(msg_config.get('form', 'project_id_not_exist'))
                        return
                else:
                    self.token_input.visible = True
                    self.project_id_input.visible = True
        except UnusableVault:
            message = msg_config.get('from', 'no_vault')
            self._err_output.update_error(message)
        except Exception:
            message = f'## [INTERNAL ERROR] : {traceback.format_exc()}'
            self._err_output.update_error(message)

    def callback_apply_button(self, event):
        """デフォルトのガバナンスシートで登録するメソッドです。

        Args:
            event: ボタンクリックイベント
        """
        self.float_panel.visible = False

        # デフォルトでガバナンスシートを作成する
        govsheet_path = os.path.join(self.abs_root, self.remote_path)
        govsheet_file = file.JsonFile(govsheet_path)
        try:
            schema = utils.get_schema()
            data = utils.get_default_govsheet(schema)
            govsheet_file.write(data)
            self.grdm.sync(self.token, self.grdm_url, self.project_id, govsheet_path, self.abs_root)
        except UnauthorizedError:
            message = msg_config.get('form', 'token_unauthorized')
            self._err_output.update_warning(message)
            return
        except RequestException as e:
            message = msg_config.get('DEFAULT', 'connection_error')
            self._err_output.update_error(f'{message}\n{str(e)}')
            return
        except Exception:
            message = f'## [INTERNAL ERROR] : {traceback.format_exc()}'
            self._err_output.update_error(message)
            return
        finally:
            govsheet_file.remove(missing_ok=True)

        # サブフローを作り直す
        utils.recreate_subflow(
            self.abs_root, self.govsheet_rf_path, self.govsheet_rf, self.govsheet, self.research_flow_dict)
        self.new_create_subflow(
            self._sub_flow_type_selector.value,
            self._sub_flow_name_form.value_input,
            self._data_dir_name_form.value_input,
            self._parent_sub_flow_selector.value
        )
        sync_path_list = utils.get_sync_path(self.abs_root)
        for sync_path in sync_path_list:
            self.grdm.sync(self.token, self.grdm_url, self.project_id, sync_path, self.abs_root)

    def callback_cancel_button(self, event):
        """適用しない押下後エラーメッセージを表示するメソッドです。

        Args:
            event: ボタンクリックイベント
        """
        self._err_output.clear()
        self.cancel_button.set_looks_processing()
        self.float_panel.visible = False
        msg = msg_config.get('main_menu', 'create_task_govsheet')
        self._err_output.update_warning(msg)

    # overwrite
    def callback_sub_flow_type_selector(self, event):
        """サブフロー種別(フェーズ)のボタンが操作できるように有効化するメソッドです。"""
        # サブフロー種別(フェーズ):シングルセレクトコールバックファンクション
        try:
            # リサーチフローステータス管理情報の取得
            research_flow_status = self.reserch_flow_status_operater.load_research_flow_status()

            selected_value = self._sub_flow_type_selector.value
            if selected_value is None:
                raise Exception('Sub Flow Type Selector has None')
            # 親サブフロー種別(フェーズ)（必須)：シングルセレクトの更新
            parent_sub_flow_type_options = self.generate_parent_sub_flow_type_options(selected_value, research_flow_status)
            self._parent_sub_flow_type_selector.options = parent_sub_flow_type_options
            # 新規作成ボタンのボタンの有効化チェック
            self.change_disable_submit_button()
        except Exception:
            self._err_output.update_error(f'## [INTERNAL ERROR] : {traceback.format_exc()}')

    # overwrite
    def change_disable_submit_button(self):
        """サブフロー新規作成フォームの必須項目が選択・入力が満たしている場合、新規作成ボタンを有効化するメソッドです。"""
        # サブフロー新規作成フォームの必須項目が選択・入力が満たしている場合、新規作成ボタンを有効化する
        self.change_submit_button_init(msg_config.get('main_menu', 'create_sub_flow'))

        value = self._sub_flow_type_selector.value
        if value is None:
            self.submit_button.disabled = True
            return
        elif int(value) == 0:
            self.submit_button.disabled = True
            return

        value = self._sub_flow_name_form.value_input
        if value is None:
            self.submit_button.disabled = True
            return
        elif len(value) < 1:
            self.submit_button.disabled = True
            return

        value = self._data_dir_name_form.value_input
        if value is None:
            self.submit_button.disabled = True
            return
        elif len(value) < 1:
            self.submit_button.disabled = True
            return

        value = self._parent_sub_flow_type_selector.value
        if value is None:
            self.submit_button.disabled = True
            return
        elif int(value) == 0:
            self.submit_button.disabled = True
            return

        value = self._parent_sub_flow_selector.value
        if value is None:
            self.submit_button.disabled = True
            return
        elif len(value) < 1:
            self.submit_button.disabled = True
            return

        if self.project_id_input.visible:
            value = self.project_id_input.value_input
            if value is None:
                self.submit_button.disabled = True
                return
            elif len(value) < 1:
                self.submit_button.disabled = True
                return

        if self.token_input.visible:
            value = self.token_input.value_input
            if value is None:
                self.submit_button.disabled = True
                return
            elif len(value) < 1:
                self.submit_button.disabled = True
                return

        self.submit_button.disabled = False

    def define_input_form(self) -> pn.Column:
        """サブフロー新規作成フォームのメソッドです。

        Returns:
            pn.Column:サブフロー新規作成フォームに必要な値を返す。
        """
        self.is_display_widgets()
        return pn.Column(
            f'### {msg_config.get("main_menu", "create_sub_flow_title")}',
            self._sub_flow_type_selector,
            self._sub_flow_name_form,
            self._data_dir_name_form,
            self._parent_sub_flow_type_selector,
            self._parent_sub_flow_selector,
            self.token_input,
            self.project_id_input,
            self.submit_button
        )

    def main(self):
        """サブフロー新規作成処理のメソッドです。

        入力情報を取得し、その値を検証してリサーチフローステータス管理JSONの更新、新規サブフローデータの用意を行う。

        Raises:
            InputWarning:入力値の不備によるエラー
            Exception:データ取得、更新が失敗したエラー
        """

        # 新規作成ボタンを処理中ステータスに更新する
        self.change_submit_button_processing(msg_config.get('main_menu', 'creating_sub_flow'))

        # 入力情報を取得する。
        phase_seq_number = self._sub_flow_type_selector.value
        sub_flow_name = self._sub_flow_name_form.value_input
        data_dir_name = self._data_dir_name_form.value_input
        parent_sub_flow_ids = self._parent_sub_flow_selector.value
        token = self.token_input.value_input
        project_id = self.project_id_input.value_input

        # 入力値の検証
        try:
            sub_flow_name = StringManager.strip(sub_flow_name)
            self.validate_sub_flow_name(sub_flow_name)
            self.is_unique_subflow_name(sub_flow_name, phase_seq_number)

            data_dir_name = StringManager.strip(data_dir_name)
            self.validate_data_dir_name(data_dir_name)
            self.is_unique_data_dir(data_dir_name, phase_seq_number)

            token = StringManager.strip(token)
            project_id = StringManager.strip(project_id)

            if self.token_input.visible and self.project_id_input.visible:
                if token:
                    utils.validate_input_token(token)
                if project_id:
                    utils.validate_input_project_id(project_id)
            elif self.token_input.visible:
                if token:
                    utils.validate_input_token(token)
            else:
                if project_id:
                    utils.validate_input_project_id(project_id)
        except InputWarning as e:
            self.change_submit_button_warning(str(e))
            raise

        # 接続確認
        try:
            vault = Vault()
            if token and project_id:
                if utils.check_grdm_token(self.grdm_url, token):
                    vault.set_value('grdm_token', token)
                    if utils.check_grdm_access(self.grdm_url, token, project_id):
                        self.token = token
                        self.project_id = project_id
                    else:
                        self.change_submit_button_error(msg_config.get('form', 'project_id_not_exist'))
                        return
                else:
                    self.change_submit_button_warning(msg_config.get('form', 'token_unauthorized'))
                    return
            elif token:
                if utils.check_grdm_token(self.grdm_url, token):
                    vault.set_value('grdm_token', token)
                    if utils.check_grdm_access(self.grdm_url, token, self.project_id):
                        self.token = token
                    else:
                        self.change_submit_button_error(msg_config.get('form', 'project_id_not_exist'))
                        return
                else:
                    self.change_submit_button_warning(msg_config.get('form', 'token_unauthorized'))
                    return
            else:
                if utils.check_grdm_access(self.grdm_url, self.token, project_id):
                    self.project_id = project_id
                else:
                    self.change_submit_button_error(msg_config.get('form', 'project_id_not_exist'))
                    return
        except UnusableVault:
            message = msg_config.get('form', 'no_vault')
            self.change_submit_button_warning(message)

        # ガバナンスシート取得
        try:
            self.govsheet = utils.get_govsheet(self.token, self.grdm_url, self.project_id, self.remote_path)
        except FileNotFoundError:
            self.govsheet = None
        except json.JSONDecodeError:
            self.govsheet = {}
        except UnauthorizedError:
            message = msg_config.get('form', 'token_unauthorized')
            self._err_output.update_warning(message)
        except RequestException as e:
            message = msg_config.get('dg_web', 'get_data_error')
            self._err_output.update_error(f'{message}\n{str(e)}')
        except Exception as e:
            message = msg_config.get('dg_web', 'get_data_error')
            self._err_output.update_error(f'{message}\n{str(e)}')

        self.govsheet_path = os.path.join(self.abs_root, self.remote_path)
        self.govsheet_rf = utils.get_govsheet_rf(self.abs_root)

        if self.research_flow_dict:
            self.recreate_current_subflow()
        if self.float_panel.visible:
            return
        if not self.govsheet_rf:
            file.JsonFile(self.govsheet_rf_path).write(self.govsheet)
        self.new_create_subflow(phase_seq_number, sub_flow_name, data_dir_name, parent_sub_flow_ids)
        sync_path_list = utils.get_sync_path(self.abs_root)
        for sync_path in sync_path_list:
            self.grdm.sync(self.token, self.grdm_url, self.project_id, sync_path, self.abs_root)

    def recreate_current_subflow(self):
        """既存のサブフローを作り直すメソッドです。"""
        if not self.govsheet_rf and not self.govsheet:
            self.float_panel.visible = True
            self._sub_flow_widget_box.append(self.float_panel)
            return

        utils.recreate_subflow(
            self.abs_root, self.govsheet_rf_path, self.govsheet_rf, self.govsheet, self.research_flow_dict)

    def update_new_status_and_preparation_notebook(self, phase_name: str, new_subflow_id: str):
        """新規サブフローのstatus.jsonを更新し、必要なタスクノートブックを用意するメソッドです。

        Args:
            new_phase_name (str): フェーズ名
            new_subflow_id (str): 新しいサブフローのID
        """
        new_status_file = os.path.join(
            self.abs_root,
            path_config.get_sub_flow_status_file_path(phase_name, new_subflow_id)
        )
        new_working_path = os.path.join(
            self.abs_root,
            path_config.DG_WORKING_RESEARCHFLOW_FOLDER,
            phase_name,
            new_subflow_id,
            path_config.TASK
        )
        utils.update_status_file(self.abs_root, new_status_file)
        utils.preparation_notebook_file(self.abs_root, new_status_file, new_working_path)

    def create_data_dir(self, phase_name: str, data_dir_name: str) -> str:
        """データディレクトリを作成するメソッドです。

        Args:
            phase_name (str): フェーズ名
            data_dir_name (str): データディレクトリ名

        Raises:
            Exception: 既にファイルが存在しているエラー

        Returns:
            str: データディレクトリを作成するパスの値を返す。
        """
        path = path_config.get_task_data_dir(self.abs_root, phase_name, data_dir_name)
        if os.path.exists(path):
            raise Exception(f'{path} is already exist.')
        os.makedirs(path)
        return path

    def new_create_subflow(self, phase_seq_number: int, sub_flow_name: str, data_dir_name: str, parent_sub_flow_ids: list[str]):
        """新規サブフローを作成するメソッドです。

        Args:
            phase_seq_number (int): サブフローを作成するフェーズのシーケンス番号
            sub_flow_name (str): 新規サブフロー名
            data_dir_name (str): 作成するディレクトリ
            parent_sub_flow_ids (str)): 親サブフロー名

        Raises:
            InputWarning: 入力不備によるエラー
        """
        # リサーチフローステータス管理JSONの更新
        try:
            phase_name, new_sub_flow_id = self.reserch_flow_status_operater.create_sub_flow(
                phase_seq_number, sub_flow_name, data_dir_name, parent_sub_flow_ids
            )
        except Exception:
            self.change_submit_button_error(msg_config.get('main_menu', 'error_create_sub_flow'))
            raise

        # /data/<phase_name>/<data_dir_name>の作成
        data_dir_path = ""
        try:
            data_dir_path = self.create_data_dir(phase_name, data_dir_name)
        except Exception as e:
            # ディレクトリ名が存在した場合
            # リサーチフローステータス管理JSONをロールバック
            self.reserch_flow_status_operater.del_sub_flow_data_by_sub_flow_id(new_sub_flow_id)
            # ユーザーに再入力を促す
            message = msg_config.get('main_menu', 'data_directory_exist')
            self.change_submit_button_warning(message)
            raise InputWarning(message) from e

        # 新規サブフローデータの用意
        try:
            utils.prepare_new_subflow_data(self.abs_root, phase_name, new_sub_flow_id, sub_flow_name, False)
            self.update_new_status_and_preparation_notebook(phase_name, new_sub_flow_id)
        except Exception:
            # 失敗した場合に/data/<phase_name>/<data_dir_name>の削除
            os.remove(data_dir_path)
            # 失敗した場合は、リサーチフローステータス管理JSONをロールバック
            self.reserch_flow_status_operater.del_sub_flow_data_by_sub_flow_id(new_sub_flow_id)
            # 新規作成ボタンを作成失敗ステータスに更新する
            self.change_submit_button_error(msg_config.get('main_menu', 'error_create_sub_flow'))
            raise

        # フォームの初期化
        self._sub_flow_type_selector.value = 0
        self._sub_flow_name_form.value = ''
        self._sub_flow_name_form.value_input = ''
        self._data_dir_name_form.value = ''
        self._data_dir_name_form.value_input = ''
        self.project_id_input.value = ''
        self.project_id_input.value_input = ''
        self.token_input.value = ''
        self.token_input.value_input = ''
        self.change_submit_button_init(msg_config.get('main_menu', 'create_sub_flow'))