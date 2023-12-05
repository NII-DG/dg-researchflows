import panel as pn

from ...utils.config import path_config, message as msg_config
from .base import BaseSubflowForm

class RenameSubflowForm(BaseSubflowForm):
    """サブフロー名称変更クラス"""

    def define_input_form(self):
        """サブフロー名称変更フォーム"""
        # 開発中のためアラートを表示する。
        return pn.pane.Alert(msg_config.get('DEFAULT','developing'),sizing_mode="stretch_width",alert_type='warning')

    def main(self):
        """サブフロー名称変更処理"""

        # 新規作成ボタンを処理中ステータスに更新する
        self.change_submit_button_processing(msg_config.get('main_menu', 'creating_sub_flow'))

        # 入力情報を取得する。
        creating_phase_seq_number = self._sub_flow_type_selector.value
        sub_flow_name = self._sub_flow_name_form.value_input
        data_dir_name = self._data_dir_name_form.value_input
        parent_sub_flow_ids = self._parent_sub_flow_selector.value