""" タスクを保存するモジュールです。"""
import os
import traceback
from typing import Any, Union

from IPython.display import clear_output
import panel as pn
from requests.exceptions import RequestException

from library.utils.config import connect as con_config
from .config import path_config, message as msg_config
from .error import UnusableVault, ProjectNotExist, UnauthorizedError, RepoPermissionError
from .input import get_grdm_connection_parameters
from .log import TaskLog
from .storage_provider import grdm
from .time_tracker import TimeDiff
from .widgets import Button, MessageBox


def all_sync_path(abs_root: str) -> list:
    """ 指定されたホームディレクトリから特定のディレクトリのパスを返す関数です。

    Args:
        abs_root (str): 絶対パスのホームディレクトリを設定します。

    Returns:
        list: ホームディレクトリからdataと、data_governanceのworking以外のパスのリストを返す。

    """
    paths = []

    # /home/jovyan/data
    paths.append(os.path.join(abs_root, path_config.DATA))

    # /home/jovyan/data_gorvernance配下のworking以外
    dg_dir = os.path.join(abs_root, path_config.DATA_GOVERNANCE)
    contents = os.listdir(dg_dir)
    contents.remove(path_config.WORKING)
    paths.extend([os.path.join(dg_dir, con) for con in contents])

    return paths


class TaskSave(TaskLog):
    """ タスクを保存するクラスです。

    Attributes:
        instance:
            _abs_root_path(str): 実行ファイルの絶対パス
            save_msg_output(MessageBox): メッセージ出力
            save_form_box(WidgetBox): フォーム用ボックス
            _save_submit_button(Button): 確定ボタン
            grdm_url(str): GRDMのURL

    """

    def __init__(self, nb_working_file_path: str, notebook_name: str) -> None:
        """ クラスのインスタンスの初期化処理を実行するメソッドです。

        Args:
            nb_working_file_path (str): 実行Notebookのファイルパスを設定します。
            notebook_name (str): 実行Notebookのファイル名を設定します。

        """
        super().__init__(nb_working_file_path, notebook_name)
        self._abs_root_path = path_config.get_abs_root_form_working_dg_file_path(nb_working_file_path)

        # メッセージ出力
        self.save_msg_output = MessageBox()
        self.save_msg_output.width = 900

        # フォーム用ボックス
        self.save_form_box = pn.WidgetBox()
        self.save_form_box.width = 900
        # 確定ボタン
        self._save_submit_button = Button(width=500)
        self.grdm_url = con_config.get('GRDM', 'BASE_URL')

    def get_grdm_params(self) -> tuple[str, str]:
        """ GRDMのトークンとプロジェクトIDを取得するメソッドです。

        Returns:
            str: GRDMのトークンを返す。
            str: プロジェクトIDを返す。

        """
        token = ""
        project_id = ""
        try:
            token, project_id = get_grdm_connection_parameters(self.grdm_url)
        except UnusableVault:
            message = msg_config.get('form', 'no_vault')
            self.save_msg_output.update_error(message)
            self.log.error(f'{message}\n{traceback.format_exc()}')
        except RepoPermissionError:
            message = msg_config.get('form', 'insufficient_permission')
            self.save_msg_output.update_error(message)
            self.log.error(f'{message}\n{traceback.format_exc()}')
        except ProjectNotExist as e:
            self.save_msg_output.update_error(str(e))
            self.log.error(traceback.format_exc())
        except RequestException as e:
            message = msg_config.get('DEFAULT', 'connection_error')
            self.save_msg_output.update_error(f'{message}\n{str(e)}')
            self.log.error(f'{message}\n{traceback.format_exc()}')
        except Exception:
            message = f'## [INTERNAL ERROR] : {traceback.format_exc()}'
            self.save_msg_output.update_error(message)
            self.log.error(message)
        return token, project_id

    async def define_save_form(self, source: Union[str, list[str]]) -> None:
        """ GRDMに保存するフォームを作成するメソッドです。

        Args:
            source (Union[str, list[str]]): 保存するファイルを設定します。

        Raises:
            TypeError: sourceがstrまたはlistでない

        """

        # validate source path
        if isinstance(source, str):
            source = [source]
        if not isinstance(source, list):
            raise TypeError
        self._source = source

        # config
        self.token, self.project_id = self.get_grdm_params()
        clear_output()

        # define form
        if not self.save_msg_output.has_message():
            self._save_submit_button.set_looks_init(msg_config.get('save', 'submit'))
            self._save_submit_button.on_click(self._handle_click)
            self.save_form_box.append(self._save_submit_button)

    async def _handle_click(self, event):
        self.log.error(f'実行されたhandle\n{traceback.format_exc()}')
        await self._save_submit_callback(event)

    @TaskLog.callback_form("input_token")
    async def _save_submit_callback(self, event: Any) -> None:
        """ ボタン押下時に保存するメソッドです。

        Args:
            event (Any): ボタンクリックイベントを設定します。

        """
        await self._save()

    async def _save(self) -> None:
        """ 保存を実行するメソッドです。"""
        size = len(self._source)
        timediff = TimeDiff()

        # start
        self.save_form_box.clear()
        msg = msg_config.get('save', 'doing')
        timediff.start()
        grdm_connect = grdm.Grdm()

        try:
            for i, path in enumerate(self._source):
                self.save_msg_output.update_info(f'{msg} {i+1}/{size}')
                await grdm_connect.sync(
                    token=self.token,
                    base_url=self.grdm_url,
                    project_id=self.project_id,
                    abs_source=path,
                    abs_root=self._abs_root_path
                )
        except UnauthorizedError:
            message = msg_config.get('form', 'token_unauthorized')
            self.save_msg_output.update_warning(message)
            self.log.warning(f'{message}\n{traceback.format_exc()}')
            return
        except RequestException as e:
            timediff.end()
            minutes, seconds = timediff.get_diff_minute()
            error_summary = traceback.format_exception_only(type(e), e)[0].rstrip('\\n')
            error_msg = msg_config.get('save', 'connection_error') + "\n" + error_summary
            self.log.error(f'{error_msg}\n{traceback.format_exc()}')
            self.save_msg_output.add_error(f'経過時間: {minutes}m {seconds}s\n {error_msg}')
            return
        except Exception as e:
            timediff.end()
            minutes, seconds = timediff.get_diff_minute()
            error_summary = traceback.format_exception_only(type(e), e)[0].rstrip('\\n')
            error_msg = f'## [INTERNAL ERROR] : {error_summary}\n{traceback.format_exc()}'
            self.save_msg_output.add_error(f'経過時間: {minutes}m {seconds}s\n {error_msg}')
            self.log.error(f'{error_msg}\n{traceback.format_exc()}')
            return
        # end
        timediff.end()
        minutes, seconds = timediff.get_diff_minute()
        message = msg_config.get('save', 'success')
        self.save_msg_output.update_success(f'{message}（{minutes}m {seconds}s）')
