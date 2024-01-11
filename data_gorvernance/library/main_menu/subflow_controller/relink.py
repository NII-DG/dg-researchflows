from typing import Dict, List
import traceback

import panel as pn
from dg_drawer.research_flow import ResearchFlowStatus, PhaseStatus

from ...utils.config import path_config, message as msg_config
from .base import BaseSubflowForm

class RelinkSubflowForm(BaseSubflowForm):
    """サブフロー間接続編集クラス"""

    def __init__(self, abs_root, message_box) -> None:
        super().__init__(abs_root, message_box)
        research_flow_status = ResearchFlowStatus.load_from_json(self._research_flow_status_file_path)
        # 親サブフロー選択オプション
        parent_sub_flow_options = self.generate_parent_sub_flow_options(0, research_flow_status)
        # 親サブフロー選択 : マルチセレクト
        self._parent_sub_flow_selector = pn.widgets.MultiSelect(
            name=msg_config.get('main_menu', 'parent_sub_flow_name'),
            options=parent_sub_flow_options
            )
        # 親サブフロー選択のイベントリスナー
        self._parent_sub_flow_selector.param.watch(self.callback_menu_form, 'value')

    def get_parent_type_and_ids(self, phase_seq_number, sub_flow_id, research_flow_status:List[PhaseStatus]):
        parent_ids = []
        parent_sub_flow_type = 0
        if phase_seq_number == 0:
            return parent_sub_flow_type, parent_ids
        for phase_status in research_flow_status:
            if phase_status._seq_number == phase_seq_number:
                for data in phase_status._sub_flow_data:
                    parent_ids.extend(data._parent_ids)
        for phase_status in research_flow_status:
            if phase_status._seq_number < phase_seq_number:
                for sf in phase_status._sub_flow_data:
                    if sf._id in parent_ids:
                        parent_sub_flow_type = phase_status._seq_number
                        break

        return parent_sub_flow_type, parent_ids

    def callback_sub_flow_name_selector(self, event):
        # サブフロー名称：シングルセレクトコールバックファンクション
        try:
            # リサーチフローステータス管理情報の取得
            research_flow_status = ResearchFlowStatus.load_from_json(self._research_flow_status_file_path)
            selected_sub_flow_type = self._sub_flow_type_selector.value
            if selected_sub_flow_type is None:
                raise Exception('Sub Flow Type Selector has None')
            selected_sub_flow_name = self._sub_flow_name_selector.value
            if selected_sub_flow_name is None:
                raise Exception('Sub Flow Name Selector has None')
            parent_sub_flow_type, parent_ids = self.get_parent_type_and_ids(
                phase_seq_number=selected_sub_flow_type, sub_flow_id=selected_sub_flow_name,
                research_flow_status=research_flow_status
            )
            parent_sub_flow_options = self.generate_parent_sub_flow_options(parent_sub_flow_type, research_flow_status)
            self._parent_sub_flow_selector.options = parent_sub_flow_options
            self._parent_sub_flow_selector.value = parent_ids
            # 新規作成ボタンのボタンの有効化チェック
            self.change_diable_submit_button()
        except Exception as e:
            self._err_output.update_error(f'## [INTERNAL ERROR] : {traceback.format_exc()}')

    # overwrite
    def change_diable_submit_button(self):
        # サブフロー新規作成フォームの必須項目が選択・入力が満たしている場合、新規作成ボタンを有効化する

        value = self._sub_flow_type_selector.value
        if value is None:
            self.submit_button.disabled = True
            return
        elif int(value) == 0:
            self.submit_button.disabled = True
            return

        value = self._sub_flow_name_selector.value
        if value is None:
            self.submit_button.disabled = True
            return
        elif int(value) == 0:
            self.submit_button.disabled = True
            return

        value = self._data_dir_name_form.value_input
        if value is None:
            self.submit_button.disabled = True
            return
        elif len(value) < 1:
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

    def define_input_form(self):
        """サブフロー間接続編集フォーム"""
        return pn.Column(
            f'### {msg_config.get("main_menu", "create_sub_flow_title")}',
            self._sub_flow_type_selector,
            self._sub_flow_name_selector,
            self._parent_sub_flow_selector,
            self.submit_button
            )

    def main(self):
        """サブフロー間接続編集処理"""

        # 新規作成ボタンを処理中ステータスに更新する
        self.change_submit_button_processing(msg_config.get('main_menu', 'creating_sub_flow'))

        # 入力情報を取得する。
        phase_seq_number = self._sub_flow_type_selector.value
        sub_flow_id = self._sub_flow_name_selector.value
        parent_sub_flow_ids = self._parent_sub_flow_selector.value

