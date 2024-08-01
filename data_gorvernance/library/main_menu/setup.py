"""初期セットアップ

このモジュールはセットアップを行うクラスがあり、セットアップを行うための認証を確認したり、設定を行うメソッドなどがあります。
"""
import os
import re
from ..utils.config import path_config, message as msg_config
from ..utils.storage_provider.gin import gin
from ..subflow.menu import access_main_menu
from pathlib import Path
import panel as pn
from IPython.display import display, clear_output
from IPython.core.display import Javascript
import traceback
from ..utils.error import UnauthorizedError



DEFAULT_WIDTH = 600
SELECT_DEFAULT_VALUE = '--'

SETUP_COMPLETED_FILE = 'setup_completed.txt'
class ContainerSetter():
    """セットアップを行うクラスです。
    
    Attributes:
        instance:
            nb_working_file_path (str): 実行Notebookパス
            _abs_root_path(str):絶対rootディレクトリを取得・設定する
            working_fdir_path(str):非同期フォルダーパス
            setup_completed_file_path(str):初期セットアップ完了ステータスファイルパス
    """

    def __init__(self, nb_working_file_path:str) -> None:
        """ContainerSetter コンストラクタのメソッドです。

        Args:
            nb_working_file_path (str): 実行Notebookパス
        """
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
        """セットアップが完了したファイルを削除するメソッドです。"""
        if os.path.exists(self.setup_completed_file_path):
            os.remove(self.setup_completed_file_path)
        else:
            pass
    def display_main_menu(self,nb_working_file_path:str):
        """メインメニューの画面を表示するメソッドです。

        Args:
            nb_working_file_path (str): 実行Notebookパス
        """
        display()
        access_main_menu(nb_working_file_path)

    def define_setup_form(self):
        """セットアップフォームを定義するメソッドです。"""
        # ユーザ名
        self._user_name_form = pn.widgets.TextInput(name=msg_config.get('user_auth','username_title'), placeholder=msg_config.get('user_auth','username_help'), width=DEFAULT_WIDTH)
        # パスワード
        self._password_form = pn.widgets.PasswordInput(name=msg_config.get('user_auth','password_title'), placeholder=msg_config.get('user_auth','password_help'), width=DEFAULT_WIDTH)
        # 送信ボタン
        self._submit_button = pn.widgets.Button()
        self.change_submit_button_init(msg_config.get('form','submit_button'))
        self._submit_button.on_click(self.callback_submit_user_auth)

        # システムエラーメッセージオブジェクトの定義
        self._msg_output = pn.WidgetBox()
        self._msg_output.width = 900

    def callback_submit_user_auth(self, event):
        """ボタンが押された時、ユーザーに権限があるかどうかを認証するメソッドです。"""
        # 入力値を取得する
        user_name = self._user_name_form.value_input
        password = self._password_form.value_input

        # 入力値のバリエーション
        ## user_name
        if user_name is None or len(user_name)<= 0:
            self.change_submit_button_warning(name=msg_config.get('form', 'none_input_value').format(msg_config.get('form', 'user_name')))
            return

        if not self.validate_format_username(user_name):
            self.change_submit_button_warning(name=msg_config.get('form', 'invali_input_value').format(msg_config.get('form', 'user_name')))
            self._msg_output.clear()
            alert = pn.pane.Alert(msg_config.get('form', 'username_pattern_error'), sizing_mode="stretch_width",alert_type='warning')
            self._msg_output.append(alert)
            return

        ## password
        if password is None or len(password) <= 0:
            self.change_submit_button_warning(name=msg_config.get('form', 'none_input_value').format(msg_config.get('form', 'password')))
            return

        #認証検証準備（GIN-forkのドメインをparam.jsonに用意する）
        try:
            gin.init_param_url()
        except:
            self.change_submit_button_error(name=msg_config.get('DEFAULT', 'unexpected_error'))
            self._msg_output.clear()
            alert = pn.pane.Alert(f'## [INTERNAL ERROR] : {traceback.format_exc()}',sizing_mode="stretch_width",alert_type='danger')
            self._msg_output.append(alert)
            return

        # 認証検証
        try:
            gin.setup_local(user_name, password)
        except UnauthorizedError:
            self.change_submit_button_warning(name=msg_config.get('form', 'invali_input_value').format(msg_config.get('form', 'user_name')+'/'+ msg_config.get('form', 'password')))
            self._msg_output.clear()
            alert = pn.pane.Alert(msg_config.get('user_auth','UnauthorizedError'), sizing_mode="stretch_width",alert_type='warning')
            self._msg_output.append(alert)
            return
        except Exception as e:
            self.change_submit_button_error(name=msg_config.get('DEFAULT', 'unexpected_error'))
            self._msg_output.clear()
            alert = pn.pane.Alert(f'## [INTERNAL ERROR] : {traceback.format_exc()}',sizing_mode="stretch_width",alert_type='danger')
            self._msg_output.append(alert)
            return
        else:
            self.change_submit_button_success(msg_config.get('user_auth','success'))
            self._msg_output.clear()
            return



    def validate_format_username(self, user_name:str):
        """ユーザー名の正規表現を解析するメソッドです。

        Args:
            user_name(str):ユーザー名
        """
        validation = re.compile(r'^[a-zA-Z0-9\-_.]+$')
        return validation.fullmatch(user_name)


    def already_setup(self):
        """セットアップが完了していることを画面に表示するメソッドです"""
        alert = pn.pane.Alert(msg_config.get('setup', 'setup_completed'),sizing_mode="stretch_width",alert_type='warning')
        display(alert)

    def change_submit_button_init(self, name:str):
        """ボタンの状態を初期化するメソッドです。

        Args:
            name (str): メッセージ
        """
        self._submit_button.name = name
        self._submit_button.button_type = 'primary'
        self._submit_button.button_style = 'solid'

    def change_submit_button_processing(self, name:str):
        """ボタンを処理中ステータスに更新するメソッドです。

        Args:
            name (str): 実行中のメッセージ
        """
        self._submit_button.name = name
        self._submit_button.button_type = 'primary'
        self._submit_button.button_style = 'outline'

    def change_submit_button_success(self, name:str):
        """ボタンが押されて成功した時のメッセージを返すメソッドです。

        Args:
            name (str): 成功したメッセージ
        """
        self._submit_button.name = name
        self._submit_button.button_type = 'success'
        self._submit_button.button_style = 'solid'

    def change_submit_button_warning(self, name:str):
        """ボタンが押されて認証が失敗した時の警告メッセージを返すメソッドです。

        Args:
            name (str): 警告メッセージ
        """
        self._submit_button.name = name
        self._submit_button.button_type = 'warning'
        self._submit_button.button_style = 'solid'

    def change_submit_button_error(self, name:str):
        """ボタンが押されて内部エラーが発生した時のエラーを返すメソッドです。

        Args:
            name (str): エラーメッセージ
        """
        self._submit_button.name = name
        self._submit_button.button_type = 'danger'
        self._submit_button.button_style = 'solid'

    @classmethod
    def setup_form(cls,nb_working_file_path:str):
        """セットアップフォームを表示するメソッドです。

        Args:
            nb_working_file_path (str): 実行Notebookパス
        """
        pn.extension()
        cs = ContainerSetter(nb_working_file_path)

        # 初期セットアップ完了ステータスファイルの存在をチェックする
        if os.path.exists(cs.setup_completed_file_path):
            # 存在する場合
            # 初期セットアップ済みとして、メインメニューへのボタンを表示する。
            cs.already_setup()
            cs.display_main_menu(nb_working_file_path)
        else:
            # 存在しない場合
            # 初期セットアップフォームを表示する。

            ## フォームを定義する
            cs.define_setup_form()
            ## フォームを表示する。
            form_section = pn.WidgetBox()
            form_section.append(cs._user_name_form)
            form_section.append(cs._password_form)
            form_section.append(cs._submit_button)
            form_section.append(cs._msg_output)
            display(form_section)

    @classmethod
    def delete_build_token(cls):
        """トークンを削除するメソッドです。

        Raises:
            Exception: トークン削除失敗
        """
        pn.extension()
        cls.check_imcomplete_auth()

        ok, msg =gin.del_build_token()
        if ok and msg is None:
            # パブリックのためのリクエストしなかった
            alert = pn.pane.Alert(msg_config.get('build_token', 'not_need_del'),sizing_mode="stretch_width",alert_type='info')
            display(alert)
            return
        elif ok and msg is not None and msg == '':
            # 削除成功
            alert = pn.pane.Alert(msg_config.get('build_token', 'success'),sizing_mode="stretch_width",alert_type='success')
            display(alert)
            return
        elif ok and msg is not None and len(msg) > 0:
            # リクエストしたが削除しなかった
            alert = pn.pane.Alert(msg,sizing_mode="stretch_width",alert_type='info')
            display(alert)
            return
        elif not ok:
            alert = pn.pane.Alert(msg_config.get('build_token', 'error'),sizing_mode="stretch_width",alert_type='danger')
            display(alert)
            raise Exception('Failed to delete token.')

    @classmethod
    def datalad_create(cls, nb_working_file_path:str):
        """dataladを設定するメソッドです。

        Args:
            nb_working_file_path (str): 実行Notebookパス

        Raises:
            Exception: 予期しないエラーが発生した
        """
        pn.extension()
        cls.check_imcomplete_auth()
        cs = ContainerSetter(nb_working_file_path)

        try:
            ok = gin.datalad_create(cs._abs_root_path)
            clear_output()
            if ok:
                alert = pn.pane.Alert(msg_config.get('setup','datalad_create_success'),sizing_mode="stretch_width",alert_type='info')
                display(alert)
            else:
                alert = pn.pane.Alert(msg_config.get('setup','datalad_create_already'),sizing_mode="stretch_width",alert_type='info')
                display(alert)

        except Exception as e:
            alert = pn.pane.Alert(msg_config.get('DEFAULT', 'unexpected_error'),sizing_mode="stretch_width",alert_type='danger')
            display(alert)
            raise e

    @classmethod
    def ssh_create_key(cls, nb_working_file_path:str):
        """SSHキーを作成するメソッドです。

        Args:
            nb_working_file_path (str): 実行Notebookパス

        Raises:
            Exception: 予期しないエラーが発生した
        """
        pn.extension()
        cls.check_imcomplete_auth()
        cs = ContainerSetter(nb_working_file_path)

        try:
            if gin.create_key(cs._abs_root_path):
                alert = pn.pane.Alert(msg_config.get('setup','ssh_create_success'),sizing_mode="stretch_width",alert_type='info')
            else:
                alert = pn.pane.Alert(msg_config.get('setup','ssh_already_create'),sizing_mode="stretch_width",alert_type='info')
            display(alert)
        except Exception as e:
            alert = pn.pane.Alert(msg_config.get('DEFAULT', 'unexpected_error'),sizing_mode="stretch_width",alert_type='danger')
            display(alert)
            raise e

    @classmethod
    def upload_ssh_key(cls, nb_working_file_path:str):
        """GIN-forkへの公開鍵の登録を行うメソッドです。

        Args:
            nb_working_file_path (str): 実行Notebookパス

        Raises:
            Exception: 予期しないエラーが発生した
        """
        pn.extension()
        cls.check_imcomplete_auth()
        cs = ContainerSetter(nb_working_file_path)

        try:
            msg = gin.upload_ssh_key(cs._abs_root_path)
            alert = pn.pane.Alert(msg ,sizing_mode="stretch_width",alert_type='info')
            display(alert)
        except Exception as e:
            alert = pn.pane.Alert(msg_config.get('DEFAULT', 'unexpected_error'),sizing_mode="stretch_width",alert_type='danger')
            display(alert)
            raise e

    @classmethod
    def ssh_trust_gin(cls, nb_working_file_path:str):
        """SSHホスト（GIN-fork）を信頼することを設定するメソッドです。

        Args:
            nb_working_file_path (str): 実行Notebookパス

        Raises:
            Exception: 予期しないエラーが発生した
        """
        pn.extension()
        cls.check_imcomplete_auth()
        cs = ContainerSetter(nb_working_file_path)

        try:
            gin.trust_gin(cs._abs_root_path)
            alert = pn.pane.Alert(msg_config.get('setup','trust_gin') ,sizing_mode="stretch_width",alert_type='info')
            display(alert)
        except Exception as e:
            alert = pn.pane.Alert(msg_config.get('DEFAULT', 'unexpected_error'),sizing_mode="stretch_width",alert_type='danger')
            display(alert)
            raise e

    @classmethod
    def prepare_sync(cls, nb_working_file_path:str):
        """GIN-forkへの同期調整を行うメソッドです。

        Args:
            nb_working_file_path (str): 実行Notebookパス

        Raises:
            Exception: 予期しないエラーが発生した
        """
        pn.extension()
        cls.check_imcomplete_auth()
        cs = ContainerSetter(nb_working_file_path)

        try:
            gin.prepare_sync(cs._abs_root_path)
            alert = pn.pane.Alert(msg_config.get('setup','prepare_sync') ,sizing_mode="stretch_width",alert_type='info')
            display(alert)
        except Exception as e:
            alert = pn.pane.Alert(msg_config.get('DEFAULT', 'unexpected_error'),sizing_mode="stretch_width",alert_type='danger')
            display(alert)
            raise e

    @classmethod
    def setup_sibling(cls, nb_working_file_path:str):
        pn.extension()
        """siblingの登録をするメソッドです。

        Args:
            nb_working_file_path (str): 実行Notebookパス

        Raises:
            Exception: 予期しないエラーが発生した

        """
        cls.check_imcomplete_auth()

        cs = ContainerSetter(nb_working_file_path)
        try:
            # ローカルにsiblingの登録(HTTP, SSH)
            gin.setup_sibling_to_local()
            # annexブランチの作成とプッシュ
            gin.push_annex_branch(cs._abs_root_path)
            clear_output()
            alert = pn.pane.Alert(msg_config.get('setup','setup_sibling') ,sizing_mode="stretch_width",alert_type='info')
            display(alert)

        except Exception as e:
            alert = pn.pane.Alert(msg_config.get('DEFAULT', 'unexpected_error'),sizing_mode="stretch_width",alert_type='danger')
            display(alert)
            raise e

    @classmethod
    def completed_setup(cls,nb_working_file_path:str):
        """初期セットアップ完了を記録するメソッドです。

        Args:
            nb_working_file_path (str): 実行Notebookパス

        Raises:
            Exception: 初期セットアップが完了していないため実行できませんというエラーが表示される。
        """
        pn.extension()
        cls.check_imcomplete_auth()
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
            alert = pn.pane.Alert(msg_config.get('setup','recoed_setup_completed') ,sizing_mode="stretch_width",alert_type='info')
            display(alert)

    @classmethod
    def syncs_config(cls, nb_working_file_path:str) -> list | str:
        pn.extension()
        """同期のためにファイルとメッセージの設定
        
         Args:
            nb_working_file_path (str): 実行Notebookパス

        Returns:
            list:Gitのパス
            str:コミットメッセージ
        """
        cls.check_imcomplete_auth()
        display(Javascript('IPython.notebook.save_checkpoint();'))
        cs = ContainerSetter(nb_working_file_path)

        candidate_paths = [path_config.DOT_GITIGNORE, path_config.DATA_GOVERNANCE]
        git_path = []
        path_msg = ''
        for path in candidate_paths:
            git_path.append(os.path.join(cs._abs_root_path, path))
            path_msg += f'・ {path}<br>'
        commit_message = msg_config.get('commit_message', 'setup')
        msg = f"""### 以下の内容で同期します
<hr>
同期対象のパス<br>
{path_msg}

コミットメッセージ<br>
・{commit_message}
"""

        alert = pn.pane.Alert(msg ,sizing_mode="stretch_width",alert_type='info')
        display(alert)
        return git_path, commit_message

    @classmethod
    def sync(cls, nb_working_file_path:str, git_path:list[str], commit_message:str):
        pn.extension()
        """Gin_forkに実行結果を同期するメソッドです。

        Args:
            nb_working_file_path (str): 実行Notebookパス
            git_path(list[str]):Gitのパス
            commit_message(str):コミットメッセージ
        """
        cs = ContainerSetter(nb_working_file_path)

        gin.syncs_with_repo(
            cwd=cs._abs_root_path,
            git_path=git_path,
            gitannex_path= [],
            gitannex_files=[],
            message=commit_message,
            get_paths=[]
            )

    @classmethod
    def check_imcomplete_auth(cls):
        """ユーザーの認証が完了しているかを確認するメソッドです。

        Raises:
            Exception: 認証が完了していない
        """
        if not gin.exist_user_info():
            alert = pn.pane.Alert(msg_config.get('user_auth', 'imcomplete_auth'),sizing_mode="stretch_width",alert_type='warning')
            display(alert)
            raise Exception('Authentication not completed')



    @classmethod
    def return_main_menu(cls,nb_working_file_path:str):
        """メインメニューに戻るためのメソッドです。

        Args:
            nb_working_file_path (str): 実行Notebookパス
        """
        pn.extension()
        cs = ContainerSetter(nb_working_file_path)
        cs.display_main_menu(cs.nb_working_file_path)
