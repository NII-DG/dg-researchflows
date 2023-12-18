
import os
import traceback

import panel as pn
from IPython.display import display

from ..task_director import TaskDirector, get_subflow_type_and_id
from ..utils.widgets import Button, MessageBox
from ..utils.package import MakePackage, OutputDirExistsException
from ..utils.config import path_config, message as msg_config
from ..utils.setting import Field, get_data_dir
from ..utils.checker import StringManager


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

        # パッケージ作成場所
        self.output_dir = get_data_dir(working_path)

        # フォームボックス
        self._form_box = pn.WidgetBox()
        self._form_box.width = 900
        # 可変フォームボックス
        self._template_form_box = pn.WidgetBox()
        self._template_form_box.width = 900
        # メッセージ用ボックス
        self._msg_output = MessageBox()
        self._msg_output.width = 900

    def set_field_selector(self):
        self._form_box.clear()

        self.field = Field()
        options = []
        self.field_list_default = msg_config.get('form', 'selector_default')
        options.append(self.field_list_default)
        options.extend(self.field.get_name())
        self.field_list = pn.widgets.Select(
                name=msg_config.get('make_experiment_package', 'field_title'),
                options=options,
                disabled_options=self.field.get_disabled_ids(),
                value=self.field_list_default
            )
        self.field_list.param.watch(self._field_select_callback, 'value')
        self._form_box.append(self.field_list)

    def _field_select_callback(self, event):
        self.selected = self.field_list.value
        self._template_form_box.clear()
        self._msg_output.clear()

        if self.selected == self.field_list_default:
            self._msg_output.update_warning(msg_config.get('form', 'select_warning'))

        self.set_template_form()

    def set_template_form(self):
        # テンプレート利用要否
        title_format = """<label>{}</label>"""
        radio_title = msg_config.get('make_experiment_package', 'recommend_pkg_title')
        radio_title = pn.pane.HTML(title_format.format(radio_title))
        options = {
            msg_config.get('make_experiment_package', 'use'): True,
            msg_config.get('make_experiment_package', 'not_use'): False
        }
        self.radio = pn.widgets.RadioBoxGroup(options=options, value=True,inline=True, margin=(0, 0, 0, 20))
        if  not self.field.get_template_path(self.selected):
            self.radio.value = False
        else:
            self._template_form_box.extend(
                pn.Column(radio_title, self.radio)
            )

        # パス入力欄
        self.template_path_form = pn.widgets.TextInput(
            name=msg_config.get('make_experiment_package', 'set_cookiecutter_title'),
            width=DEFAULT_WIDTH
        )
        self._template_form_box.append(self.template_path_form)
        # 実行ボタン
        self.submit_button = Button(width=DEFAULT_WIDTH)
        self.submit_button.set_looks_init()
        self.submit_button.on_click(self.callback_submit_template_form)
        self._template_form_box.append(self.submit_button)

        self._form_box.append(self._template_form_box)

        # NOTE: callbackで利用するフォームが定義されてから設定する
        self.radio.param.watch(self._radiobox_callback, 'value')
        # NOTE: この位置ならば無効化される
        self.radio.param.trigger('value')

    def _radiobox_callback(self, event):
        radio_value = self.radio.value

        if radio_value:
            self.template_path_form.value = self.field.get_template_path(self.selected)
            self.template_path_form.value_input = self.field.get_template_path(self.selected)
            self.template_path_form.disabled = True
        else:
            self.template_path_form.disabled = False
            self.template_path_form.value = ""
            self.template_path_form.value_input = ""

    @TaskDirector.callback_form("get_cookiecutter_template")
    def callback_submit_template_form(self, event):
        self.submit_button.set_looks_processing()

        template = self.template_path_form.value_input

        template = StringManager.strip(template)
        if StringManager.is_empty(template):
            self.submit_button.set_looks_warning(msg_config.get('form', 'value_empty_warning'))
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
                obj = pn.widgets.RadioBoxGroup(name=title, options=['yes', 'no'], inline=True, width=DEFAULT_WIDTH)
                if raw:
                    obj.value = 'yes'
                else:
                    obj.value = 'no'
            elif isinstance(raw, dict):
                continue
            else:
                obj = pn.widgets.TextInput(name=title, value=raw, value_input=raw, width=DEFAULT_WIDTH)

            self._form_box.append(obj)

    @TaskDirector.callback_form("create_package")
    def callback_submit_context_form(self, event):
        self.submit_button.set_looks_processing()
        context_dict = {}
        for obj in self._form_box.objects:
            if isinstance(obj, pn.widgets.Button):
                continue
            value = ""
            if isinstance(obj, pn.widgets.TextInput):
                value = obj.value_input
                value = StringManager.strip(value)
                if StringManager.is_empty(value):
                    message = msg_config.get('form', 'none_input_value').format(obj.name)
                    self._msg_output.update_error(message)
                    return
            else:
                value = obj.value
            context_dict[obj.name] = value

        try:
            self.make_package.create_package(
                context_dict=context_dict,
                output_dir=self.output_dir
            )
        except OutputDirExistsException:
            message = msg_config.get('make_experiment_package', 'dir_exixts_error')
            self._msg_output.update_warning(message)
            self.submit_button.set_looks_init()
            return
        except Exception:
            message = msg_config.get('DEFAULT', 'unexpected_error')
            self.submit_button.set_looks_error(message)
            message = f'## [INTERNAL ERROR] : {traceback.format_exc()}'
            self._msg_output.update_error(message)
            self.log.error(message)
            return

        self._form_box.clear()
        message = msg_config.get('make_experiment_package', 'create_success').format(self.output_dir)
        self._msg_output.update_success(message)
        # TODO: 開発中の仮置きのため後で削除すること
        self.done_task(script_file_name)

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
