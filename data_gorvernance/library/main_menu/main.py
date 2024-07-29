"""メインメニュー画面での操作
    このモジュールはメインメニューの画面やボタンを表示する関数やサブフローメニューの画面の表示、操作を行える関数などがあります。
"""
import os
import traceback

import panel as pn
from IPython.display import display
from IPython.core.display import Javascript

from ..utils.setting import ResearchFlowStatusOperater, SubflowStatusFile
from ..utils.config import path_config, message as msg_config
from ..utils.html import button as html_button
from ..utils.log import TaskLog
from ..utils.widgets import MessageBox
from .subflow_controller import (
    CreateSubflowForm,
    RelinkSubflowForm,
    RenameSubflowForm,
    DeleteSubflowForm
)
from ..utils.vault import Vault
from ..utils.error import InputWarning


# git clone https://github.com/NII-DG/dg-researchflows.git -b feature/main_menu_v2 ./demo
# mv ./demo/* ./
# rm -rf ./demo

class MainMenu(TaskLog):
    """メインメニューのクラスです。

        MainMenuクラスはTaskLogを継承したクラスです。

    FUNCTION:

    1. Display the Research Flow Main Menu
    2. View Research Flow Image
    3. When the initial setup has not been performed, the user is guided to the initial setup.

    Attributes:
        abs_root: リサーチフロー図の絶対パス
        _research_flow_status_file_path: リサーチフロー図の生成
        _research_flow_image: リサーチフロー図オブジェクトの定義
        _err_output:エラーの出力
        _menu_tabs:メニュータブ
        _project_menu:プロジェクトメニュー
        _project_widget_box:サブフロー操作コントローラーウェジットボックス
        _sub_flow_menu:サブフローメニュー
        _sub_flow_widget_box:サブフロー操作コントローラーウェジットボックス





    NOTE:

    Called from data_gorvernance/researchflow/main.ipynb
    """

    def __init__(self, working_file) -> None:
        """MainMenu　コンストラクタの関数です
            親クラスの__init__メソッドを呼び出す関数です。
            Args:
                working_file:[実行Notebookファイルパス]
        
        """
        super().__init__(working_file, 'main.ipynb')
       

        ##############################
        # リサーチフロー図オブジェクト #
        ##############################
        self.abs_root = path_config.get_abs_root_form_working_dg_file_path(working_file)
        # リサーチフロー図の生成
        ## data_gorvernance\researchflow\research_flow_status.json
        self._research_flow_status_file_path = path_config.get_research_flow_status_file_path(self.abs_root)

        self.reserch_flow_status_operater = ResearchFlowStatusOperater(self._research_flow_status_file_path)
        # プロジェクトで初回のリサーチフロー図アクセス時の初期化
        self.reserch_flow_status_operater.init_research_preparation(self._research_flow_status_file_path)
        ## リサーチフロー図オブジェクトの定義
        self._research_flow_image = pn.pane.HTML(self.reserch_flow_status_operater.get_svg_of_research_flow_status())
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

        ## プロジェクト操作コントローラーの定義
        ### 遷移ボタン for プロジェクト操作コントローラー
        self.button_for_project_menu = pn.pane.HTML()
        self.button_for_project_menu.object = html_button.create_button(msg=msg_config.get('main_menu', 'disable_jump_button'), disable=True, border=['dashed', '1px'],button_background_color='#ffffff')

        ### プロジェクト操作アクションセレクタ―
        project_menu_title = msg_config.get('main_menu', 'project_menu_title')
        project_menu_options = dict()
        project_menu_options[msg_config.get('form', 'selector_default')] = 0
        project_menu_options[msg_config.get('main_menu', 'edit_governance_sheet_title')] = 1
        project_menu_options[msg_config.get('main_menu', 'verification_results_title')] = 2
        project_menu_options[msg_config.get('main_menu', 'monitoring_settings_title')] = 3
        project_menu_options[msg_config.get('main_menu', 'update_dmp_title')] = 4
        project_menu_options[msg_config.get('main_menu', 'finish_research_title')] = 5
        self._project_menu = pn.widgets.Select(options=project_menu_options, value=0)

        ## プロジェクト操作アクションセレクタ―のイベントリスナー
        self._project_menu.param.watch(self.callback_project_menu,'value')

        ## サブフロー操作コントローラーウェジットボックス（後からなんでもいれる事ができます）
        self._project_widget_box = pn.WidgetBox()
        self._project_widget_box.width = 900

        ## サブフロー操作コントローラーの定義
        ### サブフロー操作コントローラーオプション
        sub_flow_menu_title = msg_config.get('main_menu', 'sub_flow_menu_title')
        sub_flow_menu_options = dict()
        sub_flow_menu_options[msg_config.get('form','selector_default')] = 0
        sub_flow_menu_options[msg_config.get('main_menu','create_sub_flow_title')] = 1
        sub_flow_menu_options[msg_config.get('main_menu','update_sub_flow_link_title')] = 2
        sub_flow_menu_options[msg_config.get('main_menu','update_sub_flow_name_title')] = 3
        sub_flow_menu_options[msg_config.get('main_menu','delete_sub_flow_title')] = 4
        ## サブフロー操作コントローラー
        self._sub_flow_menu = pn.widgets.Select(options=sub_flow_menu_options, value=0)
        ## サブフロー操作コントローラーのイベントリスナー
        self._sub_flow_menu.param.watch(self.callback_sub_flow_menu,'value')
        ## サブフロー操作コントローラーウェジットボックス（後からなんでもいれる事ができます）
        self._sub_flow_widget_box = pn.WidgetBox()
        self._sub_flow_widget_box.width = 900
        self.update_sub_flow_widget_box_for_init()

        sub_flow_menu_layout = pn.Column(self._sub_flow_menu, self._sub_flow_widget_box)
        project_menu_layout = pn.Column(pn.Row(self._project_menu, self.button_for_project_menu), self._project_widget_box)

        self._menu_tabs.append((sub_flow_menu_title, sub_flow_menu_layout)) # tab_index = 0
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

    def check_status_research_preparation_flow(self):
        """研究準備の実行ステータス確認をする関数です。
        """
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
            alert = pn.pane.Alert(msg_config.get('main_menu','required_research_preparation'),sizing_mode="stretch_width",alert_type='warning')
            self._sub_flow_widget_box.clear()
            self._sub_flow_widget_box.append(alert)


    ######################################
    # イベントリスナーコールバックメソッド #
    ######################################

    def callback_menu_tabs(self, event):
        """サブフロー操作で選択ができるようにする関数です。

        Args:
            event (_type_): 機能コントローラーのイベントリスナー

        Raises:
            Exception:内部エラー

        """
        try:
            self._err_output.clear()
            tab_index = event.new
            if tab_index == 0:
                # サブフロー操作が選択
                ## サブフロー操作コントローラーオプションを初期化
                self._sub_flow_menu.value = 0
                self._project_widget_box.clear()
                self.check_status_research_preparation_flow()
            if tab_index == 1:
                # プロジェクト操作が選択
                self._project_menu.value = 0
                self._sub_flow_widget_box.clear()
        except Exception as e:
            self._err_output.update_error(f'## [INTERNAL ERROR] : {traceback.format_exc()}')

    def callback_project_menu(self, event):
        """プロジェクト操作コントローラーの更新をするための遷移ボタンの関数です。
        
        Raises:
            Exception:内部エラー
        
        """
        # 開発中のためアラートを表示する。
        try:
            self._err_output.clear()
            self._project_widget_box.clear()
            alert = pn.pane.Alert(msg_config.get('DEFAULT','developing'),sizing_mode="stretch_width",alert_type='warning')
            self._project_widget_box.append(alert)
        except Exception as e:
            self._err_output.update_error(f'## [INTERNAL ERROR] : {traceback.format_exc()}')

    def callback_sub_flow_menu(self, event):
        """サブフロー操作コントローラーオプションによるサブフロー操作フォームを表示する関数です。

        Raises:
            Exception:内部エラー
        
        """
        try:
            self._err_output.clear()
            selected_value = self._sub_flow_menu.value
            if selected_value == 0: ## 選択なし
                self.update_sub_flow_widget_box_for_init()
                return
            elif selected_value == 1: ## サブフロー新規作成
                self.callback_type = "create"
                self.subflow_form = CreateSubflowForm(self.abs_root, self._err_output)
            elif selected_value == 2: ## サブフロー間接続編集
                self.callback_type = "relink"
                self.subflow_form = RelinkSubflowForm(self.abs_root, self._err_output)
            elif selected_value == 3: ## サブフロー名称変更
                self.callback_type = "rename"
                self.subflow_form = RenameSubflowForm(self.abs_root, self._err_output)
            elif selected_value == 4: ## サブフロー削除
                self.callback_type = "delete"
                self.subflow_form = DeleteSubflowForm(self.abs_root, self._err_output)
            self.update_sub_flow_widget_box()
        except Exception as e:
            self._err_output.update_error(f'## [INTERNAL ERROR] : {traceback.format_exc()}')


    #########################
    # サブフロー操作フォーム #
    #########################

    def update_sub_flow_widget_box_for_init(self):
        """サブフロー操作オプションの選択誘導する関数です。"""
        self._sub_flow_widget_box.clear()
        alert = pn.pane.Alert(msg_config.get('main_menu','guide_select_action'),sizing_mode="stretch_width",alert_type='info')
        self._sub_flow_widget_box.append(alert)

    def update_sub_flow_widget_box(self):
        """サブフロー操作フォームの表示する関数です。"""
        # ボタンのイベントリスナー
        self.subflow_form.set_submit_button_on_click(self.callback_submit_button)

        sub_flow_form_layout = self.subflow_form.define_input_form()
        self._sub_flow_widget_box.clear()
        self._sub_flow_widget_box.append(sub_flow_form_layout)
        # ボタンの無効化をする（最初の設定が反映されないため）
        self.subflow_form.submit_button.disabled=True

    def callback_submit_button(self, event):
        """サブフローのボタンを呼び戻す関数です。

        Raises:
            InputWarning:入力値が間違っているエラー
            Exception:内部エラー
        """
        try:
            # start
            self.log.start(detail=self.callback_type)
            self.subflow_form.main()

            # サブフロー関係図を更新
            self._research_flow_image.object = self.reserch_flow_status_operater.get_svg_of_research_flow_status()
            display(Javascript('IPython.notebook.save_checkpoint();'))
            # end
            self.log.finish(detail=self.callback_type)
        except InputWarning as e:
            self.log.warning(str(e))
        except  Exception:
            message = f'## [INTERNAL ERROR] : {traceback.format_exc()}'
            self.log.error(message)
            self._err_output.update_error(message)

    #################
    # クラスメソッド #
    #################

    @classmethod
    def generate(cls, working_path:str):
        """メインメニューを生成する関数です。

        working_path : Notebookのファイルの位置
        """
        # panel activation
        pn.extension()
        # Get initial setup complete status
        ## ~/.data-governance/setup_completed.txt, if present, complete, if not, not complete
        ## TODO:再調整要
        # https://github.com/NII-DG/dg-researchflowsのデータが配置されているディレクトリ
        # Jupyter環境では/home/jovyan
        #abs_root = path_config.get_abs_root_form_working_dg_file_path(working_path)
        # 初期セットアップ完了フラグファイルパス
        #abs_setup_completed_file_path = os.path.join(abs_root, path_config.SETUP_COMPLETED_TEXT_PATH)

        # Hidden Setup
        #if os.path.isfile(abs_setup_completed_file_path):

        # Initial setup is complete.
        # Display the main menu
        main_menu = MainMenu(working_path)
        # log
        main_menu.log.start()
        # initialize vault
        vault = Vault()
        vault.initialize()

        ## 機能コントローラーを配置
        main_menu_title = 'メインメニュー'
        main_menu_box = pn.WidgetBox(f'## {main_menu_title}', main_menu._menu_tabs, main_menu._err_output)
        display(main_menu_box)
        ## リサーチフロー図を配置
        research_flow_image_title = pn.pane.Markdown(f'### {msg_config.get("main_menu", "subflow_relationship_diagram")}')
        display(research_flow_image_title)
        display(main_menu._research_flow_image)

        # Hidden Setup
        #else:
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
