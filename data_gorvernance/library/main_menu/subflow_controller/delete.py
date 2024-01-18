import panel as pn

from ...utils.config import path_config, message as msg_config
from .base import BaseSubflowForm
from ...utils.widgets import Alert

class DeleteSubflowForm(BaseSubflowForm):
    """サブフロー削除クラス"""

    def __init__(self, abs_root, message_box) -> None:
        super().__init__(abs_root, message_box)
        # 処理開始ボタン
        self.change_submit_button_init(msg_config.get('main_menu', 'delete_sub_flow'))

    # overwrite
    def change_disable_submit_button(self):
        # サブフロー新規作成フォームの必須項目が選択・入力が満たしている場合、新規作成ボタンを有効化する
        self.change_submit_button_init(msg_config.get('main_menu', 'delete_sub_flow'))

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
        sub_flow_type_list = self._sub_flow_type_selector.options
        if len(sub_flow_type_list) < 2:
            # defaultがあるため2未満にする
            return Alert.warning(msg_config.get('main_menu','nothing_editable_subflow'))
        return pn.Column(
            f'### {msg_config.get("main_menu", "delete_sub_flow_title")}',
            self._sub_flow_type_selector,
            self._sub_flow_name_selector,
            self.submit_button
            )

    def main(self):
        """サブフロー削除処理"""

        # 新規作成ボタンを処理中ステータスに更新する
        self.change_submit_button_processing(msg_config.get('main_menu', 'update_delete_sub_flow'))

        # 入力情報を取得する。
        phase_seq_number = self._sub_flow_type_selector.value
        sub_flow_id = self._sub_flow_name_selector.value

        try:
            self.reserch_flow_status_operater.del_sub_flow_data_by_sub_flow_id(sub_flow_id)
        except Exception:
            self.change_submit_button_error(msg_config.get('main_menu', 'error_delete_sub_flow'))
            raise

        # 新規作成ボタンを作成完了ステータスに更新する
        self.change_submit_button_success(msg_config.get('main_menu', 'success_delete_sub_flow'))