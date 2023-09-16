from typing import Dict, List
from ..utils.config import path_config, message as msg_config
from ..utils.html import text as html_text, button as html_button
from IPython.display import display, Javascript
from dg_drawer.research_flow import ResearchFlowStatus, PhaseStatus
from ..main_menu.research_flow_status import ResearchFlowStatusOperater as re_fl_operater
import traceback

import panel as pn
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir_path = os.path.abspath(os.path.join(script_dir, '../'))

# git clone https://github.com/NII-DG/dg-researchflows.git -b feature/main_menu_v2 ./demo
# mv ./demo/* ./
# rm -rf ./demo

class MainMenu():
    """MainMenu Class

    FUNCTION:

    1. Display the Research Flow Main Menu
    2. View Research Flow Image
    3. When the initial setup has not been performed, the user is guided to the initial setup.

    NOTE:

    Called from data_gorvernance/researchflow/main.ipynb
    """

    def __init__(self, abs_root) -> None:

        ##############################
        # リサーチフロー図オブジェクト #
        ##############################

        # リサーチフロー図の生成
        ## data_gorvernance\researchflow\main_menu\status\research_flow_status.json
        self._research_flow_status_file_path = path_config.getResearchFlowStatusFilePath(abs_root)

        # プロジェクトで初回のリサーチフロー図アクセス時の初期化
        re_fl_operater.init_research_preparation(self._research_flow_status_file_path)
        ## リサーチフロー図オブジェクトの定義
        self._research_flow_image = pn.pane.HTML(re_fl_operater.get_svg_of_research_flow_status(self._research_flow_status_file_path))
        self._research_flow_image.width = 1000

        ######################################
        # システムエラーメッセージオブジェクト #
        ######################################

        # システムエラーメッセージオブジェクトの定義
        self._err_output = pn.WidgetBox()
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
        self._menu_tabs.append((project_menu_title, project_menu_layout)) # tab_index = 1
        # 機能コントローラーのイベントリスナー
        self._menu_tabs.param.watch(self.callback_menu_tabs, 'active')



    def check_status_research_preparation_flow(self):
        # 研究準備サブフローの進行状況をチェックする。

        # 必須タスクが全て完了している場合、何もしない。

        # 未完了必須タスクがある場合、以下の処理をする。
        # サブフロー操作コントローラーを無効化
        self._sub_flow_menu.disabled = True
        # プロジェクト操作コントローラーを無効化
        self._project_menu.disabled = True
        # アラートを表示する。
        alert = pn.pane.Alert(msg_config.get('main_menu','required_research_preparation'),sizing_mode="stretch_width",alert_type='warning')
        self._sub_flow_widget_box.append(alert)



    ######################################
    # イベントリスナーコールバックメソッド #
    ######################################

    def callback_menu_tabs(self, event):
        try:
            tab_index = event.new
            if tab_index == 0:
                # サブフロー操作が選択
                ## サブフロー操作コントローラーオプションを初期化
                self._sub_flow_menu.value = 0
                self._project_widget_box.clear()
            if tab_index == 1:
                # プロジェクト操作が選択
                self._project_menu.value = 0
                self._sub_flow_widget_box.clear()
        except Exception as e:
            self._err_output.clear()
            alert = pn.pane.Alert(f'## [INTERNAL ERROR] : {traceback.format_exc()}',sizing_mode="stretch_width",alert_type='danger')
            self._err_output.append(alert)



    def callback_project_menu(self, event):
        """遷移ボタン for プロジェクト操作コントローラーの更新"""
        # 開発中のためアラートを表示する。
        try:
            self._project_widget_box.clear()
            alert = pn.pane.Alert(msg_config.get('DEFAULT','developing'),sizing_mode="stretch_width",alert_type='warning')
            self._project_widget_box.append(alert)
        except Exception as e:
            self._err_output.clear()
            alert = pn.pane.Alert(f'## [INTERNAL ERROR] : {traceback.format_exc()}',sizing_mode="stretch_width",alert_type='danger')
            self._err_output.append(alert)

    def callback_sub_flow_menu(self, event):
        """サブフロー操作フォーム by サブフロー操作コントローラーオプション"""
        try:
            selected_value = self._sub_flow_menu.value
            if selected_value == 0: ## 選択なし
                self.update_sub_flow_widget_box_for_init()
            elif selected_value == 1: ## サブフロー新規作成
                self.update_sub_flow_widget_box_for_new_sub_flow()
            elif selected_value == 2: ## サブフロー間接続編集
                self.update_sub_flow_widget_box_for_relink()
            elif selected_value == 3: ## サブフロー名称変更
                self.update_sub_flow_widget_box_for_rename()
            elif selected_value == 4: ## サブフロー削除
                self.update_sub_flow_widget_box_for_delete()
        except Exception as e:
            self._err_output.clear()
            alert = pn.pane.Alert(f'## [INTERNAL ERROR] : {traceback.format_exc()}',sizing_mode="stretch_width",alert_type='danger')
            self._err_output.append(alert)



    #########################
    # サブフロー操作フォーム #
    #########################

    def update_sub_flow_widget_box_for_init(self):
        """サブフロー操作オプションの選択誘導"""
        self._sub_flow_widget_box.clear()
        alert = pn.pane.Alert(msg_config.get('main_menu','guide_select_action'),sizing_mode="stretch_width",alert_type='info')
        self._sub_flow_widget_box.append(alert)

    #########################
    # サブフロー新規作成フォーム #
    #########################



    def update_sub_flow_widget_box_for_new_sub_flow(self):
        ### サブフロー新規作成フォーム
        # リサーチフローステータス管理情報の取得
        research_flow_status = ResearchFlowStatus.load_from_json(self._research_flow_status_file_path)

        # サブフロー種別(フェーズ)オプション
        sub_flow_type_options = self.generate_sub_flow_type_options(research_flow_status)
        # サブフロー種別(フェーズ):シングルセレクト
        self._sub_flow_type_selector = pn.widgets.Select(
            name=msg_config.get('main_menu', 'sub_flow_type'),
            options=sub_flow_type_options,
            value=sub_flow_type_options[msg_config.get('form', 'selector_default')]
            )
        # サブフロー種別(フェーズ)のイベントリスナー
        self._sub_flow_type_selector.param.watch(self.callback_sub_flow_type_selector, 'value')

        # サブフロー名称（必須）：テキストフォーム
        self._sub_flow_name_form = pn.widgets.TextInput(
            name=msg_config.get('main_menu', 'sub_flow_name'),
            placeholder='Enter a sub flow name here…', max_length=15)
        # サブフロー名称（必須）：テキストフォームのイベントリスナー
        self._sub_flow_name_form.param.watch(self.callback_sub_flow_name_form, 'value')

        # 親サブフロー種別(フェーズ)オプション
        parent_sub_flow_type_options = self.generate_parent_sub_flow_type_options(sub_flow_type_options[msg_config.get('form', 'selector_default')], research_flow_status)
        # 親サブフロー種別(フェーズ)（必須)：シングルセレクト
        self._parent_sub_flow_type_selector = pn.widgets.Select(
            name=msg_config.get('main_menu', 'parent_sub_flow_type'),
            options=parent_sub_flow_type_options,
            value=parent_sub_flow_type_options[msg_config.get('form', 'selector_default')],
            )
        # 親サブフロー種別(フェーズ)のイベントリスナー
        self._parent_sub_flow_type_selector.param.watch(self.callback_parent_sub_flow_type_selector, 'value')

        # 親サブフロー選択オプション
        parent_sub_flow_options = self.generate_parent_sub_flow_options(parent_sub_flow_type_options[msg_config.get('form', 'selector_default')], research_flow_status)
        # 親サブフロー選択 : マルチセレクト
        self._parent_sub_flow_selector = pn.widgets.MultiSelect(
            name=msg_config.get('main_menu', 'parent_sub_flow_name'),
            options=parent_sub_flow_options
            )
        # 親サブフロー選択のイベントリスナー
        self._parent_sub_flow_selector.param.watch(self.callback_parent_sub_flow_selector, 'value')

        # 新規作成ボタン
        self.submit_button = pn.widgets.Button(disabled=True)
        self.change_submit_button_init(msg_config.get('main_menu', 'create_sub_flow'))
        self.submit_button.width = 500
        # 新規作成ボタンのイベントリスナー
        self.submit_button.on_click(self.callback_create_new_sub_flow)

        sub_flow_form_layout = pn.Column(
            f'### {msg_config.get("main_menu", "create_sub_flow_title")}',
            self._sub_flow_type_selector,
            self._sub_flow_name_form,
            self._parent_sub_flow_type_selector,
            self._parent_sub_flow_selector,
            self.submit_button
            )
        self._sub_flow_widget_box.clear()
        self._sub_flow_widget_box.append(sub_flow_form_layout)


    def generate_sub_flow_type_options(self, research_flow_status:List[PhaseStatus])->Dict[str, int]:
        # サブフロー種別(フェーズ)オプション(表示名をKey、順序値をVauleとする)
        pahse_options = {}
        pahse_options['--'] = 0
        for phase_status in research_flow_status:
            if phase_status._seq_number == 1:
                continue
            else:
                pahse_options[msg_config.get('research_flow_phase_display_name',phase_status._name)] = phase_status._seq_number
        return pahse_options

    def generate_parent_sub_flow_type_options(self, pahase_seq_number:int, research_flow_status:List[PhaseStatus])->Dict[str, int]:
        # 親サブフロー種別(フェーズ)オプション(表示名をKey、順序値をVauleとする)
        pahse_options = {}
        pahse_options['--'] = 0
        if pahase_seq_number == 0:
            return pahse_options
        else:
            for phase_status in research_flow_status:
                if phase_status._seq_number < pahase_seq_number:
                    pahse_options[msg_config.get('research_flow_phase_display_name',phase_status._name)] = phase_status._seq_number
        return pahse_options

    def generate_parent_sub_flow_options(self, pahase_seq_number:int, research_flow_status:List[PhaseStatus])->Dict[str, str]:
        # 親サブフロー選択オプション(表示名をKey、サブフローIDをVauleとする)
        pahse_options = {}
        if pahase_seq_number == 0:
            return pahse_options
        else:
            for phase_status in research_flow_status:
                if phase_status._seq_number == pahase_seq_number:
                    for sf in phase_status._sub_flow_data:
                        pahse_options[sf._name] = sf._id
        return pahse_options

    def change_submit_button_init(self, name):
        self.submit_button.name = name
        self.submit_button.button_type = 'primary'
        self.submit_button.button_style = 'outline'
        self.submit_button.icon = 'plus'

    def change_submit_button_processing(self, name):
        self.submit_button.name = name
        self.submit_button.button_type = 'primary'
        self.submit_button.button_style = 'solid'

    def change_submit_button_success(self, name):
        self.submit_button.name = name
        self.submit_button.button_type = 'success'
        self.submit_button.button_style = 'solid'

    def change_submit_button_warning(self, name):
        self.submit_button.name = name
        self.submit_button.button_type = 'warning'
        self.submit_button.button_style = 'solid'

    def change_submit_button_error(self, name):
        self.submit_button.name = name
        self.submit_button.button_type = 'danger'
        self.submit_button.button_style = 'solid'

    def callback_create_new_sub_flow(self, event):
        # 新規作成ボタンコールバックファンクション
        # サブフロー作成処理
        try:
            self.change_submit_button_processing(msg_config.get('main_menu', 'creating_sub_flow'))
            pass
        except Exception as e:
            pass

    def callback_sub_flow_type_selector(self, event):
        # サブフロー種別(フェーズ):シングルセレクトコールバックファンクション
        try:
            # リサーチフローステータス管理情報の取得
            research_flow_status = ResearchFlowStatus.load_from_json(self._research_flow_status_file_path)

            selected_value = self._sub_flow_type_selector.value
            if selected_value is None:
                raise Exception('Sub Flow Type Selector has None')
            # 親サブフロー種別(フェーズ)（必須)：シングルセレクトの更新
            parent_sub_flow_type_options = self.generate_parent_sub_flow_type_options(selected_value, research_flow_status)
            self._parent_sub_flow_type_selector.options = parent_sub_flow_type_options
            # 新規作成ボタンのボタンの有効化チェック
            self.change_diable_creating_button()
        except Exception as e:
            self._err_output.clear()
            alert = pn.pane.Alert(f'## [INTERNAL ERROR] : {traceback.format_exc()}',sizing_mode="stretch_width",alert_type='danger')
            self._err_output.append(alert)

    def callback_sub_flow_name_form(self, event):
        # サブフロー名称（必須）：テキストフォームコールバックファンクション
        try:
            # 新規作成ボタンのボタンの有効化チェック
            self.change_diable_creating_button()
        except Exception as e:
            self._err_output.clear()
            alert = pn.pane.Alert(f'## [INTERNAL ERROR] : {traceback.format_exc()}',sizing_mode="stretch_width",alert_type='danger')
            self._err_output.append(alert)

    def callback_parent_sub_flow_type_selector(self, event):
        # 親サブフロー種別(フェーズ)のコールバックファンクション
        try:
            # リサーチフローステータス管理情報の取得
            research_flow_status = ResearchFlowStatus.load_from_json(self._research_flow_status_file_path)

            selected_value = self._parent_sub_flow_type_selector.value
            if selected_value is None:
                raise Exception('Parent Sub Flow Type Selector has None')

            parent_sub_flow_options = self.generate_parent_sub_flow_options(selected_value, research_flow_status)
            self._parent_sub_flow_selector.options = parent_sub_flow_options
            # 新規作成ボタンのボタンの有効化チェック
            self.change_diable_creating_button()
        except Exception as e:
            self._err_output.clear()
            alert = pn.pane.Alert(f'## [INTERNAL ERROR] : {traceback.format_exc()}',sizing_mode="stretch_width",alert_type='danger')
            self._err_output.append(alert)

    def callback_parent_sub_flow_selector(self, event):
        try:
            # 新規作成ボタンのボタンの有効化チェック
            self.change_diable_creating_button()
        except Exception as e:
            self._err_output.clear()
            alert = pn.pane.Alert(f'## [INTERNAL ERROR] : {traceback.format_exc()}',sizing_mode="stretch_width",alert_type='danger')
            self._err_output.append(alert)


    def change_diable_creating_button(self):
        # サブフロー新規作成フォームの必須項目が選択・入力が満たしている場合、新規作成ボタンを有効化する

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


        value = self._parent_sub_flow_type_selector.value
        if value is None:
            self.submit_button.disabled = True
            return
        elif int(value) < 1:
            self.submit_button.disabled = True
            return

        value = self._parent_sub_flow_selector.value
        if value is None:
            self.submit_button.disabled = True
            return
        elif len(value) < 1:
            self.submit_button.disabled = True
            return

        self.submit_button.disabled = False

    #########################
    # サブフロー間接続編集フォーム #
    #########################
    def update_sub_flow_widget_box_for_relink(self):
        # サブフロー間接続編集フォーム
        # 開発中のためアラートを表示する。
        alert = pn.pane.Alert(msg_config.get('DEFAULT','developing'),sizing_mode="stretch_width",alert_type='warning')
        self._sub_flow_widget_box.clear()
        self._sub_flow_widget_box.append(alert)

    #########################
    # サブフロー名称変更フォーム #
    #########################
    def update_sub_flow_widget_box_for_rename(self):
        # サブフロー名称変更フォーム
        # 開発中のためアラートを表示する。
        alert = pn.pane.Alert(msg_config.get('DEFAULT','developing'),sizing_mode="stretch_width",alert_type='warning')
        self._sub_flow_widget_box.clear()
        self._sub_flow_widget_box.append(alert)



    #########################
    # サブフロー削除フォーム #
    #########################
    def update_sub_flow_widget_box_for_delete(self):
        # サブフロー削除フォーム
        # 開発中のためアラートを表示する。
        alert = pn.pane.Alert(msg_config.get('DEFAULT','developing'),sizing_mode="stretch_width",alert_type='warning')
        self._sub_flow_widget_box.clear()
        self._sub_flow_widget_box.append(alert)




    #################
    # クラスメソッド #
    #################

    @classmethod
    def generate(cls, working_path:str):
        """Generate main menu

        working_path : Notebookのファイルの位置
        """
        # panel activation
        pn.extension()
        # Get initial setup complete status
        ## ~/.data-governance/setup_completed.txt, if present, complete, if not, not complete
        ## TODO:再調整要
        # https://github.com/NII-DG/dg-researchflowsのデータが配置されているディレクトリ
        # Jupyter環境では/home/jovyan
        abs_root = working_path[0:working_path.rfind(path_config.DATA_GOVERNANCE)-1]
        # 初期セットアップ完了フラグファイルパス
        abs_setup_completed_file_path = os.path.join(abs_root, path_config.SETUP_COMPLETED_TEXT_PATH)


        if os.path.isfile(abs_setup_completed_file_path):
            # Initial setup is complete.
            # Display the main menu
            main_menu = MainMenu(abs_root)
            ## 機能コントローラーを配置
            main_menu_title = 'メインメニュー'
            main_menu_box = pn.WidgetBox(f'## {main_menu_title}', main_menu._menu_tabs)
            display(main_menu_box)
            ## リサーチフロー図を配置
            display(main_menu._research_flow_image)
            ## システムエラー表示オブジェクトを配置
            display(main_menu._err_output)
        else:
            # Initial setup is incomplete.
            # Leads you to the initial setup

            # display message
            html_text.display_msg_warm(msg=msg_config.get('main_menu', 'required_initial_setup'))
            # display initial setup link button
            initial_setup_link_button = pn.pane.HTML()
            ## TODO:再調整要
            initial_setup_link_button.object = html_button.create_button(
                url = './setup.ipynb',
                msg=msg_config.get('main_menu', 'access_initial_setup'),
                button_width='500px'
            )
            initial_setup_link_button.width = 500
            display(initial_setup_link_button)
            display(Javascript('IPython.notebook.save_checkpoint();'))
