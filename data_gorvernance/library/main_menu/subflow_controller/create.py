import shutil
import os

import panel as pn

from ...utils.nb_file import NbFile
from ...utils import file
from ...utils.config import path_config, message as msg_config
from .base import BaseSubflowForm


class CreateSubflowForm(BaseSubflowForm):
    """サブフロー新規作成クラス"""

    def define_input_form(self):
        """サブフロー新規作成フォーム"""
        return pn.Column(
            f'### {msg_config.get("main_menu", "create_sub_flow_title")}',
            self._sub_flow_type_selector,
            self._sub_flow_name_form,
            self._data_dir_name_form,
            self._parent_sub_flow_type_selector,
            self._parent_sub_flow_selector,
            self.submit_button
            )


    def main(self):
        """サブフロー新規作成処理"""

        # 新規作成ボタンを処理中ステータスに更新する
        self.change_submit_button_processing(msg_config.get('main_menu', 'creating_sub_flow'))

        # 入力情報を取得する。
        creating_phase_seq_number = self._sub_flow_type_selector.value
        sub_flow_name = self._sub_flow_name_form.value_input
        data_dir_name = self._data_dir_name_form.value_input
        parent_sub_flow_ids = self._parent_sub_flow_selector.value

        if not self.validate_sub_flow_name():
            return

        if not self.validate_data_dir_name():
            return

        # リサーチフローステータス管理JSONの更新
        phase_name, new_sub_flow_id = self.reserch_flow_status_operater.update_research_flow_status(creating_phase_seq_number, sub_flow_name, data_dir_name, parent_sub_flow_ids)

        # /data/<phase_name>/<data_dir_name>の作成
        data_dir_path = ""
        try:
            data_dir_path = self.create_data_dir(phase_name, data_dir_name)
        except Exception:
            # ディレクトリ名が存在した場合
            # リサーチフローステータス管理JSONをロールバック
            self.reserch_flow_status_operater.del_sub_flow_data_by_sub_flow_id(new_sub_flow_id)
            # ユーザーに再入力を促す
            self.change_submit_button_warning(msg_config.get('main_menu','must_not_same_data_dir'))
            return

        # 新規サブフローデータの用意
        try:
            self.prepare_new_subflow_data(phase_name, new_sub_flow_id, sub_flow_name)
        except Exception as e:
            # 失敗した場合に/data/<phase_name>/<data_dir_name>の削除
            os.remove(data_dir_path)
            # 失敗した場合は、リサーチフローステータス管理JSONをロールバック
            self.reserch_flow_status_operater.del_sub_flow_data_by_sub_flow_id(new_sub_flow_id)
            # 新規作成ボタンを作成失敗ステータスに更新する
            raise

        # 新規作成ボタンを作成完了ステータスに更新する
        self.change_submit_button_success(msg_config.get('main_menu', 'success_create_sub_flow'))

    def create_data_dir(self, phase_name:str, data_dir_name:str):
        path = path_config.get_task_data_dir(self.abs_root, phase_name, data_dir_name)
        if os.path.exists(path):
            raise Exception(f'{path} is already exist.')
        os.makedirs(path)
        return path

    def prepare_new_subflow_data(self, phase_name:str, new_sub_flow_id:str, sub_flow_name):

        # 新規サブフローデータの用意
        # data_gorvernance\researchflowを取得
        dg_researchflow_path = os.path.join(self.abs_root, path_config.DG_RESEARCHFLOW_FOLDER)
        # data_gorvernance\base\subflowを取得する
        dg_base_subflow_path = os.path.join(self.abs_root, path_config.DG_SUB_FLOW_BASE_DATA_FOLDER)

        # コピー先フォルダパス
        dect_dir_path = os.path.join(dg_researchflow_path, phase_name, new_sub_flow_id)

        # コピー先フォルダの作成
        os.makedirs(dect_dir_path) # 既に存在している場合はエラーになる

        # 対象コピーファイルorディレクトリリスト
        copy_files = path_config.get_prepare_file_name_list_for_subflow()

        try:
            for copy_file_name in copy_files:
                # コピー元ファイルパス
                src_path = os.path.join(dg_base_subflow_path, phase_name, copy_file_name)
                dect_path = os.path.join(dg_researchflow_path, phase_name, new_sub_flow_id, copy_file_name)
                # コピーする。
                if os.path.isfile(src_path):
                    shutil.copyfile(src_path, dect_path)
                if os.path.isdir(src_path):
                    file.copy_dir(src_path, dect_path, overwrite=True)
                # menu.ipynbファイルの場合は、menu.ipynbのヘッダーにサブフロー名を埋め込む
                if copy_file_name == path_config.MENU_NOTEBOOK:
                    nb_file = NbFile(dect_path)
                    nb_file.embed_subflow_name_on_header(sub_flow_name)
        except Exception as e:
            # 失敗した場合は、コピー先フォルダごと削除する（ロールバック）
            shutil.rmtree(dect_dir_path)
            raise