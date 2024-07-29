"""サブフローの名称変更
    このモジュールはサブフロー名称変更クラスを始め、新しいサブフローの名称を変更したりする関数などがあります。
"""
import os
import traceback

import panel as pn

from ...utils.config import path_config, message as msg_config
from .base import BaseSubflowForm
from ...utils.string import StringManager
from ...utils.widgets import Alert
from ...utils.error import InputWarning


class RenameSubflowForm(BaseSubflowForm):
    """サブフロー名称変更クラスです。
        
    
    Attributes:
        class:
            なし

        instance:
            abs_root (str): サブフローの絶対パス
            message_box (MessageBox): メッセージを格納する。
    
    """

    def __init__(self, abs_root, message_box) -> None:
        """RenameSubflowForm コンストラクタの関数です
            親クラス__init__メソッドを呼び出しています。

        Args:
            abs_root (str): サブフローの絶対パス
            message_box (MessageBox): メッセージを格納する。

        """
        super().__init__(abs_root, message_box)
        # 処理開始ボタン
        self.change_submit_button_init(msg_config.get('main_menu', 'rename_sub_flow'))

    # overwrite
    def callback_sub_flow_name_selector(self, event):
        """サブフロー種別(フェーズ)を表示する関数です。

        Returns:
            Dict[str, int]: フェーズ表示名を返す。

        Raises:
            Exception: サブフロー種別(フェーズ)がないエラー
            Exception: サブフロー名がないエラー
        """
        # サブフロー名称：シングルセレクトコールバックファンクション
        try:
            selected_sub_flow_type = self._sub_flow_type_selector.value
            if selected_sub_flow_type is None:
                raise Exception('Sub Flow Type Selector has None')
            selected_sub_flow_id = self._sub_flow_name_selector.value
            if selected_sub_flow_id is None:
                raise Exception('Sub Flow Name Selector has None')

            if selected_sub_flow_type == 0 or selected_sub_flow_id == 0:
                self._sub_flow_name_form.value = ''
                self._sub_flow_name_form.value_input = ''
                self._data_dir_name_form.value = ''
                self._data_dir_name_form.value_input = ''
            else:
                old_sub_flow_name, old_data_dir_name = self.reserch_flow_status_operater.get_flow_name_and_dir_name(selected_sub_flow_type, selected_sub_flow_id)
                self._sub_flow_name_form.value = old_sub_flow_name
                self._sub_flow_name_form.value_input = old_sub_flow_name
                self._data_dir_name_form.value = old_data_dir_name
                self._data_dir_name_form.value_input = old_data_dir_name

            # 新規作成ボタンのボタンの有効化チェック
            self.change_disable_submit_button()
        except Exception as e:
            self._err_output.update_error(f'## [INTERNAL ERROR] : {traceback.format_exc()}')

    # overwrite
    def change_disable_submit_button(self):
        """サブフロー新規作成フォームの必須項目が選択・入力が満たしている場合、新規作成ボタンを有効化する関数です。
    

        """
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
        """サブフロー名称変更フォームの関数です。
        
        Returns:
            pn.Column:サブフロー名称変更フォームに必要な値を返す。

        """
        sub_flow_type_list = self._sub_flow_type_selector.options
        if len(sub_flow_type_list) < 2:
            # defaultがあるため2未満にする
            return Alert.warning(msg_config.get('main_menu','nothing_editable_subflow'))
        return  pn.Column(
            f'### {msg_config.get("main_menu", "update_sub_flow_name_title")}',
            self._sub_flow_type_selector,
            self._sub_flow_name_selector,
            self._sub_flow_name_form,
            self._data_dir_name_form,
            self.submit_button
            )

    def main(self):
        """サブフロー名称変更処理の関数です。
        
        Raises:
            InputWarning:入力値に不備があったエラー
            InputWarning:同じファイルが存在している時のエラー
            Exception:ファイル名の変更に失敗した時のエラー

        
        """

        # 新規作成ボタンを処理中ステータスに更新する
        self.change_submit_button_processing(msg_config.get('main_menu', 'update_rename_sub_flow'))

        # 入力情報を取得する。
        phase_seq_number = self._sub_flow_type_selector.value
        sub_flow_id = self._sub_flow_name_selector.value
        sub_flow_name = self._sub_flow_name_form.value_input
        data_dir_name = self._data_dir_name_form.value_input

        old_sub_flow_name, old_data_dir_name = self.reserch_flow_status_operater.get_flow_name_and_dir_name(phase_seq_number, sub_flow_id)

        # 入力値の検証
        try:
            sub_flow_name = StringManager.strip(sub_flow_name)
            self.validate_sub_flow_name(sub_flow_name)
            if sub_flow_name != old_sub_flow_name:
                self.is_unique_subflow_name(sub_flow_name, phase_seq_number)

            data_dir_name = StringManager.strip(data_dir_name)
            self.validate_data_dir_name(data_dir_name)
            if data_dir_name != old_data_dir_name:
                self.is_unique_data_dir(data_dir_name, phase_seq_number)
        except InputWarning as e:
            self.change_submit_button_warning(str(e))
            raise

        phase_name = self.reserch_flow_status_operater.get_subflow_phase(phase_seq_number)
        new_path = path_config.get_task_data_dir(self.abs_root, phase_name, data_dir_name)
        old_path = path_config.get_task_data_dir(self.abs_root, phase_name, old_data_dir_name)

        # ディレクトリ名を変更する場合
        if new_path != old_path:

            if os.path.exists(new_path):
                message = msg_config.get('main_menu','data_directory_exist')
                self.change_submit_button_warning(message)
                raise InputWarning(message)

            if not os.path.isdir(old_path):
                self.change_submit_button_error(msg_config.get('main_menu', 'error_rename_sub_flow'))
                raise Exception(f'There is no directory. path : {old_path}')

            try:
                os.rename(old_path, new_path)
            except (FileExistsError, NotADirectoryError, OSError):
                message = msg_config.get('main_menu','data_directory_exist')
                self.change_submit_button_warning(message)
                raise InputWarning(message)
            except Exception:
                self.change_submit_button_error(msg_config.get('main_menu', 'error_rename_sub_flow'))
                raise

        try:
            self.reserch_flow_status_operater.rename_sub_flow(phase_seq_number, sub_flow_id, sub_flow_name, data_dir_name)
        except Exception:
            self.change_submit_button_error(msg_config.get('main_menu', 'error_rename_sub_flow'))
            # エラーの場合は変更したディレクトリ名を元に戻す
            if new_path != old_path:
                os.rename(new_path, old_path)
            raise

        # フォームの初期化
        self._sub_flow_type_selector.value = 0
        self.change_submit_button_init(msg_config.get('main_menu', 'rename_sub_flow'))
