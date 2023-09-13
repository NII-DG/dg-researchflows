

import json
from ..utils.config import path_config, message as msg_config
from ..utils.html import text as html_text, button as html_button
from IPython.display import display
from dg_drawer.research_flow import ResearchFlowStatus, PhaseStatus, FlowDrawer

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

    Called from template\\library\\main_menu\\main.py
    """

    def __init__(self) -> None:
        # リサーチフロー図の生成
        ## researchflow\main_menu\status\research_flow_status.json
        relative_research_flow_status_file_path = '../../../../researchflow/main_menu/status/research_flow_status.json'
        abs_research_flow_status_file_path = os.path.abspath(os.path.join(script_dir, relative_research_flow_status_file_path))
        self._research_flow_status_file_path = abs_research_flow_status_file_path

        ## リサーチフロー図オブジェクトの定義
        self._research_flow_image = pn.pane.HTML(self.get_svg_of_research_flow_status)
        self._research_flow_image.width = 1000

        # 開発用エラーメッセージオブジェクトの定義
        self._err_output  = pn.pane.HTML()
        self._err_output.object = ''
        self._err_output.width = 700

        # 機能コントローラーの定義


        ## プロジェクト操作コントローラーの定義
        ### 遷移ボタン for プロジェクト操作コントローラー
        self.button_for_project_sub_menu = pn.pane.HTML()
        self.button_for_project_sub_menu.object = html_button.create_button(msg=msg_config.get('main_menu', 'disable_jump_button'), disable=True, border=['dashed', '1px'],button_background_color='#ffffff')

        ### プロジェクト操作アクションセレクタ―
        project_sub_menu_options = dict()
        project_sub_menu_options[msg_config.get('DEFAULT', 'selector_default')] = 0
        project_sub_menu_options[msg_config.get('main_menu', 'edit_governance_sheet_title')] = 1
        project_sub_menu_options[msg_config.get('main_menu', 'verification_results_title')] = 2
        project_sub_menu_options[msg_config.get('main_menu', 'monitoring_settings_title')] = 3
        project_sub_menu_options[msg_config.get('main_menu', 'update_dmp_title')] = 4
        project_sub_menu_options[msg_config.get('main_menu', 'finish_research_title')] = 5
        self._project_sub_menu = pn.widgets.Select(options=project_sub_menu_options, value=0)
        ## プロジェクト操作アクションセレクタ―のイベントリスナー
        self._project_sub_menu.param.watch(self.update_button_for_project_sub_menu,'value')



        ## サブフロー操作コントローラーの定義


        pass

    def update_button_for_project_sub_menu(self):
        """遷移ボタン for プロジェクト操作コントローラーの更新"""
        pass

    def get_research_flow_status(self):
        with open(self._research_flow_status_file_path) as file:
            return json.load(file)

    def get_svg_of_research_flow_status(self)->str:
        """Get SVG data of Research Flow Image

        Returns:
            str: SVG data of Research Flow Image
        """
        rfs = ResearchFlowStatus.load_from_json(self._research_flow_status_file_path)
        fd = FlowDrawer(research_flow_status=rfs)
        return fd.draw()

    @classmethod
    def generate(cls):
        """Generate main menu
        """
        # panel activation
        pn.extension()
        # Get initial setup complete status
        ## ~/.data-governance/setup_completed.txt, if present, complete, if not, not complete
        ## TODO:再調整要
        relative_setup_completed_file_path = os.path.join('../../../..', path_config.SETUP_COMPLETED_TEXT_PATH)
        abs_setup_completed_file_path = os.path.abspath(os.path.join(script_dir, relative_setup_completed_file_path))

        if os.path.isfile(abs_setup_completed_file_path):
            # Initial setup is complete.
            # Display the main menu
            main_menu = MainMenu()
            ## 機能コントローラーを配置
            ## リサーチフロー図を配置
            display(main_menu._research_flow_image)
            ## システムエラー表示オブジェクトを配置
            display(main_menu._err_output)
            pass
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
