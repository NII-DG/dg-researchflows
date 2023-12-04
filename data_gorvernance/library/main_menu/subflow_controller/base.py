import re
from typing import Dict, List
import traceback

import panel as pn
from dg_drawer.research_flow import ResearchFlowStatus, PhaseStatus

from ...utils.setting import ResearchFlowStatusOperater
from ...utils.config import path_config, message as msg_config


class BaseSubflowForm():
    """サブフロー操作基底クラス"""

    def __init__(self, abs_root, message_box) -> None:
        self.abs_root = abs_root

        self._research_flow_status_file_path = path_config.get_research_flow_status_file_path(abs_root)
        self.reserch_flow_status_operater = ResearchFlowStatusOperater(self._research_flow_status_file_path)

        # リサーチフローステータス管理情報の取得
        research_flow_status = ResearchFlowStatus.load_from_json(self._research_flow_status_file_path)
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

        # サブフロー名称（必須）：テキストフォーム
        self._sub_flow_name_form = pn.widgets.TextInput(
            name=msg_config.get('main_menu', 'sub_flow_name'),
            placeholder='Enter a sub flow name here…', max_length=15)
        # サブフロー名称（必須）：テキストフォームのイベントリスナー
        self._sub_flow_name_form.param.watch(self.callback_input_form, 'value')

        # データディレクトリ名
        self._data_dir_name_form = pn.widgets.TextInput(
            name=msg_config.get('main_menu', 'data_dir_name'),
            placeholder='Enter a data directory name here…', max_length=50)
        # データディレクトリ名：テキストフォームのイベントリスナー
        self._data_dir_name_form.param.watch(self.callback_input_form, 'value')

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

        # 処理開始ボタン
        self.submit_button = pn.widgets.Button(disabled=True)
        self.change_submit_button_init(msg_config.get('main_menu', 'create_sub_flow'))
        self.submit_button.width = 500


    def set_submit_button_on_click(self, callback_function):
        """処理開始ボタンのイベントリスナー設定"""
        self.submit_button.on_click(callback_function)

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
        self.submit_button.button_style = 'solid'
        self.submit_button.icon = 'plus'

    def change_submit_button_processing(self, name):
        self.submit_button.name = name
        self.submit_button.button_type = 'primary'
        self.submit_button.button_style = 'outline'

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
            self.change_diable_submit_button()
        except Exception as e:
            self._err_output.update_error(f'## [INTERNAL ERROR] : {traceback.format_exc()}')

    def callback_input_form(self, event):
        # サブフロー名称（必須）：テキストフォームコールバックファンクション
        try:
            # 新規作成ボタンのボタンの有効化チェック
            self.change_diable_submit_button()
        except Exception as e:
            self._err_output.update_error(f'## [INTERNAL ERROR] : {traceback.format_exc()}')

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
            self.change_diable_submit_button()
        except Exception as e:
            self._err_output.update_error(f'## [INTERNAL ERROR] : {traceback.format_exc()}')

    def callback_parent_sub_flow_selector(self, event):
        try:
            # 新規作成ボタンのボタンの有効化チェック
            self.change_diable_submit_button()
        except Exception as e:
            self._err_output.update_error(f'## [INTERNAL ERROR] : {traceback.format_exc()}')


    def change_diable_submit_button(self):
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
        self.change_submit_button_init(msg_config.get('main_menu', 'create_sub_flow'))

    def validate_sub_flow_name(self):
        creating_phase_seq_number = self._sub_flow_type_selector.value
        sub_flow_name = self._sub_flow_name_form.value_input

        if sub_flow_name is None:
            # sub_flow_nameがNoneの場合、ユーザ警告
            self.change_submit_button_warning(msg_config.get('main_menu','not_input_subflow_name'))
            return False

        if not self.reserch_flow_status_operater.is_unique_subflow_name(creating_phase_seq_number, sub_flow_name):
            # サブフロー名がユニークでないの場合、ユーザ警告
            self.change_submit_button_warning(msg_config.get('main_menu','must_not_same_subflow_name'))
            return False

        if len(str(sub_flow_name).replace(" ", "").replace("　", "")) < 1:
            # 半角と全角スペースのみの場合、ユーザ警告
            self.change_submit_button_warning(msg_config.get('main_menu','must_not_only_space'))
            return False

        return True

    def validate_data_dir_name(self):
        creating_phase_seq_number = self._sub_flow_type_selector.value
        data_dir_name = self._data_dir_name_form.value_input

        # データディレクトリ名の検証
        if data_dir_name is None:
            # data_dir_nameがNoneの場合、ユーザ警告
            self.change_submit_button_warning(msg_config.get('main_menu','not_input_data_dir'))
            return False

        if re.search(r"[^\x20-\x7E]", data_dir_name):
            # 半角文字でない時、ユーザ警告
            self.change_submit_button_warning(msg_config.get('main_menu','data_dir_pattern_error'))
            return False

        if re.search(r'[\/\\0]', data_dir_name):
            # data_dir_nameに禁止文字列が含まれる時、ユーザ警告
            self.change_submit_button_warning(msg_config.get('main_menu','data_dir_pattern_error'))
            return False

        if not self.reserch_flow_status_operater.is_unique_data_dir(creating_phase_seq_number, data_dir_name):
            # data_dir_nameがユニークでないの場合、ユーザ警告
            self.change_submit_button_warning(msg_config.get('main_menu','must_not_same_data_dir'))
            return False

        return True