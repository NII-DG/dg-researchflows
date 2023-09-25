import os
from ..utils.config import path_config
from ..subflow.menu import access_main_menu
from pathlib import Path
import panel as pn

SETUP_COMPLETED_FILE = 'setup_completed.txt'
class ContainerSetter():

    def __init__(self, nb_working_file_path:str) -> None:
        # 実行Notebookパス
        self.nb_working_file_path = nb_working_file_path
        # 絶対rootディレクトリを取得・設定する
        self._abs_root_path = path_config.get_abs_root_form_working_dg_file_path(self.nb_working_file_path)

        # 非同期フォルダーパス（data_gorvernance/working）
        self.working_fdir_path = os.path.join(self._abs_root_path, path_config.DG_WORKING_FOLDER)

        # 初期セットアップ完了ステータスファイルパス(data_gorvernance/working/setup_completed.txt)
        self.setup_completed_file_path = os.path.join(self.working_fdir_path, SETUP_COMPLETED_FILE)

        # 非同期フォルダーの作成（有れば作成しない）
        os.makedirs(self.working_fdir_path, exist_ok=True)

    def del_setup_completed_file(self):
        if os.path.exists(self.setup_completed_file_path):
            os.remove(self.setup_completed_file_path)
        else:
            pass

    @classmethod
    def setup_form(cls,nb_working_file_path:str):
        pn.extension()
        cs = ContainerSetter(nb_working_file_path)
        # 初期セットアップが再実行されて場合に備え、初期セットアップ完了ステータスファイルを削除する
        cs.del_setup_completed_file()

        pass

    @classmethod
    def completed_setup(cls,nb_working_file_path:str):
        # 初期セットアップ完了ステータスファイルを作成する
        cs = ContainerSetter(nb_working_file_path)
        setup_flag_file = Path(cs.setup_completed_file_path)
        setup_flag_file.touch()

    @classmethod
    def return_main_menu(cls,nb_working_file_path:str):
        pn.extension()
        access_main_menu(nb_working_file_path)
