import traceback

import panel as pn

from ...utils.config import path_config, message as msg_config
from .base import BaseSubflowForm
from ...utils.checker import StringManager

class RenameSubflowForm(BaseSubflowForm):
    """サブフロー名称変更クラス"""

    def __init__(self, abs_root, message_box) -> None:
        super().__init__(abs_root, message_box)
        # 処理開始ボタン
        self.change_submit_button_init(msg_config.get('main_menu', 'rename_sub_flow'))

    # overwrite
    def callback_sub_flow_name_selector(self, event):
        # サブフロー名称：シングルセレクトコールバックファンクション
        try:

            # 新規作成ボタンのボタンの有効化チェック
            self.change_disable_submit_button()
        except Exception as e:
            self._err_output.update_error(f'## [INTERNAL ERROR] : {traceback.format_exc()}')

    # overwrite
    def change_disable_submit_button(self):
        # サブフロー新規作成フォームの必須項目が選択・入力が満たしている場合、新規作成ボタンを有効化する
        self.change_submit_button_init(msg_config.get('main_menu', 'rename_sub_flow'))

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
        elif value == 0:
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

        self.submit_button.disabled = False

    def define_input_form(self):
        """サブフロー名称変更フォーム"""
        # 開発中のためアラートを表示する。
        return  pn.Column(
            f'### {msg_config.get("main_menu", "update_sub_flow_name_title")}',
            self._sub_flow_type_selector,
            self._sub_flow_name_selector,
            self._sub_flow_name_form,
            self._data_dir_name_form,
            self.submit_button
            )

    def main(self):
        """サブフロー名称変更処理"""

        # 新規作成ボタンを処理中ステータスに更新する
        self.change_submit_button_processing(msg_config.get('main_menu', 'update_rename_sub_flow'))

        # 入力情報を取得する。
        phase_seq_number = self._sub_flow_type_selector.value
        sub_flow_id = self._sub_flow_name_selector.value
        sub_flow_name = self._sub_flow_name_form.value_input
        data_dir_name = self._data_dir_name_form.value_input

        sub_flow_name = StringManager.strip(sub_flow_name)
        if not self.validate_sub_flow_name(sub_flow_name, phase_seq_number):
            return

        data_dir_name = StringManager.strip(data_dir_name)
        if not self.validate_data_dir_name(data_dir_name, phase_seq_number):
            return

        try:
            self.reserch_flow_status_operater.rename_sub_flow(phase_seq_number, sub_flow_id, sub_flow_name, data_dir_name)
        except Exception:
            self.change_submit_button_error(msg_config.get('main_menu', 'error_rename_sub_flow'))
            raise

        # 新規作成ボタンを作成完了ステータスに更新する
        self.change_submit_button_success(msg_config.get('main_menu', 'success_rename_sub_flow'))