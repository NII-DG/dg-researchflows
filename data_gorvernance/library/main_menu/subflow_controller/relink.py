"""サブフローの編集

このモジュールはサブフロー間接続編集クラスを始め、新しいサブフローのデータを編集したりするメソッドなどがあります。
"""
from typing import Dict, List
import traceback

import panel as pn
from dg_drawer.research_flow import PhaseStatus

from ...utils.config import message as msg_config
from .base import BaseSubflowForm
from ...utils.widgets import Alert

class RelinkSubflowForm(BaseSubflowForm):
    """サブフロー間接続編集クラスです。
        
    Attributes:
        instance:
            abs_root (str): サブフローの絶対パス
            message_box (MessageBox): メッセージを格納する。
    
    
    """

    def __init__(self, abs_root, message_box) -> None:
        """RelinkSubflowForm コンストラクタのメソッドです

        Args:
            abs_root (str): サブフローの絶対パス
            message_box (MessageBox): メッセージを格納する。

        """

        super().__init__(abs_root, message_box)
        # 処理開始ボタン
        self.change_submit_button_init(msg_config.get('main_menu', 'relink_sub_flow'))

    # overwrite
    def generate_sub_flow_type_options(self, research_flow_status:List[PhaseStatus])->Dict[str, int]:
        """サブフロー種別(フェーズ)を表示するメソッドです。

        Args:
            research_flow_status (List[PhaseStatus]): リサーチフローステータス管理情報

        Returns:
            Dict[str, int]: フェーズ表示名を返す。
        """
        # サブフロー種別(フェーズ)オプション(表示名をKey、順序値をVauleとする)
        pahse_options = {}
        pahse_options['--'] = 0
        for phase_status in research_flow_status:
            # planには親が無い
            if phase_status._seq_number == 1:
                continue
            # experimentはplanのみを親とするため
            if phase_status._seq_number == 2:
                continue
            # サブフローのあるフェーズのみ
            if len(phase_status._sub_flow_data) > 0:
                pahse_options[msg_config.get('research_flow_phase_display_name',phase_status._name)] = phase_status._seq_number
        return pahse_options

    def get_parent_type_and_ids(self, phase_seq_number, sub_flow_id, research_flow_status:List[PhaseStatus]):
        """親サブフロー種別(フェーズ)と親サブフローIDを取得するメソッドです。

        Args:
            phase_seq_number (int): フェーズ番号
            sub_flow_id (Select): サブフローID
            research_flow_status (List[PhaseStatus]): リサーチフローステータス管理情報

        Returns:
            parent_sub_flow_type(Literal): 親サブフロー種別(フェーズ)
            parent_ids(list):親サブフローIDの値を返す。
        """
        parent_ids = []
        parent_sub_flow_type = 0
        if phase_seq_number == 0:
            return parent_sub_flow_type, parent_ids
        for phase_status in research_flow_status:
            if phase_status._seq_number != phase_seq_number:
                continue
            for sf in phase_status._sub_flow_data:
                if sf._id == sub_flow_id:
                    parent_ids.extend(sf._parent_ids)
                    break
            break
        for phase_status in research_flow_status:
            if phase_status._seq_number < phase_seq_number:
                for sf in phase_status._sub_flow_data:
                    if sf._id in parent_ids:
                        parent_sub_flow_type = phase_status._seq_number
                        break

        return parent_sub_flow_type, parent_ids

    # overwrite
    def callback_sub_flow_name_selector(self, event):
        """サブフロー種別(フェーズ)を表示するメソッドです。

        Returns:
            Dict[str, int]: フェーズ表示名を返す。

        Raises:
            Exception: サブフロー選択肢タイプ、サブフロー名がないエラー
        """
        # サブフロー名称：シングルセレクトコールバックファンクション
        try:
            # リサーチフローステータス管理情報の取得
            research_flow_status = self.reserch_flow_status_operater.load_research_flow_status()
            selected_sub_flow_type = self._sub_flow_type_selector.value
            if selected_sub_flow_type is None:
                raise Exception('Sub Flow Type Selector has None')
            selected_sub_flow_id = self._sub_flow_name_selector.value
            if selected_sub_flow_id is None:
                raise Exception('Sub Flow Name Selector has None')
            # 親サブフロー種別の更新
            parent_sub_flow_type_options = self.generate_parent_sub_flow_type_options(selected_sub_flow_type, research_flow_status)
            self._parent_sub_flow_type_selector.options = parent_sub_flow_type_options
            # 新規作成ボタンのボタンの有効化チェック
            self.change_disable_submit_button()
        except Exception as e:
            self._err_output.update_error(f'## [INTERNAL ERROR] : {traceback.format_exc()}')

    # overwrite
    def callback_parent_sub_flow_type_selector(self, event):
        """親サブフロー種別(フェーズ)を表示するメソッドです。

        Raises:
            Exception: サブフロー種別(フェーズ)、サブフロー名、親サブフロー種別(フェーズ)がないエラー
        """
        # 親サブフロー種別(フェーズ)のコールバックファンクション
        try:
            # リサーチフローステータス管理情報の取得
            research_flow_status = self.reserch_flow_status_operater.load_research_flow_status()

            selected_sub_flow_type = self._sub_flow_type_selector.value
            if selected_sub_flow_type is None:
                raise Exception('Sub Flow Type Selector has None')
            selected_sub_flow_id = self._sub_flow_name_selector.value
            if selected_sub_flow_id is None:
                raise Exception('Sub Flow Name Selector has None')
            selected_parent_type = self._parent_sub_flow_type_selector.value
            if selected_parent_type is None:
                raise Exception('Parent Sub Flow Type Selector has None')

            # 親サブフロー選択の更新
            parent_sub_flow_options = self.generate_parent_sub_flow_options(selected_parent_type, research_flow_status)
            self._parent_sub_flow_selector.options = parent_sub_flow_options
            # 親サブフロー選択の値の更新
            parent_sub_flow_type, parent_ids = self.get_parent_type_and_ids(
                phase_seq_number=selected_sub_flow_type, sub_flow_id=selected_sub_flow_id,
                research_flow_status=research_flow_status
            )
            if parent_sub_flow_type == selected_parent_type:
                self._parent_sub_flow_selector.value = parent_ids
            # 新規作成ボタンのボタンの有効化チェック
            self.change_disable_submit_button()
        except Exception as e:
            self._err_output.update_error(f'## [INTERNAL ERROR] : {traceback.format_exc()}')

    # overwrite
    def change_disable_submit_button(self):
        """サブフロー新規作成フォームの必須項目が選択・入力が満たしている場合、新規作成ボタンを有効化するメソッドです。"""
        # サブフロー新規作成フォームの必須項目が選択・入力が満たしている場合、新規作成ボタンを有効化する
        self.change_submit_button_init(msg_config.get('main_menu', 'relink_sub_flow'))

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

        value = self._parent_sub_flow_type_selector.value
        if value is None:
            self.submit_button.disabled = True
            return
        elif int(value) == 0:
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

    def define_input_form(self):
        """サブフロー間接続編集フォームのメソッドです。
        
        Returns:
            pn.Column:サブフロー間接続編集フォームに必要な値を返す。
        """
        sub_flow_type_list = self._sub_flow_type_selector.options
        if len(sub_flow_type_list) < 2:
            # defaultがあるため2未満にする
            return Alert.warning(msg_config.get('main_menu','nothing_editable_subflow'))

        return pn.Column(
            f'### {msg_config.get("main_menu", "update_sub_flow_link_title")}',
            self._sub_flow_type_selector,
            self._sub_flow_name_selector,
            self._parent_sub_flow_type_selector,
            self._parent_sub_flow_selector,
            self.submit_button
            )

    def main(self):
        """サブフロー間接続編集処理のメソッドです。
        
        Raises:
            Exception:編集失敗した場合のエラー
        """

        # 新規作成ボタンを処理中ステータスに更新する
        self.change_submit_button_processing(msg_config.get('main_menu', 'update_relink_sub_flow'))

        # 入力情報を取得する。
        phase_seq_number = self._sub_flow_type_selector.value
        sub_flow_id = self._sub_flow_name_selector.value
        parent_sub_flow_ids = self._parent_sub_flow_selector.value

        try:
            self.reserch_flow_status_operater.relink_sub_flow(phase_seq_number, sub_flow_id, parent_sub_flow_ids)
        except Exception:
            self.change_submit_button_error(msg_config.get('main_menu', 'error_relink_sub_flow'))
            raise

        # フォームの初期化
        self._sub_flow_type_selector.value = 0
        self.change_submit_button_init(msg_config.get('main_menu', 'relink_sub_flow'))

