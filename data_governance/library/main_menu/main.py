"""メインメニュー画面での操作のモジュールです。

このモジュールはメインメニューの画面やボタンを表示するメソッドやサブフローメニューの画面の表示、操作を行えるメソッドなどがあります。
"""
import datetime
import json
import os
import traceback

from IPython.core.display import Javascript
from IPython.display import display
import panel as pn
from requests.exceptions import RequestException

from library.utils.config import path_config, message as msg_config, connect as con_config
from library.utils.error import InputWarning, UnusableVault, ProjectNotExist, UnauthorizedError
from library.utils.html import button as html_button
from library.utils.log import TaskLog
from library.utils.setting import ResearchFlowStatusOperater, SubflowStatusFile
from library.utils.string import StringManager
from library.utils.storage_provider import grdm
from library.utils import file
from library.utils.vault import Vault
from library.utils.widgets import MessageBox, Button
from library.main_menu.subflow_controller import (
    CreateSubflowForm,
    RelinkSubflowForm,
    RenameSubflowForm,
    DeleteSubflowForm,
    utils
)

# git clone https://github.com/NII-DG/dg-researchflows.git -b feature/main_menu_v2 ./demo
# mv ./demo/* ./
# rm -rf ./demo


class MainMenu(TaskLog):
    """メインメニューのクラスです。

    Attributes:

        instance:
            abs_root(str): リサーチフローのルートディレクトリ
            _research_flow_status_file_path(str): リサーチフロー図があるパス
            reserch_flow_status_operater(ResearchFlowStatusOperater):リサーチフロー図の生成
            _research_flow_image(pn.pane.HTML): リサーチフロー図オブジェクトの定義
            _err_output(MessageBox):エラーの出力
            _menu_tabs(pn.Tabs):メニュータブ
            button_for_project_menu(pn.pane.HTML):メインメニューに遷移するためのボタン
            _project_menu(pn.pane.HTML):プロジェクトメニュー
            _project_widget_box(pn.WidgetBox):サブフロー操作コントローラーウェジットボックス
            _sub_flow_menu(pn.widgets.Select):サブフローメニュー
            _sub_flow_widget_box(pn.WidgetBox):サブフロー操作コントローラーウェジットボックス
            grdm(Grdm):grdmファイルのGrdmクラス
            grdm_url(str):GRDMのクラス
            remote_path(str):リモート先のパス
            govsheet_rf_path(str):RFガバナンスシートのパス
            research_flow_widget_box(pn.WidgetBox):ガバナンスシート適用ウィジェットボックス
            research_flow_message(MessageBox):ガバナンスシート適用メッセージオブジェクト
            apply_govsheet_button(Button):ガバナンスシート適用ボタン
            token_input(pn.widgets.PasswordInput):パーソナルアクセストークンの入力欄
            project_id_input(pn.widgets.TextInput):プロジェクトIDの入力欄
            input_button(Button):確定ボタン
            float_panel(pn.layout.FloatPanel):FloatPanel
            apply_button(Button):適用するボタン
            cancel_button(Button):適用しないボタン
            token(str):パーソナルアクセストークン
            project_id(str):プロジェクトID
            tmp_project_id(str):一時的に保持するプロジェクトID
            callback_type(str):呼び出すメソッドのタイプ
            subflow_form(CreateSubflowForm | RelinkSubflowForm | RenameSubflowForm | DeleteSubflowForm):サブフローのフォーム
            research_flow_dict(dict):存在するフェーズをkeyとし対応するサブフローIDとサブフロー名をvalueとした辞書

    NOTE:
    Called from data_governance/researchflow/main.ipynb
    """

    def __init__(self, working_file: str) -> None:
        """MainMenu コンストラクタのメソッドです。

        Args:
            working_file(str):実行Notebookファイルパス

        """
        super().__init__(working_file, 'main.ipynb')

        ##############################
        # リサーチフロー図オブジェクト #
        ##############################
        self.abs_root = path_config.get_abs_root_form_working_dg_file_path(working_file)
        # リサーチフロー図の生成
        # data_governance\researchflow\research_flow_status.json
        self._research_flow_status_file_path = path_config.get_research_flow_status_file_path(self.abs_root)

        self.reserch_flow_status_operater = ResearchFlowStatusOperater(self._research_flow_status_file_path)
        # プロジェクトで初回のリサーチフロー図アクセス時の初期化
        self.reserch_flow_status_operater.init_research_preparation()
        # リサーチフロー図オブジェクトの定義
        self._research_flow_image = pn.pane.HTML(
            self.reserch_flow_status_operater.get_svg_of_research_flow_status()
        )
        self._research_flow_image.width = 1000

        ######################################
        # システムエラーメッセージオブジェクト #
        ######################################

        # システムエラーメッセージオブジェクトの定義
        self._err_output = MessageBox()
        self._err_output.width = 900

        ################################
        # 機能コントローラーオブジェクト #
        ################################
        # 機能コントローラーの定義
        self._menu_tabs = pn.Tabs()

        # プロジェクト操作コントローラーの定義
        # 遷移ボタン for プロジェクト操作コントローラー
        self.button_for_project_menu = pn.pane.HTML()
        self.button_for_project_menu.object = html_button.create_button(
            msg=msg_config.get('main_menu', 'disable_jump_button'),
            disable=True, border=['dashed', '1px'], button_background_color='#ffffff'
        )
        # プロジェクト操作アクションセレクタ―
        project_menu_title = msg_config.get('main_menu', 'project_menu_title')
        project_menu_options = dict()
        project_menu_options[msg_config.get('form', 'selector_default')] = 0
        project_menu_options[msg_config.get('main_menu', 'edit_governance_sheet_title')] = 1
        project_menu_options[msg_config.get('main_menu', 'verification_results_title')] = 2
        project_menu_options[msg_config.get('main_menu', 'monitoring_settings_title')] = 3
        project_menu_options[msg_config.get('main_menu', 'update_dmp_title')] = 4
        project_menu_options[msg_config.get('main_menu', 'finish_research_title')] = 5
        self._project_menu = pn.widgets.Select(options=project_menu_options, value=0)

        # プロジェクト操作アクションセレクタ―のイベントリスナー
        self._project_menu.param.watch(self.callback_project_menu, 'value')

        # サブフロー操作コントローラーウェジットボックス（後からなんでもいれる事ができます）
        self._project_widget_box = pn.WidgetBox()
        self._project_widget_box.width = 900

        # サブフロー操作コントローラーの定義
        # サブフロー操作コントローラーオプション
        sub_flow_menu_title = msg_config.get(
            'main_menu', 'sub_flow_menu_title')
        sub_flow_menu_options = dict()
        sub_flow_menu_options[msg_config.get('form', 'selector_default')] = 0
        sub_flow_menu_options[msg_config.get('main_menu', 'create_sub_flow_title')] = 1
        sub_flow_menu_options[msg_config.get('main_menu', 'update_sub_flow_link_title')] = 2
        sub_flow_menu_options[msg_config.get('main_menu', 'update_sub_flow_name_title')] = 3
        sub_flow_menu_options[msg_config.get('main_menu', 'delete_sub_flow_title')] = 4
        # サブフロー操作コントローラー
        self._sub_flow_menu = pn.widgets.Select(options=sub_flow_menu_options, value=0)
        # サブフロー操作コントローラーのイベントリスナー
        self._sub_flow_menu.param.watch(self.callback_sub_flow_menu, 'value')
        # サブフロー操作コントローラーウェジットボックス（後からなんでもいれる事ができます）
        self._sub_flow_widget_box = pn.WidgetBox()
        self._sub_flow_widget_box.width = 900
        self.update_sub_flow_widget_box_for_init()

        sub_flow_menu_layout = pn.Column(
            self._sub_flow_menu,
            self._sub_flow_widget_box
        )
        project_menu_layout = pn.Column(
            pn.Row(self._project_menu, self.button_for_project_menu),
            self._project_widget_box
        )

        self._menu_tabs.append((sub_flow_menu_title, sub_flow_menu_layout))  # tab_index = 0
        # 未開発のためコメントアウト
        # self._menu_tabs.append((project_menu_title, project_menu_layout)) # tab_index = 1
        # 機能コントローラーのイベントリスナー
        self._menu_tabs.param.watch(self.callback_menu_tabs, 'active')

        # TODO:研究準備の実行ステータス確認をする。
        # ファイル：data_governance\researchflow\plan\status.json
        # 必須タスクが全て1回以上実行完了していない場合、研究準備サブフローへ誘導する。
        # サブフロー操作コントローラーを無効化する。
        # 必須タスクが完了している場合は、何もしない
        self.check_status_research_preparation_flow()

        ################################
        # ガバナンスシート適用 #
        ################################
        self.grdm = grdm.Grdm()
        self.grdm_url = con_config.get('GRDM', 'BASE_URL')
        self.remote_path = con_config.get('DG_WEB', 'GOVSHEET_PATH')
        self.govsheet_rf_path = utils.get_govsheet_rf_path(self.abs_root)

        pn.extension('floatpanel')

        # ガバナンスシート適用ウィジェットボックス
        self.research_flow_widget_box = pn.WidgetBox()
        self.research_flow_widget_box.width = 900
        # ガバナンスシート適用メッセージオブジェクト
        self.research_flow_message = MessageBox()
        self.research_flow_message.width = 900

        # ガバナンスシート適用ボタン
        self.apply_govsheet_button = Button(width=10)
        self.apply_govsheet_button.on_click(self._handle_click)

        # パーソナルアクセストークンとプロジェクトID入力欄
        self.token_input, self.project_id_input = utils.input_widget()
        self.token_input.param.watch(self.input, 'value_input')
        self.project_id_input.param.watch(self.input, 'value_input')
        # 確定ボタン
        self.input_button = Button(disabled=True, align='end')
        self.input_button.set_looks_init()
        self.input_button.on_click(self.callback_input_button)

        # FloatPanel、デフォルトのガバナンスシートを作成する/しないボタン
        self.float_panel, self.apply_button, self.cancel_button = utils.create_float_panel()
        self.apply_button.on_click(self._handle_default_click)
        self.cancel_button.on_click(self.callback_cancel_button)

        self.update_research_flow_widget_box_init()

    def check_status_research_preparation_flow(self):
        """研究準備の実行ステータス確認をするメソッドです。"""
        sf = SubflowStatusFile(os.path.join(self.abs_root, path_config.PLAN_TASK_STATUS_FILE_PATH))
        plan_sub_flow_status = sf.read()
        for plan_status in plan_sub_flow_status.tasks:
            if plan_status.is_required and plan_status.completed_count < 1:
                plan_sub_flow_status._is_completed = False
        plan_sub_flow_status._is_completed = True
        # 研究準備サブフローの進行状況をチェックする。
        if plan_sub_flow_status.is_completed:
            # 必須タスクが全て完了している場合、何もしない。
            pass
        else:
            # 未完了必須タスクがある場合、以下の処理をする。
            # サブフロー操作コントローラーを無効化
            self._sub_flow_menu.disabled = True
            # プロジェクト操作コントローラーを無効化
            self._project_menu.disabled = True
            # アラートを表示する。
            alert = pn.pane.Alert(
                msg_config.get('main_menu', 'required_research_preparation'),
                sizing_mode="stretch_width", alert_type='warning'
            )
            self._sub_flow_widget_box.clear()
            self._sub_flow_widget_box.append(alert)

    ######################################
    # イベントリスナーコールバックメソッド #
    ######################################

    def callback_menu_tabs(self, event):
        """サブフロー操作で選択ができるようにするメソッドです。

        Args:
            event: 機能コントローラーのイベントリスナー
        """
        try:
            self._err_output.clear()
            tab_index = event.new
            if tab_index == 0:
                # サブフロー操作が選択
                # サブフロー操作コントローラーオプションを初期化
                self._sub_flow_menu.value = 0
                self._project_widget_box.clear()
                self.check_status_research_preparation_flow()
            if tab_index == 1:
                # プロジェクト操作が選択
                self._project_menu.value = 0
                self._sub_flow_widget_box.clear()
        except Exception:
            self._err_output.update_error(f'## [INTERNAL ERROR] : {traceback.format_exc()}')

    def callback_project_menu(self, event):
        """プロジェクト操作コントローラーの更新をするための遷移ボタンのメソッドです。"""
        # 開発中のためアラートを表示する。
        try:
            self._err_output.clear()
            self._project_widget_box.clear()
            alert = pn.pane.Alert(
                msg_config.get('DEFAULT', 'developing'),
                sizing_mode="stretch_width", alert_type='warning'
            )
            self._project_widget_box.append(alert)
        except Exception:
            self._err_output.update_error(f'## [INTERNAL ERROR] : {traceback.format_exc()}')

    def callback_sub_flow_menu(self, event):
        """サブフロー操作コントローラーオプションによるサブフロー操作フォームを表示するメソッドです。"""
        try:
            self._err_output.clear()
            selected_value = self._sub_flow_menu.value
            if selected_value == 0:  # 選択なし
                self.update_sub_flow_widget_box_for_init()
                return
            elif selected_value == 1:  # サブフロー新規作成
                self.callback_type = "create"
                self.subflow_form = CreateSubflowForm(self.abs_root, self._sub_flow_widget_box, self._err_output, self._research_flow_image)
            elif selected_value == 2:  # サブフロー間接続編集
                self.callback_type = "relink"
                self.subflow_form = RelinkSubflowForm(self.abs_root, self._err_output)
            elif selected_value == 3:  # サブフロー名称変更
                self.callback_type = "rename"
                self.subflow_form = RenameSubflowForm(self.abs_root, self._err_output)
            elif selected_value == 4:  # サブフロー削除
                self.callback_type = "delete"
                self.subflow_form = DeleteSubflowForm(self.abs_root, self._err_output)
            self.update_sub_flow_widget_box()
        except Exception as e:
            self._err_output.update_error(f'## [INTERNAL ERROR] : {traceback.format_exc()}')

    #########################
    # サブフロー操作フォーム #
    #########################

    def update_sub_flow_widget_box_for_init(self):
        """サブフロー操作オプションの選択誘導するメソッドです。"""
        self._sub_flow_widget_box.clear()
        alert = pn.pane.Alert(
            msg_config.get('main_menu', 'guide_select_action'),
            sizing_mode="stretch_width", alert_type='info'
        )
        self._sub_flow_widget_box.append(alert)

    def update_sub_flow_widget_box(self):
        """サブフロー操作フォームの表示するメソッドです。"""
        # ボタンのイベントリスナー
        self.subflow_form.set_submit_button_on_click(self.callback_submit_button)

        sub_flow_form_layout = self.subflow_form.define_input_form()
        self._sub_flow_widget_box.clear()
        self._sub_flow_widget_box.append(sub_flow_form_layout)
        # ボタンの無効化をする（最初の設定が反映されないため）
        self.subflow_form.submit_button.disabled = True

    async def callback_submit_button(self, event):
        """サブフローのボタンを呼び戻すメソッドです。"""
        try:
            # start
            self.subflow_form.log.start(detail=self.callback_type)
            await self.subflow_form.main()

            # サブフロー関係図を更新
            self._research_flow_image.object = self.reserch_flow_status_operater.get_svg_of_research_flow_status()
            display(Javascript('IPython.notebook.save_checkpoint();'))
            # end
            self.subflow_form.log.finish(detail=self.callback_type)
        except InputWarning:
            self.log.warning(traceback.format_exc())
        except Exception:
            message = f'## [INTERNAL ERROR] : {traceback.format_exc()}'
            self.log.error(message)
            self._err_output.update_error(message)

    ################################
    # ガバナンスシート適用 #
    ################################

    def update_research_flow_widget_box_init(self):
        """ガバナンスシート適用ボタンを表示するメソッドです。"""
        self.research_flow_widget_box.clear()
        apply_govsheet_button_title = msg_config.get('main_menu', 'apply_govsheet')
        button = pn.Row(
            pn.Spacer(width=700),
            self.apply_govsheet_button
        )
        self.apply_govsheet_button.set_looks_init(apply_govsheet_button_title)
        self.research_flow_widget_box.append(button)

    def display_input_box(self):
        """パーソナルアクセストークンとプロジェクトIDの入力欄と確定ボタン表示用メソッドです。"""
        self.research_flow_widget_box.clear()
        input_layout = pn.Row(
            self.token_input,
            self.project_id_input,
            self.input_button
        )
        self.token_input.value = ''
        self.project_id_input.value = ''
        self.input_button.set_looks_init()
        self.research_flow_widget_box.append(input_layout)
        self.input_button.disabled = True

    async def _handle_click(self, event):
        """非同期処理の実行のための仲介メソッドです"""
        await self.apply_click(event)

    @TaskLog.callback_form('ガバナンスシートを適用する')
    async def apply_click(self, event):
        """ガバナンスシート適用ボタンを押下されたときにガバナンスシートを適用するメソッドです。

        Args:
            event: ボタンクリックイベント
        """
        self.research_flow_message.clear()
        self.token_input.value = ''
        self.project_id_input.value = ''
        self.apply_govsheet_button.set_looks_processing()
        try:
            token = utils.get_token()
            project_id = utils.get_project_id()

            if project_id is None and token is None:
                self.project_id_input.visible = True
                self.token_input.visible = True
            elif token is None:
                self.token_input.visible = True
                self.tmp_project_id = project_id
            elif project_id is None:
                self.project_id_input.visible = True
                self.token = token
            else:
                if utils.check_grdm_token(self.grdm_url, token):
                    if utils.check_grdm_access(self.grdm_url, token, project_id):
                        self.token = token
                        self.project_id = project_id
                        await self.operation_file()
                        return
                    else:
                        self.research_flow_widget_box.clear()
                        self.research_flow_message.update_error(msg_config.get('form', 'insufficient_permission'))
                        return
                else:
                    self.token_input.visible = True
                    self.project_id_input.visible = True
            self.display_input_box()

        except UnauthorizedError:
            self.display_input_box()
            message = msg_config.get('main_menu', 're_enter_token')
            self.research_flow_message.update_warning(message)
            self.log.warning(f'{message}\n{traceback.format_exc()}')
            return
        except ProjectNotExist:
            self.research_flow_widget_box.clear()
            message = msg_config.get('form', 'project_id_not_exist').format(project_id)
            self.research_flow_message.update_error(message)
            self.log.error(f'{message}\n{traceback.format_exc()}')
            return
        except RequestException as e:
            self.research_flow_widget_box.clear()
            message = msg_config.get('DEFAULT', 'connection_error')
            self.research_flow_message.update_error(f'{message}\n{str(e)}')
            self.log.error(f'{message}\n{traceback.format_exc()}')
            return
        except Exception as e:
            self.research_flow_widget_box.clear()
            message = f'## [INTERNAL ERROR] : {traceback.format_exc()}'
            self.research_flow_message.update_error(message)
            self.log.error(message)
            return

    def input(self, event):
        """確定ボタンを有効化するメソッドです

        Args:
            event: 入力イベント
        """
        self.token_input.value_input = StringManager.strip(self.token_input.value_input)
        self.project_id_input.value_input = StringManager.strip(self.project_id_input.value_input)
        try:
            if self.token_input.visible and self.project_id_input.visible:
                if self.token_input.value_input and self.project_id_input.value_input:
                    utils.validate_input_token(self.token_input.value_input)
                    utils.validate_input_project_id(self.project_id_input.value_input)
                    self.input_button.disabled = False

            elif self.token_input.visible:
                if self.token_input.value_input:
                    utils.validate_input_token(self.token_input.value_input)
                    self.input_button.disabled = False
            else:
                if self.project_id_input.value_input:
                    utils.validate_input_project_id(self.project_id_input.value_input)
                    self.input_button.disabled = False
        except InputWarning as e:
            self.input_button.disabled = True
            self.research_flow_message.update_warning(str(e))

    @TaskLog.callback_form('入力されたパーソナルアクセストークン及びプロジェクトIDでガバナンスシートを適用する')
    async def callback_input_button(self, event):
        """入力されたパーソナルアクセストークン及びプロジェクトIDでガバナンスシート適用をするメソッドです。

        Args:
            event: クリックイベント
        """
        self.input_button.set_looks_processing()

        if self.token_input.visible:
            if not self.token_input.value_input:
                self.input_button.set_looks_init()
                self.research_flow_message.update_warning(msg_config.get('main_menu', 'not_input_token'))
                return
        if self.project_id_input.visible:
            if not self.project_id_input.value_input:
                self.input_button.set_looks_init()
                self.research_flow_message.update_warning(msg_config.get('main_menu', 'not_input_project_id'))
                return

        try:
            vault = Vault()
            if self.token_input.value_input and self.project_id_input.value_input:
                self.tmp_project_id = self.project_id_input.value_input
                if utils.check_grdm_token(self.grdm_url, self.token_input.value_input):
                    vault.set_value('grdm_token', self.token_input.value_input)
                    if utils.check_grdm_access(self.grdm_url, self.token_input.value_input, self.tmp_project_id):
                        self.token = self.token_input.value_input
                        self.project_id = self.tmp_project_id
                        self.token_input.visible = False
                        self.project_id_input.visible = False
                        await self.operation_file()
                    else:
                        self.research_flow_widget_box.clear()
                        self.research_flow_message.update_error(msg_config.get('form', 'insufficient_permission'))
                        return
                else:
                    self.research_flow_message.update_warning(msg_config.get('main_menu', 're_enter_token'))
                    self.display_input_box()
                    return
            elif self.token_input.value_input:
                if utils.check_grdm_token(self.grdm_url, self.token_input.value_input):
                    vault.set_value('grdm_token', self.token_input.value_input)
                    if utils.check_grdm_access(self.grdm_url, self.token_input.value_input, self.tmp_project_id):
                        self.token = self.token_input.value_input
                        self.project_id = self.tmp_project_id
                        await self.operation_file()
                    else:
                        self.research_flow_widget_box.clear()
                        self.research_flow_message.update_error(msg_config.get('form', 'insufficient_permission'))
                        return
                else:
                    self.research_flow_message.update_warning(msg_config.get('main_menu', 're_enter_token'))
                    self.display_input_box()
                    return
            else:
                self.tmp_project_id = self.project_id_input.value_input
                if utils.check_grdm_access(self.grdm_url, self.token, self.tmp_project_id):
                    self.project_id = self.tmp_project_id
                    await self.operation_file()
                else:
                    self.research_flow_widget_box.clear()
                    self.research_flow_message.update_error(msg_config.get('form', 'insufficient_permission'))
                    return

        except UnusableVault:
            self.research_flow_widget_box.clear()
            message = msg_config.get('form', 'no_vault')
            self.research_flow_message.update_error(message)
            self.log.error(f'{message}\n{traceback.format_exc()}')
        except UnauthorizedError:
            self.display_input_box()
            message = msg_config.get('main_menu', 're_enter_token')
            self.research_flow_message.update_warning(message)
            self.log.warning(f'{message}\n{traceback.format_exc()}')
        except ProjectNotExist:
            self.research_flow_widget_box.clear()
            message = msg_config.get('form', 'project_id_not_exist').format(self.tmp_project_id)
            self.research_flow_message.update_error(message)
            self.log.error(f'{message}\n{traceback.format_exc()}')
        except RequestException as e:
            self.research_flow_widget_box.clear()
            message = msg_config.get('DEFAULT', 'connection_error')
            self.research_flow_message.update_error(f'{message}\n{str(e)}')
            self.log.error(f'{message}\n{traceback.format_exc()}')
        except Exception:
            self.research_flow_widget_box.clear()
            message = f'## [INTERNAL ERROR] : {traceback.format_exc()}'
            self.research_flow_message.update_error(message)
            self.log.error(message)

    async def operation_file(self):
        """ガバナンスシートを適用して必要なファイルを用意するメソッドです。"""
        self.research_flow_message.clear()
        self.research_flow_dict = self.reserch_flow_status_operater.get_phase_subflow_id_name()
        govsheet_rf = utils.get_govsheet_rf(self.abs_root)
        current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        mapping_file = utils.get_mapping_file(self.abs_root)

        govsheet = None
        try:
            govsheet = await utils.get_govsheet(self.token, self.grdm_url, self.project_id, self.remote_path)
        except (FileNotFoundError, json.JSONDecodeError):
            govsheet = None
        except UnauthorizedError:
            self.display_input_box()
            message = msg_config.get('main_menu', 're_enter_token')
            self.research_flow_message.update_warning(message)
            self.log.warning(f'{message}\n{traceback.format_exc()}')
            return
        except RequestException as e:
            self.research_flow_widget_box.clear()
            message = msg_config.get('dg_web', 'get_data_error')
            self.research_flow_message.update_error(f'{message}\n{str(e)}')
            self.log.error(f'{message}\n{traceback.format_exc()}')
            return
        except Exception as e:
            self.research_flow_widget_box.clear()
            message = msg_config.get('dg_web', 'get_data_error')
            self.research_flow_message.update_error(message)
            self.log.error(f'{message}\n{traceback.format_exc()}')
            return

        if not govsheet:
            self.research_flow_widget_box.clear()
            self.apply_button.set_looks_init(msg_config.get('main_menu', 'apply'))
            self.cancel_button.set_looks_init(msg_config.get('main_menu', 'cancel'))
            self.float_panel.visible = True
            self.research_flow_widget_box.append(self.float_panel)
            return

        # ガバナンスシートにカスタムガバナンスシートをマージする
        custom_govsheet = utils.get_custom_govsheet(self.abs_root)
        merge_govsheet = utils.get_merge_govsheet(govsheet, custom_govsheet)

        if govsheet_rf == merge_govsheet:
            self.update_research_flow_widget_box_init()
            message = msg_config.get('main_menu', 'current_version_govsheet')
            self.research_flow_message.update_info(message)
            return

        if not self.research_flow_dict:
            if govsheet_rf:
                utils.backup_govsheet_rf_file(self.abs_root, self.govsheet_rf_path, current_time)
            file.JsonFile(self.govsheet_rf_path).write(merge_govsheet)
        else:
            utils.recreate_subflow(
                self.abs_root, self.govsheet_rf_path, govsheet_rf, merge_govsheet, self.research_flow_dict, mapping_file)

        # GRDMと同期
        self.research_flow_widget_box.clear()
        self.research_flow_message.update_info(msg_config.get('save', 'doing'))
        try:
            sync_path_list = utils.get_sync_path(self.abs_root)
            for sync_path in sync_path_list:
                await self.grdm.sync(self.token, self.grdm_url, self.project_id, sync_path, self.abs_root)
        except UnauthorizedError:
            message = msg_config.get('form', 'token_unauthorized')
            self.research_flow_message.update_warning(message)
            self.log.warning(f'{message}\n{traceback.format_exc()}')
            return
        except RequestException as e:
            message = msg_config.get('DEFAULT', 'connection_error')
            self.research_flow_message.update_error(f'{message}\n{str(e)}')
            self.log.error(f'{message}\n{traceback.format_exc()}')
            return
        except Exception:
            message = f'## [INTERNAL ERROR] : {traceback.format_exc()}'
            self.research_flow_message.update_error(message)
            self.log.error(message)
            return
        self.update_research_flow_widget_box_init()
        self.research_flow_message.update_success(msg_config.get('main_menu', 'success_govsheet'))

    async def _handle_default_click(self, event):
        """非同期処理の実行のための仲介メソッドです"""
        await self.callback_apply_button(event)

    @TaskLog.callback_form('デフォルトでガバナンスシートを作成する')
    async def callback_apply_button(self, event):
        """デフォルトのガバナンスシートで登録するメソッドです。

        Args:
            event: ボタンクリックイベント
        """
        self.research_flow_message.clear()
        self.apply_button.set_looks_processing()
        govsheet_rf = utils.get_govsheet_rf(self.abs_root)
        mapping_file = utils.get_mapping_file(self.abs_root)

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
            self.research_flow_message.update_warning(message)
            self.log.warning(f'{message}\n{traceback.format_exc()}')
            return
        except RequestException as e:
            self.update_research_flow_widget_box_init()
            message = msg_config.get('DEFAULT', 'connection_error')
            self.research_flow_message.update_error(f'{message}\n{str(e)}')
            self.log.error(f'{message}\n{traceback.format_exc()}')
            return
        except Exception:
            message = f'## [INTERNAL ERROR] : {traceback.format_exc()}'
            self.research_flow_message.update_error(message)
            self.log.error(message)
            return
        finally:
            govsheet_file.remove(missing_ok=True)

        # ガバナンスシートにカスタムガバナンスシートをマージする
        custom_govsheet = utils.get_custom_govsheet(self.abs_root)
        merge_govsheet = utils.get_merge_govsheet(data, custom_govsheet)

        # サブフローを作り直す
        utils.recreate_subflow(
            self.abs_root, self.govsheet_rf_path, govsheet_rf, merge_govsheet, self.research_flow_dict, mapping_file)

        # GRDMと同期
        self.float_panel.visible = False
        self.research_flow_message.update_info(msg_config.get('save', 'doing'))
        try:
            sync_path_list = utils.get_sync_path(self.abs_root)
            for sync_path in sync_path_list:
                await self.grdm.sync(self.token, self.grdm_url, self.project_id, sync_path, self.abs_root)
        except UnauthorizedError:
            message = msg_config.get('form', 'token_unauthorized')
            self.research_flow_message.update_warning(message)
            self.log.warning(f'{message}\n{traceback.format_exc()}')
            return
        except RequestException as e:
            message = msg_config.get('DEFAULT', 'connection_error')
            self.research_flow_message.update_error(f'{message}\n{str(e)}')
            self.log.error(f'{message}\n{traceback.format_exc()}')
            return
        except Exception:
            message = f'## [INTERNAL ERROR] : {traceback.format_exc()}'
            self.research_flow_message.update_error(message)
            self.log.error(message)
            return
        self.update_research_flow_widget_box_init()
        self.research_flow_message.update_success(msg_config.get('main_menu', 'success_govsheet'))

    def callback_cancel_button(self, event):
        """適用しないを押した後エラーメッセージを表示するメソッドです。

        Args:
            event: ボタンクリックイベント
        """
        self.research_flow_message.clear()
        self.cancel_button.set_looks_processing()
        self.float_panel.visible = False
        msg = msg_config.get('main_menu', 'create_task_govsheet')
        self.research_flow_message.update_warning(msg)

    #################
    # クラスメソッド #
    #################

    @classmethod
    def generate(cls, working_path: str):
        """メインメニューを生成するメソッドです。

        Args:
            working_path(str) : Notebookのファイルのパス
        """
        # panel activation
        pn.extension()
        # Get initial setup complete status
        # ~/.data-governance/setup_completed.txt, if present, complete, if not, not complete
        # TODO:再調整要
        # https://github.com/NII-DG/dg-researchflowsのデータが配置されているディレクトリ
        # Jupyter環境では/home/jovyan
        # abs_root = path_config.get_abs_root_form_working_dg_file_path(working_path)
        # 初期セットアップ完了フラグファイルパス
        # abs_setup_completed_file_path = os.path.join(abs_root, path_config.SETUP_COMPLETED_TEXT_PATH)

        # Hidden Setup
        # if os.path.isfile(abs_setup_completed_file_path):

        # Initial setup is complete.
        # Display the main menu
        main_menu = MainMenu(working_path)
        # log
        main_menu.log.start()
        # initialize vault
        vault = Vault()
        vault.initialize()

        # 機能コントローラーを配置
        main_menu_title = 'メインメニュー'
        main_menu_box = pn.WidgetBox(
            f'## {main_menu_title}',
            main_menu._menu_tabs, main_menu._err_output
        )
        display(main_menu_box)
        research_flow_image_title = pn.pane.Markdown(
            f'### {msg_config.get("main_menu", "subflow_relationship_diagram")}'
        )
        research_flow_box = pn.WidgetBox(
            research_flow_image_title,
            main_menu.research_flow_widget_box,
            main_menu.research_flow_message
        )
        display(research_flow_box)
        display(main_menu._research_flow_image)

        # Hidden Setup
        # else:
        # Initial setup is incomplete.
        # Leads you to the initial setup

        # display message
        #    alert = pn.pane.Alert(msg_config.get('main_menu', 'required_initial_setup'),sizing_mode="stretch_width",alert_type='warning')
        # display initial setup link button
        #    initial_setup_link_button = pn.pane.HTML()
        #    initial_setup_link_button.object = html_button.create_button(
        #        url = './setup.ipynb?init_nb=true',
        #        msg=msg_config.get('main_menu', 'access_initial_setup'),
        #        button_width='500px'
        #    )
        #    initial_setup_link_button.width = 500
        #    display(alert)
        #    display(initial_setup_link_button)

        main_menu.log.finish()
        display(Javascript('IPython.notebook.save_checkpoint();'))