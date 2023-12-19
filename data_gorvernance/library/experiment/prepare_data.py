import os
import traceback
import re

import panel as pn
from IPython.display import display
from botocore.exceptions import ClientError

from ..task_director import TaskDirector
from ..utils.widgets import Button, MessageBox
from ..utils.config import path_config, message as msg_config
from ..utils.error import InputWarning
from ..utils.checker import StringManager
from ..utils.storage_provider import AWS
from ..utils.setting import get_data_dir


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
        self.data_dir = get_data_dir(self.nb_working_file_path)

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
        self.aws_pre.define_aws_form(self.data_dir)
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
        self._msg_output.clear()
        try:
            self.aws_pre.get_data()

        except InputWarning as e:
            self.log.warning(str(e))
            return
        except Exception:
            message = f'## [INTERNAL ERROR] : {traceback.format_exc()}'
            self.aws_pre.submit_button.set_looks_error(msg_config.get('prepare_data', 'submit'))
            self._msg_output.update_error(message)
            self.log.error(message)
            return

        self._form_box.clear()
        self._msg_output.update_success(msg_config.get('prepare_data', 'success'))


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

    def __init__(self, form_box, message_box:MessageBox) -> None:
        self._form_box = form_box
        self._msg_output = message_box

        # define widgets
        self.access_key_title = msg_config.get('prepare_data', 'access_key_title')
        self.access_key_form = pn.widgets.PasswordInput(
            name=self.access_key_title,
            width=600,
            max_length=20
        )
        self.secret_key_title = msg_config.get('prepare_data', 'secret_key_title')
        self.secret_key_form = pn.widgets.PasswordInput(
            name=self.secret_key_title,
            width=600,
            max_length=40
        )
        self.bucket_title = msg_config.get('prepare_data', 'bucket_title')
        self.bucket_form = pn.widgets.TextInput(
            name=self.bucket_title,
            width=600,
            max_length=63
        )
        self.aws_path_title = msg_config.get('prepare_data', 'aws_path_title')
        self.aws_path_form = pn.widgets.TextInput(
            name=self.aws_path_title,
            width=600
        )
        self.local_path_title = msg_config.get('prepare_data', 'local_path_title')
        self.local_path_form = pn.widgets.TextInput(
            width=400,
            margin=(0, 10)
        )
        self.submit_button = Button()
        self.submit_button.width = 600
        self.submit_button.set_looks_init(msg_config.get('prepare_data', 'submit'))

    def define_aws_form(self, data_dir: str):
        home_path = os.environ['HOME']
        if not home_path.endswith("/"):
            home_path += "/"
        data_dir = data_dir.replace(home_path, '')
        if not data_dir.endswith("/"):
            data_dir += "/"
        self.local_path_form.value = data_dir
        self.local_path_form.value_input = data_dir
        # display
        self._form_box.append(self.access_key_form)
        self._form_box.append(self.secret_key_form)
        self._form_box.append(self.bucket_form)
        self._form_box.append(self.aws_path_form)
        title = pn.pane.Markdown(self.local_path_title, margin=(0, 10))
        path_text = pn.pane.Markdown(f"{home_path}", margin=(0, 0, 0, 5))
        widgets = pn.Column(title, pn.Row(path_text, self.local_path_form, margin=(0, 10)))
        self._form_box.append(widgets)
        self._form_box.append(self.submit_button)

    def set_submit_button_callback(self, func):
        self.submit_button.on_click(func)

    def get_data(self):
        access_key = self.access_key_form.value_input
        secret_key = self.secret_key_form.value_input
        bucket_name = self.bucket_form.value_input
        aws_path = self.aws_path_form.value_input
        local_path = self.local_path_form.value_input

        requred_msg = msg_config.get('prepare_data', 'required_format')
        invalid_msg = msg_config.get('prepare_data', 'invalid_format')

        try:
            # アクセスキー
            access_key = StringManager.strip(access_key, remove_empty=False)
            if StringManager.is_empty(access_key):
                raise InputWarning(requred_msg.format(self.access_key_title))
            if len(access_key) != 20:
                raise InputWarning(invalid_msg.format(self.access_key_title))
            if StringManager.has_whitespace(access_key):
                raise InputWarning(invalid_msg.format(self.access_key_title))
            # シークレットキー
            secret_key = StringManager.strip(secret_key, remove_empty=False)
            if StringManager.is_empty(secret_key):
                raise InputWarning(requred_msg.format(self.secret_key_title))
            if len(secret_key) != 40:
                raise InputWarning(invalid_msg.format(self.secret_key_title))
            if StringManager.has_whitespace(secret_key):
                raise InputWarning(invalid_msg.format(self.secret_key_title))
            # バケット名
            bucket_name = StringManager.strip(bucket_name)
            if StringManager.is_empty(bucket_name):
                raise InputWarning(requred_msg.format(self.bucket_title))
            if not re.fullmatch(r'^[a-z0-9][a-z0-9\.-]{1,61}[a-z0-9]$', bucket_name):
                # 以下の条件を満たさない場合エラー
                #   3文字以上63文字以下
                #   小文字・数字・ドット・ハイフンのみ
                #   先頭と末尾は小文字か数字のみ
                raise InputWarning(invalid_msg.format(self.bucket_title))
            if re.search(r'\.{2,}', bucket_name):
                # ドットが連続する場合エラー
                raise InputWarning(invalid_msg.format(self.bucket_title))
            # 転送元データパス（AWS）
            aws_path = StringManager.strip(aws_path)
            if StringManager.is_empty(aws_path):
                raise InputWarning(requred_msg.format(self.aws_path_title))
            # 転送先
            local_path = StringManager.strip(local_path)
            if StringManager.is_empty(local_path):
                raise InputWarning(requred_msg.format(self.aws_path_title))

            if aws_path.endswith("/") != local_path.endswith("/"):
                self._msg_output.update_warning(msg_config.get('prepare_data', 'path_warning'))
                raise InputWarning(msg_config.get('prepare_data', 'invalid'))

        except InputWarning as e:
            self.submit_button.set_looks_warning(str(e))
            raise

        local_path = os.path.join(os.environ['HOME'], local_path)
        try:
            AWS.download(access_key, secret_key, bucket_name, aws_path, local_path)
        except FileExistsError as e:
            # 転送先が既に存在する
            self._msg_output.update_warning(msg_config.get('prepare_data', 'local_path_exist'))
            self.submit_button.set_looks_warning(invalid_msg.format(self.local_path_title))
            raise InputWarning(str(e))
        except FileNotFoundError as e:
            # 転送元が存在しない
            self._msg_output.update_warning(msg_config.get('prepare_data', 'aws_file_not_found'))
            self.submit_button.set_looks_warning(invalid_msg.format(self.aws_path_title))
            raise InputWarning(str(e))
        except ClientError as e:
            if e.response["ResponseMetadata"]["HTTPStatusCode"] == 403:
                # アクセスキーかシークレットキーが間違っている
                self._msg_output.update_warning(msg_config.get('prepare_data', 'aws_unauthorized'))
                self.submit_button.set_looks_warning(msg_config.get('prepare_data', 'invalid'))
                raise InputWarning(str(e))
            elif e.response['Error']['Code'] == 'NoSuchBucket':
                # バケットが存在しない
                self._msg_output.update_warning(msg_config.get('prepare_data', 'bucket_not_found'))
                self.submit_button.set_looks_warning(invalid_msg.format(self.bucket_title))
                raise InputWarning(str(e))
            else:
                raise