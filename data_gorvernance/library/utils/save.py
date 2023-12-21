import os
import traceback
from requests.exceptions import RequestException

import panel as pn

from .config import path_config, message as msg_config
from .widgets import Button, MessageBox
from .storage_provider import grdm
from .time import TimeDiff
from .log import TaskLog
from .error import UnauthorizedError
from .checker import StringManager


def all_sync_path(abs_root):
    paths = []

    # /home/jovyan/data
    paths.append(os.path.join(abs_root, path_config.DATA))
    # 暫定処置
    os.makedirs(os.path.join(abs_root, path_config.DATA), exist_ok=True)

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

        # メッセージ出力
        self.save_msg_output = MessageBox()
        self.save_msg_output.width = 900

        # フォーム用ボックス
        self.save_form_box = pn.WidgetBox()
        self.save_form_box.width = 900
        # 入力フォーム
        self._save_form = pn.widgets.PasswordInput(name="GRDM Token", width=600)
        self.save_form_box.append(self._save_form)
        # 確定ボタン
        self._save_submit_button = Button(width=600)
        self._save_submit_button.set_looks_init()
        self._save_submit_button.on_click(self._token_form_callback)
        self.save_form_box.append(self._save_submit_button)

    def define_save_form(self, source, script_file_name):
        """source is str or list."""

        # validate source path
        if isinstance(source, str):
            source = [source]
        if not isinstance(source, list):
            raise TypeError
        self._source = source

        # config
        self._script_file_name = script_file_name

    @TaskLog.callback_form("input_token")
    def _token_form_callback(self, event):
        self.save_msg_output.clear()
        self._save_submit_button.set_looks_processing()

        token = self._save_form.value_input
        token = StringManager.strip(token, remove_empty=True)
        if not self._validate_token(token):
            return
        self.grdm_token = token

        project_id = grdm.get_project_id()
        if project_id:
            self.project_id = project_id
            self._save()
        else:
            # grdmから起動しない場合（開発用）
            self._project_id_form()

    def _validate_token(self, token):
        if not token:
            message = msg_config.get('save', 'empty_warning')
            self.log.warning(message)
            self._save_submit_button.set_looks_warning(message)
            return False
        if StringManager.has_whitespace(token):
            message = msg_config.get('form', 'token_invalid')
            self.log.warning(message)
            self._save_submit_button.set_looks_warning(message)
            return False

        try:
            grdm.get_projects_list(
                grdm.SCHEME, grdm.DOMAIN, token
            )
        except UnauthorizedError:
            message = msg_config.get('form', 'token_unauthorized')
            self.log.warning(message)
            self._save_submit_button.set_looks_warning(message)
            return False
        except RequestException:
            message = msg_config.get('save', 'connection_error')
            self.log.error(message)
            self._save_submit_button.set_looks_error(message)
            return False
        except Exception:
            message = msg_config.get('DEFAULT', 'unexpected_error')
            self.log.error(message)
            self._save_submit_button.set_looks_error(message)
            return False

        return True

    def _project_id_form(self):
        self.save_msg_output.clear()
        projects = grdm.get_projects_list(
            grdm.SCHEME, grdm.DOMAIN, self.grdm_token
        )

        options =  dict()
        options[msg_config.get('form', 'selector_default')] = False
        for id, name in projects.items():
            options[name] = id

        self.save_form_box.clear()

        self._save_form = pn.widgets.Select(options=options, value=False)
        self._save_form.param.watch(self._project_select_callback, 'value')
        self.save_form_box.append(self._save_form)

        self._save_submit_button = Button(width=600)
        self._save_submit_button.set_looks_init()
        self._save_submit_button.on_click(self._id_form_callback)
        self.save_form_box.append(self._save_submit_button)
        self._save_submit_button.disabled = True

    def _project_select_callback(self, event):
        # NOTE: 一度値を格納してからでないと上手く動かない
        value = self._save_form.value
        if value:
            self._save_submit_button.disabled = False
        else:
            self._save_submit_button.disabled = True

    @TaskLog.callback_form("select_grdm_project")
    def _id_form_callback(self, event):
        value = self._save_form.value
        if not value:
            message = msg_config.get('form', 'select_warning')
            self._save_submit_button.set_looks_warning("message")
            self.log.warning(message)
            return
        self.project_id = value
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
                    token=self.grdm_token,
                    base_url=grdm.BASE_URL,
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