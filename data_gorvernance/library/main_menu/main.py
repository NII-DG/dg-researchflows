"""メインメニュー画面での操作のモジュールです。

このモジュールはメインメニューの画面やボタンを表示するメソッドやサブフローメニューの画面の表示、操作を行えるメソッドなどがあります。
"""
import os
import traceback
import datetime
import json

from IPython.core.display import Javascript
from IPython.display import display
import panel as pn

from library.utils.config import path_config, message as msg_config, connect as con_config
from library.utils.error import InputWarning
from library.utils.html import button as html_button
from library.utils import file
from library.utils.log import TaskLog
from library.utils.setting import ResearchFlowStatusOperater, SubflowStatusFile
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
            callback_type(str):呼び出すメソッドのタイプ
            subflow_form(CreateSubflowForm | RelinkSubflowForm | RenameSubflowForm | DeleteSubflowForm):サブフローのフォーム

    NOTE:
    Called from data_gorvernance/researchflow/main.ipynb
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
        # data_gorvernance\researchflow\research_flow_status.json
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
        # ファイル：data_gorvernance\researchflow\plan\status.json
        # 必須タスクが全て1回以上実行完了していない場合、研究準備サブフローへ誘導する。
        # サブフロー操作コントローラーを無効化する。
        # 必須タスクが完了している場合は、何もしない
        self.check_status_research_preparation_flow()

        self.grdm_url = con_config.get('GRDM', 'BASE_URL')
        self.remote_path = con_config.get('DG_WEB', 'GOVSHEET_PATH')

        pn.extension('floatpanel')

        self.research_flow_widget_box = pn.WidgetBox()
        self.research_flow_widget_box.width = 900

        # パーソナルアクセストークンとプロジェクトID入力欄
        self.token_input, self.project_id_input = utils.input_widget()
        self.token_input.param.watch(self.input, 'value')
        self.project_id_input.param.watch(self.input, 'value')

        # ガバナンスシート適用ボタン
        apply_govsheet_button_title = msg_config.get('main_menu', 'apply_gov_sheet')
        self.apply_gov_sheet_button = Button(width=10)
        self.apply_gov_sheet_button.set_looks_init(apply_govsheet_button_title)
        self.apply_gov_sheet_button.on_click(self.apply_click)

        self.update_research_flow_widget_box_init()

        self.field_box = pn.WidgetBox()
        self.field_box.width = 900

        self.research_flow_message = MessageBox()
        self.research_flow_message.width = 900

        self.input_button = Button(width=10, visible=False, disabled=True)
        self.input_button.set_looks_init()
        self.input_button.on_click(self.callback_input_button)

        self.govsheet_rf_path = utils.get_govsheet_rf_path(self.abs_root)
        self.current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    def is_govsheet(self):
        """RFガバナンスシートやガバナンスシートの存在で処理を変えるためのメソッドです。

        Args:
            token (str): パーソナルアクセストークン
            project_id (str): プロジェクトID
        """
        govsheet_rf = utils.get_govsheet_rf(self.abs_root)
        govsheet = utils.get_govsheet(self.token, self.grdm_url, self.project_id, self.remote_path)
        if govsheet:
            if govsheet_rf == govsheet:
                self.token_input.visible = False
                self.project_id_input.visible = False
                message = msg_config.get('main_menu', 'current_version_govsheet')
                self.research_flow_message.update_info(message)
                self.field_box.append(self.research_flow_message)
            else:
                self.backup_file()
        else:
            utils.display_float_panel(self.abs_root, self.field_box, self.research_flow_message, self.token, self.project_id)

    def backup_file(self):
        govsheet_rf = utils.get_govsheet_rf(self.abs_root)
        govsheet = utils.get_govsheet(self.token, self.grdm_url, self.project_id, self.remote_path)
        research_flow_dict = self.reserch_flow_status_operater.get_phase_subflow_id_name()
        if govsheet_rf:
            self.backup_gov_sheet_rf_file()
            utils.copy_govsheet(self.govsheet_rf_path, govsheet)
        utils.backup_zipfile(self.abs_root, research_flow_dict, self.current_time)
        file_dir = os.path.dirname(self.govsheet_rf_path)
        if os.path.exists(file_dir):
            os.makedirs(file_dir)
        file.JsonFile(self.govsheet_rf_path).write(govsheet)
        self.remove_and_copy_file_notebook()

    def remove_and_copy_file_notebook(self):
        """サブフローの設定ファイル群とタスクノートブックを削除しbaseからコピーするメソッドです。"""
        research_flow_dict = self.reserch_flow_status_operater.get_phase_subflow_id_name()
        if research_flow_dict:
            for phase_name, sub_flow_data in research_flow_dict.items():
                for sub_flow_id, sub_flow_name in sub_flow_data.items():
                    menu_notebook_path, status_json_path = utils.get_options_path(self.abs_root, phase_name, sub_flow_id, sub_flow_name)
                    working_path = utils.get_working_path(self.abs_root, phase_name, sub_flow_id, sub_flow_name)
                    self.remove_file(working_path)
                    file.File(str(menu_notebook_path)).remove()
                    file.File(str(status_json_path)).remove()
                    CreateSubflowForm.prepare_new_subflow_data(self, phase_name, sub_flow_id, sub_flow_name, True)
                    utils.update_status_file(self.abs_root, status_json_path, working_path)
        else:
            msg = msg_config.get('main_menu', 'success_govsheet')
            self.research_flow_message.update_success(msg)
            self.field_box.append(self.research_flow_message)

    def remove_file(self, drc_path: str):
        """フォルダ内のファイルを全て削除するメソッドです。

        Args:
            drc_path (str): 対象のディレクトリのパス
        """
        if not os.path.isdir(drc_path):
            pass
        for root, dirs, files in os.walk(drc_path):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)

    def backup_gov_sheet_rf_file(self):
        """RFガバナンスシートのバックアップを行うメソッドです。"""
        backup_file_path = os.path.join(
            self.abs_root,
            path_config.DATA_GOVERNANCE,
            path_config.LOG,
            'gov-sheet-rf',
            f'{self.current_time}.json'
        )
        file.copy_file(self.govsheet_rf_path, backup_file_path)

    def check_status_research_preparation_flow(self):
        """研究準備の実行ステータス確認をするメソッドです。"""
        sf = SubflowStatusFile(os.path.join(self.abs_root, path_config.PLAN_TASK_STATUS_FILE_PATH))
        plan_sub_flow_status = sf.read()
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
                self.subflow_form = CreateSubflowForm(self.abs_root, self._sub_flow_widget_box, self._err_output)
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

    def input(self, event):
        """パーソナルアクセストークンとプロジェクトIDが正しい形式で記入されているか確認するメソッドです。

        Args:
            event: 入力イベント
        """
        if self.token_input.visible and self.project_id_input.visible:
            token_value = utils.check_input(self.token_input.value_input)
            project_id_value = utils.check_input(self.project_id_input.value_input)
            if token_value and project_id_value:
                self.input_button.visible = True
            elif token_value:
                self.project_id_input.value = ''
                self.input_button.visible = False
            else:
                self.token_input.value = ''
                self.input_button.visible = False
        elif self.token_input.visible:
            token_value = utils.check_input(self.token_input.value_input)
            if token_value:
                self.input_button.visible = True
            else:
                self.token_input.value = ''
                self.input_button.visible = False
        else:
            project_id_value = utils.check_input(self.project_id_input.value_input)
            if project_id_value:
                self.input_button.visible = True
            else:
                self.project_id_input.value = ''
                self.input_button.visible = False

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

    def callback_submit_button(self, event):
        """サブフローのボタンを呼び戻すメソッドです。"""
        try:
            # start
            self.log.start(detail=self.callback_type)
            self.subflow_form.main()

            # サブフロー関係図を更新
            self._research_flow_image.object = self.reserch_flow_status_operater.get_svg_of_research_flow_status()
            display(Javascript('IPython.notebook.save_checkpoint();'))
            # end
            self.log.finish(detail=self.callback_type)
        except InputWarning:
            self.log.warning(traceback.format_exc())
        except Exception:
            message = f'## [INTERNAL ERROR] : {traceback.format_exc()}'
            self.log.error(message)
            self._err_output.update_error(message)

    def update_research_flow_widget_box_init(self):
        """リサーチフロー関係図とガバナンスシート適用ボタンを表示するメソッドです。"""
        self.research_flow_widget_box.clear()
        research_flow_image_title = f'### {msg_config.get("main_menu", "subflow_relationship_diagram")}'
        layout = pn.Row(
            research_flow_image_title,
            pn.Spacer(width=580),
            self.apply_gov_sheet_button
        )
        self.research_flow_widget_box.append(layout)

    def update_field_box(self):
        """パーソナルアクセストークンとプロジェクトIDと確定ボタンを表示するメソッドです。"""
        self.field_box.clear()
        input_layout = pn.Row(
            self.token_input,
            self.project_id_input,
            self.input_button
        )
        self.field_box.append(input_layout)

    def apply_click(self, event):
        """ガバナンスシート適用ボタン押下後の表示を変えるメソッドです。

        Args:
            event: ボタンクリックイベント
        """
        self.input_button.set_looks_init()
        self.research_flow_message.clear()
        self.field_box.clear()
        self.token_input.value = ''
        self.project_id_input.value = ''
        self.token = utils.get_token()
        self.project_id = utils.get_project_id()
        if self.project_id is None and self.token is None:
            self.project_id_input.visible = True
            self.token_input.visible = True
        elif self.token is None:
            self.token_input.visible = True
        else:
            self.project_id_input.visible = False
            self.token_input.visible = False
            self.is_govsheet(token, project_id)
        self.update_field_box()

    def callback_input_button(self, event):
        """入力内容のチェックをするメソッドです。

        Args:
            event: クリックイベント
        """
        self.input_button.set_looks_processing()
        try:
            vault = Vault()
            token = self.token_input.value if self.token_input.visible else None
            project_id = self.project_id_input.value if self.project_id_input.visible else None
            if token and project_id:
                if not utils.grdm_access_check(self.grdm_url, token, project_id):
                    vault.set_value('grdm_token', '')
                    self.token_input.value = ''
                    self.project_id_input.value = ''
                else:
                    self.field_box.clear()
                    self.token = token
                    self.project_id = project_id
                    self.is_govsheet()
            elif token:
                if not utils.grdm_access_check(self.grdm_url, token, self.project_id):
                    vault.set_value('grdm_token', '')
                    self.token_input.value = ''
                else:
                    self.field_box.clear()
                    self.token = token
                    self.is_govsheet()
            else:
                if not utils.grdm_access_check(self.grdm_url, self.token, project_id):
                    self.project_id_input.value = ''
                else:
                    self.field_box.clear()
                    self.project_id = project_id
                    self.is_govsheet()
        except Exception:
            message = f'## [INTERNAL ERROR] : {traceback.format_exc()}'
            self._err_output.update_error(message)
            self.log.error(message)


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
        main_menu.research_flow_widget_box.append(main_menu.field_box)
        display(main_menu.research_flow_widget_box)
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
