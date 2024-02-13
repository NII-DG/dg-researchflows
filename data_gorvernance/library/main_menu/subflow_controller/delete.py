import panel as pn

from ...utils.config import path_config, message as msg_config
from .base import BaseSubflowForm

class DeleteSubflowForm(BaseSubflowForm):
    """サブフロー削除クラス"""

    # overwrite
    def change_disable_submit_button(self):
        # サブフロー新規作成フォームの必須項目が選択・入力が満たしている場合、新規作成ボタンを有効化する
        self.change_submit_button_init(msg_config.get('main_menu', 'create_sub_flow'))

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

        self.submit_button.disabled = False

    def define_input_form(self):
        """サブフロー削除フォーム"""
        # 開発中のためアラートを表示する。
        return pn.pane.Alert(msg_config.get('DEFAULT','developing'),sizing_mode="stretch_width",alert_type='warning')

    def main(self):
        """サブフロー削除処理"""

        # 新規作成ボタンを処理中ステータスに更新する
        self.change_submit_button_processing(msg_config.get('main_menu', 'creating_sub_flow'))

        # 入力情報を取得する。
        phase_seq_number = self._sub_flow_type_selector.value
        sub_flow_id = self._sub_flow_name_selector.value