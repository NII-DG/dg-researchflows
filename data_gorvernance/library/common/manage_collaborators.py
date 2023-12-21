
import os
import traceback
from requests.exceptions import RequestException

import panel as pn
import pandas as pd
from IPython.display import display

from ..task_director import TaskDirector
from ..utils.widgets import Button, MessageBox
from ..utils.config import path_config, message as msg_config
from ..utils.error import InputWarning, UnauthorizedError
from ..utils.storage_provider import grdm
from ..utils.checker import StringManager


# 本ファイルのファイル名
script_file_name = os.path.splitext(os.path.basename(__file__))[0]
notebook_name = script_file_name+'.ipynb'

class CollaboratorManager(TaskDirector):

    def __init__(self, working_path:str) -> None:
        super().__init__(working_path, notebook_name)

        # フォームボックス
        self._form_box = pn.WidgetBox()
        self._form_box.width = 900
        # メッセージ用ボックス
        self._msg_output = MessageBox()
        self._msg_output.width = 900

        self.show_col = ShowCollaborator(self._form_box, self._msg_output)

    @TaskDirector.task_cell("1")
    def generateFormScetion(self):
        # タスク開始によるサブフローステータス管理JSONの更新
        self.doing_task(script_file_name)

        # フォーム定義
        self.show_col.define_form()
        self.show_col.set_submit_button_callback(self.show_collaborator_callback)
        # フォーム表示
        pn.extension()
        form_section = pn.WidgetBox()
        form_section.append(self._form_box)
        form_section.append(self._msg_output)
        display(form_section)


    @TaskDirector.callback_form("show_collaborator")
    def show_collaborator_callback(self, event):
        self.show_col.submit_button.set_looks_processing()
        try:
            self.show_col.get_collaborators()
        except InputWarning as e:
            self.log.warning(str(e))
            return
        except RequestException as e:
            self.log.error(str(e))
            return
        except Exception:
            message = f'## [INTERNAL ERROR] : {traceback.format_exc()}'
            self.show_col.submit_button.set_looks_error(msg_config.get('prepare_data', 'submit'))
            self._msg_output.update_error(message)
            self.log.error(message)
            return

        # タスク実行の完了情報を該当サブフローステータス管理JSONに書き込む
        self.done_task(script_file_name)


class ShowCollaborator:

    def __init__(self, form_box, message_box:MessageBox) -> None:
        self._form_box = form_box
        self._msg_output = message_box

        self.project_id = grdm.get_project_id()
        # define widgets
        self.token_form = pn.widgets.PasswordInput(
            name=msg_config.get('form', 'token_title'),
            width=600
        )
        self.project_form = pn.widgets.TextInput(name="Project ID", width=600)
        self.submit_button = Button(width=600)

    def define_form(self):
        # display
        self._form_box.append(self.token_form)
        if not self.project_id:
            self._form_box.append(self.project_form)
        self.submit_button.set_looks_init()
        self._form_box.append(self.submit_button)

    def set_submit_button_callback(self, func):
        self.submit_button.on_click(func)

    def get_collaborators(self):
        """メイン処理"""
        token = self.token_form.value_input

        try:
            # token
            token = StringManager.strip(token, remove_empty=True)
            if not token:
                raise InputWarning(msg_config.get('save', 'empty_warning'))
            if StringManager.has_whitespace(token):
                raise InputWarning(msg_config.get('form', 'token_invalid'))
            # priject id
            if not self.project_id:
                project_id = self.project_form.value_input
                project_id = StringManager.strip(project_id)
                if StringManager.is_empty(project_id):
                    message = msg_config.get('form', 'none_input_value').format("Project ID")
                self.project_id = project_id
        except InputWarning as e:
            self.submit_button.set_looks_warning(str(e))
            raise

        try:
            contents = grdm.get_collaborator_list(grdm.SCHEME, grdm.DOMAIN, token, self.project_id)
        except UnauthorizedError:
            message = msg_config.get('form', 'token_unauthorized')
            self.submit_button.set_looks_warning(message)
            raise InputWarning(message)
        except RequestException:
            message = msg_config.get('save', 'connection_error')
            self.submit_button.set_looks_error(message)
            raise
        except Exception:
            message = msg_config.get('DEFAULT', 'unexpected_error')
            self.submit_button.set_looks_error(message)
            raise

        self.display_table(contents)


    def display_table(self, contents:dict):
        display_permission = {
                "admin": msg_config.get('manage_collaborators', 'admin'),
                "write": msg_config.get('manage_collaborators', 'write'),
                "read": msg_config.get('manage_collaborators', 'read')
            }

        name_list = []
        permission_list = []
        for full_name, permission in contents.items():
            name_list.append(full_name)
            permission_list.append(display_permission[permission])

        df = pd.DataFrame({
            msg_config.get('manage_collaborators', 'name_title'): name_list,
            msg_config.get('manage_collaborators', 'permission_title'): permission_list
        })
        self._form_box.clear()
        table = pn.pane.DataFrame(df, index=False)
        self._form_box.append(table)

