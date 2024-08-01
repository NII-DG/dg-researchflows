"""サブフローの削除

このモジュールはサブフロー削除クラスを始め、新しいサブフローのデータを削除したりするメソッドなどがあります。
"""
from typing import Dict, List

import panel as pn
from dg_drawer.research_flow import PhaseStatus

from ...utils.config import path_config, message as msg_config
from .base import BaseSubflowForm
from ...utils.widgets import Alert

class DeleteSubflowForm(BaseSubflowForm):
    """サブフロー削除クラスです。

    Attributes:
        instance:
            abs_root (str): サブフローの絶対パス
            message_box (MessageBox): メッセージを格納する。
            change_submit_button_init(Callable):処理開始ボタン
    """

    def __init__(self, abs_root:str, message_box:pn.widgets.MessageBox) -> None:
        """DeleteSubflowForm コンストラクタのメソッドです

        Args:
            abs_root (str): サブフローの絶対パス
            message_box (MessageBox): メッセージを格納する。
        """
        super().__init__(abs_root, message_box)
        # 処理開始ボタン
        self.change_submit_button_init(msg_config.get('main_menu', 'delete_sub_flow'))

    # overwrite
    def generate_sub_flow_name_options(self, phase_seq_number:int, research_flow_status:List[PhaseStatus])->Dict[str, int]:
        """サブフロー種別(フェーズ)を表示するメソッドです。

        Args:
            research_flow_status (List[PhaseStatus]): リサーチフローステータス管理情報

        Returns:
            Dict[str, int]: フェーズ表示名を返す。
        """
        # サブフロー名(表示名をkey, サブフローIDをVauleとする)
        name_options = {}
        name_options['--'] = 0
        if phase_seq_number == 0:
            return name_options

        for phase_status in research_flow_status:
            if phase_status._seq_number < phase_seq_number:
                continue
            if phase_status._seq_number == phase_seq_number:
                for sf in phase_status._sub_flow_data:
                    name_options[sf._name] = sf._id
                break

        for phase_status in research_flow_status:
            if phase_status._seq_number <= phase_seq_number:
                continue
            for sf in phase_status._sub_flow_data:
                del_names = []
                for name, id in name_options.items():
                    if id in sf._parent_ids:
                        del_names.append(name)
                for name in del_names:
                    del name_options[name]

        return name_options

    # overwrite
    def change_disable_submit_button(self):
        """サブフロー新規作成フォームの必須項目が選択・入力が満たしている場合、新規作成ボタンを有効化するメソッドです。"""
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

    def define_input_form(self) -> Alert:
        """サブフロー削除フォームを定義するメソッドです。
            
        Retunes:
            Alert | pn.Column: フォームに表示する内容
        """
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
        """サブフロー削除処理のメソッドです。
          
        入力情報やパスを取得し、 削除したいデータを取得する。 
        
        Raises:
            Exception:削除失敗したエラー
        """

        # 新規作成ボタンを処理中ステータスに更新する
        self.change_submit_button_processing(msg_config.get('main_menu', 'update_delete_sub_flow'))

        # 入力情報を取得する。
        phase_seq_number = self._sub_flow_type_selector.value
        sub_flow_id = self._sub_flow_name_selector.value

        # 削除前にパスを取得しておく
        phase_name = self.reserch_flow_status_operater.get_subflow_phase(phase_seq_number)
        data_dir_name = self.reserch_flow_status_operater.get_data_dir(phase_name, sub_flow_id)
        path = path_config.get_task_data_dir(self.abs_root, phase_name, data_dir_name)

        try:
            self.reserch_flow_status_operater.del_sub_flow_data_by_sub_flow_id(sub_flow_id)
        except Exception:
            self.change_submit_button_error(msg_config.get('main_menu', 'error_delete_sub_flow'))
            raise

        message = msg_config.get('main_menu', 'delete_caution').format(path)
        self._err_output.update_info(message)
        # フォームの初期化
        self._sub_flow_type_selector.value = 0
        self.change_submit_button_init(msg_config.get('main_menu', 'delete_sub_flow'))