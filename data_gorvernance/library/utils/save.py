import os
import traceback
from requests.exceptions import RequestException

import panel as pn
from IPython.display import clear_output

from .config import path_config, message as msg_config
from .widgets import Button, MessageBox
from .storage_provider import grdm
from .time import TimeDiff
from .log import TaskLog
from .token import get_token, get_project_id


def all_sync_path(abs_root):
    paths = []

    # /home/jovyan/data
    paths.append(os.path.join(abs_root, path_config.DATA))

    # /home/jovyan/data_gorvernance配下のworking以外
    dg_dir = os.path.join(abs_root, path_config.DATA_GOVERNANCE)
    contents = os.listdir(dg_dir)
    contents.remove(path_config.WORKING)
    paths.extend([
        os.path.join(dg_dir, con)
        for con in contents
    ])

    return paths


class TaskSave(TaskLog):

    def __init__(self, nb_working_file_path, notebook_name) -> None:
        super().__init__(nb_working_file_path, notebook_name)
        self._abs_root_path = path_config.get_abs_root_form_working_dg_file_path(nb_working_file_path)
        self._notebook_name = notebook_name

        # メッセージ出力
        self.save_msg_output = MessageBox()
        self.save_msg_output.width = 900

        # フォーム用ボックス
        self.save_form_box = pn.WidgetBox()
        self.save_form_box.width = 900
        # 確定ボタン
        self._save_submit_button = Button(width=600)

    def define_save_form(self, source):
        """source is str or list."""

        # validate source path
        if isinstance(source, str):
            source = [source]
        if not isinstance(source, list):
            raise TypeError
        self._source = source

        # config
        self.token = get_token()
        self.project_id = get_project_id()
        clear_output()

        # define form
        self._save_submit_button.set_looks_init(msg_config.get('save', 'submit'))
        self._save_submit_button.on_click(self._save_submit_callback)
        self.save_form_box.append(self._save_submit_button)

    @TaskLog.callback_form("input_token")
    def _save_submit_callback(self, event):
        self._save()

    def _save(self):
        size = len(self._source)
        timediff = TimeDiff()

        # start
        self.save_form_box.clear()
        msg = msg_config.get('save', 'doing')
        timediff.start()

        try:
            for i, path in enumerate(self._source):
                self.save_msg_output.update_info(f'{msg} {i+1}/{size}')
                grdm.sync(
                    token=self.token,
                    base_url=grdm.API_V2_BASE_URL,
                    project_id=self.project_id,
                    abs_source = path,
                    abs_root=self._abs_root_path
                )
        except RequestException as e:
            timediff.end()
            minutes, seconds = timediff.get_diff_minute()
            error_summary = traceback.format_exception_only(type(e), e)[0].rstrip('\\n')
            error_msg = msg_config.get('save', 'connection_error') + "\n" + error_summary
            self.log.error(error_msg)
            self.save_msg_output.add_error(f'経過時間: {minutes}m {seconds}s\n {error_msg}')
            return False
        except Exception as e:
            timediff.end()
            minutes, seconds = timediff.get_diff_minute()
            error_summary = traceback.format_exception_only(type(e), e)[0].rstrip('\\n')
            error_msg = f'## [INTERNAL ERROR] : {error_summary}\n{traceback.format_exc()}'
            self.save_msg_output.add_error(f'経過時間: {minutes}m {seconds}s\n {error_msg}')
            self.log.error(error_msg)
            return
        # end
        timediff.end()
        minutes, seconds = timediff.get_diff_minute()
        message = msg_config.get('save', 'success')
        self.save_msg_output.update_success(f'{message}（{minutes}m {seconds}s）')