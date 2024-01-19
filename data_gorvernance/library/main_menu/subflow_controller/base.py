import re
from typing import Dict, List
import traceback

import panel as pn
from dg_drawer.research_flow import PhaseStatus

from ...utils.setting import ResearchFlowStatusOperater
from ...utils.config import path_config, message as msg_config
from ...utils.checker import StringManager
from ...utils.widgets import Button, MessageBox


class BaseSubflowForm():
    """サブフロー操作基底クラス"""

    def __init__(self, abs_root, message_box: MessageBox) -> None:
        self.abs_root = abs_root

        research_flow_status_file_path = path_config.get_research_flow_status_file_path(abs_root)
        self.reserch_flow_status_operater = ResearchFlowStatusOperater(research_flow_status_file_path)

        # リサーチフローステータス管理情報の取得
        research_flow_status = self.reserch_flow_status_operater.load_research_flow_status()
        self._err_output = message_box

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

        # サブフロー名称オプション
        sub_flow_name_options = self.generate_sub_flow_name_options(sub_flow_type_options[msg_config.get('form', 'selector_default')], research_flow_status)
        # サブフロー名称：シングルセレクト
        self._sub_flow_name_selector = pn.widgets.Select(
            name=msg_config.get('main_menu', 'sub_flow_name_select'),
            options=sub_flow_name_options,
            value=sub_flow_name_options[msg_config.get('form', 'selector_default')]
        )
        # サブフロー名称のイベントリスナー
        self._sub_flow_name_selector.param.watch(self.callback_sub_flow_name_selector, 'value')

        # サブフロー名称：テキストフォーム
        self._sub_flow_name_form = pn.widgets.TextInput(
            name=msg_config.get('main_menu', 'sub_flow_name_input'),
            placeholder='Enter a sub flow name here…', max_length=15)
        # サブフロー名称：テキストフォームのイベントリスナー
        self._sub_flow_name_form.param.watch(self.callback_menu_form, 'value')

        # データディレクトリ名
        self._data_dir_name_form = pn.widgets.TextInput(
            name=msg_config.get('main_menu', 'data_dir_name'),
            placeholder='Enter a data directory name here…', max_length=50)
        # データディレクトリ名：テキストフォームのイベントリスナー
        self._data_dir_name_form.param.watch(self.callback_menu_form, 'value')

        # 処理開始ボタン
        self.submit_button = Button(disabled=True)
        self.submit_button.width = 500


    def set_submit_button_on_click(self, callback_function):
        """処理開始ボタンのイベントリスナー設定"""
        self.submit_button.on_click(callback_function)

    def generate_sub_flow_type_options(self, research_flow_status:List[PhaseStatus])->Dict[str, int]:
        # サブフロー種別(フェーズ)オプション(表示名をKey、順序値をVauleとする)
        pahse_options = {}
        pahse_options['--'] = 0
        for phase_status in research_flow_status:
            # planは選択させない
            if phase_status._seq_number == 1:
                continue
            # サブフローのあるフェーズのみ
            if len(phase_status._sub_flow_data) > 0:
                pahse_options[msg_config.get('research_flow_phase_display_name',phase_status._name)] = phase_status._seq_number
        return pahse_options

    def generate_sub_flow_name_options(self, phase_seq_number:int, research_flow_status:List[PhaseStatus])->Dict[str, int]:
        # サブフロー名(表示名をkey, サブフローIDをVauleとする)
        name_options = {}
        name_options['--'] = 0
        if phase_seq_number == 0:
            return name_options

        for phase_status in research_flow_status:
            if phase_status._seq_number == phase_seq_number:
                for sf in phase_status._sub_flow_data:
                    name_options[sf._name] = sf._id

        return name_options

    def generate_parent_sub_flow_options(self, pahase_seq_number:int, research_flow_status:List[PhaseStatus])->Dict[str, str]:
        # 親サブフロー選択オプション(表示名をKey、サブフローIDをVauleとする)
        # createとrelinkで用いる
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
        self.submit_button.set_looks_init(name)

    def change_submit_button_processing(self, name):
        self.submit_button.set_looks_processing(name)

    def change_submit_button_success(self, name):
        self.submit_button.set_looks_success(name)

    def change_submit_button_warning(self, name):
        self.submit_button.set_looks_warning(name)

    def change_submit_button_error(self, name):
        self.submit_button.set_looks_error(name)

    ############
    # callback #
    ############

    def callback_menu_form(self, event):
        # フォームコールバックファンクション
        try:
            # 新規作成ボタンのボタンの有効化チェック
            self.change_disable_submit_button()
        except Exception as e:
            self._err_output.update_error(f'## [INTERNAL ERROR] : {traceback.format_exc()}')

    def callback_sub_flow_type_selector(self, event):
        # サブフロー種別(フェーズ):シングルセレクトコールバックファンクション
        try:
            # リサーチフローステータス管理情報の取得
            research_flow_status = self.reserch_flow_status_operater.load_research_flow_status()

            selected_value = self._sub_flow_type_selector.value
            if selected_value is None:
                raise Exception('Sub Flow Type Selector has None')
            # サブフロー名称：シングルセレクトの更新
            sub_flow_name_options = self.generate_sub_flow_name_options(selected_value, research_flow_status)
            self._sub_flow_name_selector.options = sub_flow_name_options
            # 新規作成ボタンのボタンの有効化チェック
            self.change_disable_submit_button()
        except Exception as e:
            self._err_output.update_error(f'## [INTERNAL ERROR] : {traceback.format_exc()}')

    def callback_sub_flow_name_selector(self, event):
        # サブフロー名称：シングルセレクトコールバックファンクション
        # relinkとrenameで継承するため個別処理
        try:
            # 新規作成ボタンのボタンの有効化チェック
            self.change_disable_submit_button()
        except Exception as e:
            self._err_output.update_error(f'## [INTERNAL ERROR] : {traceback.format_exc()}')

    ############
    # validate #
    ############

    def change_disable_submit_button(self):
        """サブフロー新規作成フォームの必須項目が選択・入力が満たしている場合、新規作成ボタンを有効化する"""
        # 継承した先で実装する

    def validate_sub_flow_name(self, sub_flow_name):

        if StringManager.is_empty(sub_flow_name):
            # sub_flow_nameが未入力の場合、ユーザ警告
            self.change_submit_button_warning(msg_config.get('main_menu','not_input_subflow_name'))
            return False
        return True

    def is_unique_subflow_name(self, sub_flow_name, phase_seq_number):

        if not self.reserch_flow_status_operater.is_unique_subflow_name(phase_seq_number, sub_flow_name):
            # サブフロー名がユニークでない場合、ユーザ警告
                self.change_submit_button_warning(msg_config.get('main_menu','must_not_same_subflow_name'))
                return False
        return True

    def validate_data_dir_name(self, data_dir_name):

        # データディレクトリ名の検証
        if StringManager.is_empty(data_dir_name):
            # data_dir_nameが未入力の場合、ユーザ警告
            self.change_submit_button_warning(msg_config.get('main_menu','not_input_data_dir'))
            return False

        if not StringManager.is_half(data_dir_name):
            # 半角文字でない時、ユーザ警告
            self.change_submit_button_warning(msg_config.get('main_menu','data_dir_pattern_error'))
            return False

        if re.search(r'[\/\\0]', data_dir_name):
            # data_dir_nameに禁止文字列が含まれる時、ユーザ警告
            self.change_submit_button_warning(msg_config.get('main_menu','data_dir_pattern_error'))
            return False

        return True

    def is_unique_data_dir(self, data_dir_name, phase_seq_number):

        if not self.reserch_flow_status_operater.is_unique_data_dir(phase_seq_number, data_dir_name):
            # data_dir_nameがユニークでない場合、ユーザ警告
            self.change_submit_button_warning(msg_config.get('main_menu','must_not_same_data_dir'))
            return False
        return True