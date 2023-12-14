import os
import traceback

import panel as pn
from IPython.display import display

from ..task_director import TaskDirector
from ..utils.widgets import Button, MessageBox
from ..utils.config import path_config, message as msg_config
from ..utils.error import InputWarning


# 本ファイルのファイル名
script_file_name = os.path.splitext(os.path.basename(__file__))[0]
notebook_name = script_file_name+'.ipynb'

class DataPreparer(TaskDirector):

    def __init__(self, working_path:str) -> None:
        """ExperimentEnvBuilder コンストラクタ

        Args:
            working_path (str): [実行Notebookファイルパス]
        """
        super().__init__(working_path, notebook_name)

        # フォームボックス
        self._form_box = pn.WidgetBox()
        self._form_box.width = 900
        # メッセージ用ボックス
        self._msg_output = MessageBox()
        self._msg_output.width = 900

        self.aws_pre = AWSPreparer(self._form_box, self._msg_output)

    @TaskDirector.task_cell("1")
    def from_AWS(self):
        # タスク開始によるサブフローステータス管理JSONの更新
        self.doing_task(script_file_name)

        # フォーム定義
        self.aws_pre.define_aws_form()
        self.aws_pre.set_submit_button_callback(self.aws_callback)
        # フォーム表示
        pn.extension()
        form_section = pn.WidgetBox()
        form_section.append(self._form_box)
        form_section.append(self._msg_output)
        display(form_section)

    @TaskDirector.callback_form("aws_preparer")
    def aws_callback(self, event):
        self.aws_pre.submit_button.set_looks_processing()
        try:
            self.aws_pre.get_data()

        except InputWarning as e:
            self.log.warning(e)
            return
        except Exception:
            message = f'## [INTERNAL ERROR] : {traceback.format_exc()}'
            self._msg_output.update_error(message)
            self.log.error(message)
            return


    @TaskDirector.task_cell("2")
    def from_github(self):
        # タスク開始によるサブフローステータス管理JSONの更新
        self.doing_task(script_file_name)

        # フォーム定義
        # フォーム表示
        pn.extension()
        form_section = pn.WidgetBox()
        form_section.append(self._form_box)
        form_section.append(self._msg_output)
        display(form_section)


    TaskDirector.task_cell("3")
    def completed_task(self):
        # フォーム定義
        source = []
        self.define_save_form(source, script_file_name)
        # フォーム表示
        pn.extension()
        form_section = pn.WidgetBox()
        form_section.append(self.save_form_box)
        form_section.append(self.save_msg_output)
        display(form_section)


class AWSPreparer():

    def __init__(self, form_box, message_box) -> None:
        self._form_box = form_box
        self._msg_output = message_box

        self.submit_button = Button()

    def define_aws_form(self):
        # define widgets
        self.access_key_form = pn.widgets.PasswordInput(
            name="アクセスキー",
            width=600,
            max_length=20
        )
        self.secret_key_form = pn.widgets.PasswordInput(
            name="シークレットキー",
            width=600,
            max_length=40
        )
        self.bucket_form = pn.widgets.TextInput(
            name="バケット",
            width=600,
            max_length=63
        )
        self.aws_path_form = pn.widgets.TextInput(
            name="転送元データパス（AWS）",
            width=600
        )
        self.local_path_form = pn.widgets.TextInput(
            width=400
        )
        self.submit_button.width = 600
        self.submit_button.set_looks_init("実行")
        # display
        self._form_box.append(self.access_key_form)
        self._form_box.append(self.secret_key_form)
        self._form_box.append(self.bucket_form)
        self._form_box.append(self.aws_path_form)
        self._form_box.append('### 転送先')
        row = pn.Row(f"{os.environ['HOME']}", self.local_path_form)
        self._form_box.append(row)

    def set_submit_button_callback(self, func):
        self.submit_button.on_click(func)

    def get_data(self):
        access_key = self.access_key_form.value_input
        secret_key = self.secret_key_form.value_input
        bucket_name = self.bucket_form.value_input
        aws_path = self.aws_path_form.value_input
        local_path = self.local_path_form.value_input

        try:
            # アクセスキー
            if len(access_key) < 1:
                raise InputWarning
            if len(access_key) < 20:
                raise InputWarning
            # シークレットキー
            if len(secret_key) < 1:
                raise InputWarning
            if len(secret_key) < 40:
                raise InputWarning
            # バケット名
            if len(bucket_name) < 1:
                raise InputWarning
            if len(bucket_name) < 3:
                raise InputWarning
            # 転送元データパス（AWS）
            if len(aws_path) < 1:
                raise InputWarning
            # 転送先
            if len(local_path) < 1:
                raise InputWarning

        except InputWarning as e:
            self.submit_button.set_looks_warning(e)
            raise