
import os
import traceback

import panel as pn
from IPython.display import display

from ..task_director import TaskDirector
from ..subflow.subflow import get_subflow_type_and_id
from ..utils.widgets import Button, MessageBox
from ..utils.package import MakePackage
from ..utils.config import path_config, message as msg_config
from ..utils.field_config import Field


# 本ファイルのファイル名
script_file_name = os.path.splitext(os.path.basename(__file__))[0]
notebook_name = script_file_name+'.ipynb'

DEFAULT_WIDTH = 600

class ExperimentPackageMaker(TaskDirector):

    def __init__(self, working_path:str) -> None:
        """ExperimentPackageMaker コンストラクタ

        Args:
            working_path (str): [実行Notebookファイルパス]
        """
        super().__init__(working_path, notebook_name)
        self.make_package = MakePackage()

        # フォームボックス
        self._form_box = pn.WidgetBox()
        self._form_box.width = 900
        # メッセージ用ボックス
        self._msg_output = MessageBox()
        self._msg_output.width = 900

    def set_field_selector(self):
        self._form_box.clear()

        self.field = Field()
        options = dict()
        self.feild_list_default = {
            msg_config.get('form', 'selector_default'): False
        }
        options.update(self.feild_list_default)
        options.update(self.field.get_id_and_name())
        self.feild_list = pn.widgets.Select(
                options=options,
                disabled_options=self.field.get_disabled_ids(),
                value = False
            )
        self.feild_list.param.watch(self._field_select_callback, 'value')
        self.save_form_box.append(self.feild_list)

    def _field_select_callback(self, event):
        self.select_id = self.feild_list.value
        if not self.select_id:
            self.template_path_form.clear()
        # デフォルトを選択不可に
        disabled_options = self.feild_list.disabled_options
        if False not in disabled_options:
            disabled_options.append(self.feild_list_default)
            self.feild_list.disabled_options = disabled_options

        self.set_template_form()

    def set_template_form(self):
        # テンプレート利用要否
        options = {
            "利用する": True,
            "利用しない": False
        }
        self.radio = pn.widgets.RadioBoxGroup(options=options, value=True,inline=True, name='テンプレートを利用するかどうか')
        self.radio.param.watch(self._radiobox_callback)
        self._form_box.append(self.radio)
        # パス入力欄
        self.template_path_form = pn.widgets.TextInput(name="cookiecutter template path", width=DEFAULT_WIDTH, disabled=True)
        self.template_path_form.value_input = self.field.get_template_path(self.select_id)
        self._form_box.append(self.template_path_form)
        # 実行ボタン
        self.submit_button = Button(width=DEFAULT_WIDTH)
        self.submit_button.set_looks_init()
        self.submit_button.on_click(self.callback_submit_template_form)

        self._form_box.append(self.submit_button)

    def _radiobox_callback(self, event):
        radio_value = self.radio.value

        if radio_value:
            self.template_path_form.value_input = self.field.get_template_path(self.select_id)
            self.template_path_form.disabled = True
        else:
            self.template_path_form.disabled = False
            self.template_path_form.value_input = ""

    @TaskDirector.callback_form("get_cookiecutter_template")
    def callback_submit_template_form(self, event):
        self.submit_button.set_looks_processing()
        template = self.template_path_form.value_input

        if not template:
            self.submit_button.set_looks_warning("値が入力されていません")
            return

        try:
            context = self.make_package.get_template(template)
        except Exception:
            message = f'## [INTERNAL ERROR] : {traceback.format_exc()}'
            self._msg_output.update_error(message)
            self.log.error(message)
            return
        else:
            self.set_context_form(context)

    def set_context_form(self, context):
        self._form_box.clear()
        self._msg_output.clear()
        self.create_context_form(context)
        self.submit_button = Button(width=DEFAULT_WIDTH)
        self.submit_button.set_looks_init()
        self.submit_button.on_click(self.callback_submit_context_form)
        self._form_box.append(self.submit_button)

    def create_context_form(self, context):
        for key, raw in context.items():
            title = key
            if isinstance(raw, list):
                obj = pn.widgets.Select(name=title, options=raw, width=DEFAULT_WIDTH)
            elif isinstance(raw, bool):
                obj = pn.widgets.RadioBoxGroup(name=title, options=['yes', 'no', ], inline=True, width=DEFAULT_WIDTH)
                if raw:
                    obj.value = 'yes'
                else:
                    obj.value = 'no'
            elif isinstance(raw, dict):
                continue
            else:
                obj = pn.widgets.TextInput(name=title, value=raw, width=DEFAULT_WIDTH)

            self._form_box.append(obj)

    @TaskDirector.callback_form("create_package")
    def callback_submit_context_form(self, event):
        self.submit_button.set_looks_processing()
        context_dict = {}
        for obj in self._form_box.objects:
            if isinstance(obj, pn.widgets.Button):
                continue
            if obj.value:
                context_dict[obj.name] = obj.value
            else:
                self._msg_output.update_error(f'{obj.name} is empty.')
                return

        subflow_type, subflow_id = get_subflow_type_and_id(self.nb_working_file_path)
        if subflow_id is None:
            self._msg_output.update_error(f'## [INTERNAL ERROR] : don\'t get subflow id')
            return
        self.output_dir = os.path.join(self._abs_root_path, "data", subflow_type, subflow_id)
        try:
            self.make_package.create_package(
                context_dict=context_dict,
                output_dir=self.output_dir
            )
        except Exception:
            message = f'## [INTERNAL ERROR] : {traceback.format_exc()}'
            self._msg_output.update_error(message)
            self.log.error(message)
            return

        self._form_box.clear()
        self._msg_output.update_success(f'実験パッケージを{self.output_dir}に作成しました。')

    @TaskDirector.task_cell("1")
    def generateFormScetion(self):
        # タスク開始によるサブフローステータス管理JSONの更新
        self.doing_task(script_file_name)

        # フォーム定義
        self.set_field_selector()

        # フォーム表示
        pn.extension()
        form_section = pn.WidgetBox()
        form_section.append(self._form_box)
        form_section.append(self._msg_output)
        display(form_section)


    TaskDirector.task_cell("2")
    def completed_task(self):
        # フォーム定義
        source = self.output_dir
        self.define_save_form(source, script_file_name)
        # フォーム表示
        pn.extension()
        form_section = pn.WidgetBox()
        form_section.append(self.save_form_box)
        form_section.append(self.save_msg_output)
        display(form_section)
