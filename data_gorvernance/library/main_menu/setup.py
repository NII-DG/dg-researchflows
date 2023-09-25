import os
from ..utils.config import path_config, message as msg_config
from ..subflow.menu import access_main_menu
from pathlib import Path
import panel as pn
from IPython.display import display
from IPython.core.display import Javascript, HTML

DEFAULT_WIDTH = 600
SELECT_DEFAULT_VALUE = '--'

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
    def display_main_menu(self,nb_working_file_path:str):
        display()
        access_main_menu(nb_working_file_path)

    def define_setup_form(self):
        # ユーザ名
        self.user_name_form = pn.widgets.TextInput(name=msg_config.get('user_auth','username_title'), placeholder=msg_config.get('user_auth','username_help'), width=DEFAULT_WIDTH)
        # パスワード
        self.password_form = pn.widgets.PasswordInput(name=msg_config.get('user_auth','password_title'), placeholder=msg_config.get('user_auth','password_help'), width=DEFAULT_WIDTH)
        # 送信ボタン
        self.submit_button = pn.widgets.Button(name=msg_config.get('form','submit_button'), button_type= "default", width=DEFAULT_WIDTH)

        # システムエラーメッセージオブジェクトの定義
        self._err_output = pn.WidgetBox()
        self._err_output.width = 900






    @classmethod
    def setup_form(cls,nb_working_file_path:str):
        pn.extension()
        cs = ContainerSetter(nb_working_file_path)

        # 初期セットアップ完了ステータスファイルの存在をチェックする
        if os.path.exists(cs.setup_completed_file_path):
            # 存在する場合
            # 初期セットアップ済みとして、メインメニューへのボタンを表示する。
            alert = pn.pane.Alert(msg_config.get('setup', 'setup_completed'),sizing_mode="stretch_width",alert_type='warning')
            display(alert)
            cs.display_main_menu(nb_working_file_path)
        else:
            # 存在しない場合
            # 初期セットアップフォームを表示する。

            ## フォームを定義する
            cs.define_setup_form()
            ## フォームを表示する。

            pass


    @classmethod
    def completed_setup(cls,nb_working_file_path:str):
        # 初期セットアップ完了ステータスファイルを作成する
        cs = ContainerSetter(nb_working_file_path)

        # 初期セットアップ完了ステータスファイルの存在をチェックする
        if os.path.exists(cs.setup_completed_file_path):
            # 存在する場合
            # 初期セットアップ済みとして、エラーにする
            alert = pn.pane.Alert(msg_config.get('setup', 'setup_completed'),sizing_mode="stretch_width",alert_type='warning')
            display(alert)
            cs.display_main_menu(nb_working_file_path)
            raise Exception('Cannot run because initial setup is complete')
        else:
            # 存在しない場合
            # 初期セットアップ完了ステータスファイルを作成する
            setup_flag_file = Path(cs.setup_completed_file_path)
            setup_flag_file.touch()


    @classmethod
    def return_main_menu(cls,nb_working_file_path:str):
        pn.extension()
        cs = ContainerSetter(nb_working_file_path)
        cs.display_main_menu(cs.nb_working_file_path)
