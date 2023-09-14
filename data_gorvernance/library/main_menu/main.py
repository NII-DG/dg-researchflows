

import json
from typing import List
from ..utils.config import path_config, message as msg_config
from ..utils.html import text as html_text, button as html_button
from IPython.display import display
from dg_drawer.research_flow import ResearchFlowStatus, PhaseStatus, FlowDrawer
from ..main_menu.research_flow_status import ResearchFlowStatusFile as rfsf

import panel as pn
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir_path = os.path.abspath(os.path.join(script_dir, '../'))

class MainMenu():
    """MainMenu Class

    FUNCTION:

    1. Display the Research Flow Main Menu
    2. View Research Flow Image
    3. When the initial setup has not been performed, the user is guided to the initial setup.

    NOTE:

    Called from data_gorvernance/researchflow/main_menu/main.ipynb
    """

    def __init__(self, abs_root) -> None:

        ##############################
        # リサーチフロー図オブジェクト #
        ##############################

        # リサーチフロー図の生成
        ## data_gorvernance\researchflow\main_menu\status\research_flow_status.json
        self._research_flow_status_file_path = path_config.getResearchFlowStatusFilePath(abs_root)

        # プロジェクトで初回のリサーチフロー図アクセス時の初期化
        rfsf.init_research_preparation(self._research_flow_status_file_path)
        ## リサーチフロー図オブジェクトの定義
        self._research_flow_image = pn.pane.HTML(rfsf.get_svg_of_research_flow_status(self._research_flow_status_file_path))
        self._research_flow_image.width = 1000

        ######################################
        # システムエラーメッセージオブジェクト #
        ######################################

        # システムエラーメッセージオブジェクトの定義
        self._err_output  = pn.pane.HTML()
        self._err_output.object = ''
        self._err_output.width = 700

        ################################
        # 機能コントローラーオブジェクト #
        ################################

        # 機能コントローラーの定義
        self.menu_tabs = pn.Tabs()

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
        self._project_menu.param.watch(self.update_button_for_project_sub_menu,'value')
        project_menu_layout = pn.Row(self._project_menu, self.button_for_project_menu)

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
        self.sub_flow_menu = pn.widgets.Select(options=sub_flow_menu_options, value=0)
        self.sub_flow_menu.param.watch(self.update_sub_flow_form,'value')
        ## サブフロー操作フォーム
        self.sub_flow_form = pn.WidgetBox()
        sub_flow_menu_layout = pn.Column(self.sub_flow_menu, self.sub_flow_form)

        self.menu_tabs.append((project_menu_title, project_menu_layout)) # tab_index = 0
        self.menu_tabs.append((sub_flow_menu_title, sub_flow_menu_layout)) # tab_index = 1

        # 機能コントローラーのイベントリスナー
        self.menu_tabs.param.watch(self.change_tabs, 'active')
        pass

    def change_tabs(self, event):
        tab_index = event.new
        if tab_index == 0:
            # プロジェクト操作
            self.sub_flow_form.clear()
        if tab_index == 1:
            # サブフロー操作
            self.sub_flow_menu.value = 0

    def update_button_for_project_sub_menu(self):
        """遷移ボタン for プロジェクト操作コントローラーの更新"""
        pass

    def update_sub_flow_form(self):
        pass

    def get_research_flow_status(self):
        with open(self._research_flow_status_file_path) as file:
            return json.load(file)


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
            main_menu_box = pn.WidgetBox(f'## {main_menu_title}', main_menu.menu_tabs)
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
                url = './setup.py',
                msg=msg_config.get('main_menu', 'access_initial_setup'),

            )
            display(initial_setup_link_button)
