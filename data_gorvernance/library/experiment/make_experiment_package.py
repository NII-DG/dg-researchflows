
import os
import traceback

import panel as pn
from IPython.display import display

from ..task_director import TaskDirector
from ..subflow.subflow import get_subflow_type_and_id
from ..utils.widgets import Button
from ..utils.package import MakePackage
from ..utils.config import path_config, message as msg_config


# 本ファイルのファイル名
script_file_name = os.path.splitext(os.path.basename(__file__))[0]

DEFAULT_WIDTH = 600

class ExperimentPackageMaker(TaskDirector):

    def __init__(self, nb_working_file_path:str) -> None:
        """ExperimentPackageMaker コンストラクタ

        Args:
            nb_working_file_path (str): [実行Notebookファイルパス]
        """
        super().__init__(nb_working_file_path)
        self.make_package = MakePackage()

        # フォームボックス
        self._form_box = pn.WidgetBox()
        self._form_box.width = 900
        # メッセージ用ボックス
        self._msg_output = pn.WidgetBox()
        self._msg_output.width = 900

    def set_template_form(self):
        self._form_box.clear()
        self.template_path_form = pn.widgets.TextInput(name="cookiecutter template path", width=DEFAULT_WIDTH)
        self._form_box.append(self.template_path_form)
        self.submit_button = Button(width=DEFAULT_WIDTH)
        self.submit_button.set_looks_init()
        self.submit_button.on_click(self.callback_submit_template_form)
        self._form_box.append(self.submit_button)

    def callback_submit_template_form(self, event):
        self.submit_button.set_looks_processing("処理中")
        template = self.template_path_form.value_input

        try:
            context = self.make_package.get_template(template)
        except Exception:
            self._msg_output.clear()
            alert = pn.pane.Alert(f'## [INTERNAL ERROR] : {traceback.format_exc()}',sizing_mode="stretch_width",alert_type='danger')
            self._msg_output.append(alert)
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
        self.submit_button.set_looks_processing("処理中")
        for key, raw in context:
            title = key
            if isinstance(raw, list):
                obj = pn.widgets.Select(name=title, options=raw, width=DEFAULT_WIDTH)
            elif isinstance(raw, bool):
                obj = pn.widgets.RadioBoxGroup(name=title, options=['yes', 'no', ], inline=True, , width=DEFAULT_WIDTH)
                if raw:
                    obj.value = 'yes'
                else:
                    obj.value = 'no'
            elif isinstance(raw, dict):
                continue
            else:
                obj = pn.widgets.TextInput(name=title, value=raw, width=DEFAULT_WIDTH)

            self._form_box.append(obj)


    def callback_submit_context_form(self, event):
        context_dict = {}
        for obj in self._form_box.objects:
            if obj.value:
                context_dict[obj.name] = obj.value
            else:
                self._msg_output.clear()
                alert = pn.pane.Alert(f'{obj.name} is empty.',sizing_mode="stretch_width",alert_type='danger')
                self._msg_output.append(alert)
                return

        subflow_type, subflow_id = get_subflow_type_and_id(self.nb_working_file_path)
        if subflow_id is None:
            self._msg_output.clear()
            alert = pn.pane.Alert(f'## [INTERNAL ERROR] : don\'t get subflow id',sizing_mode="stretch_width",alert_type='danger')
            self._msg_output.append(alert)
            return
        output_dir = os.path.join(self._abs_root_path, path_config.DG_RESEARCHFLOW_FOLDER, subflow_type, subflow_id, "data")
        self.make_package.create_package(
            context_dict=context_dict,
            output_dir=output_dir
        )
        self._msg_output.clear()
        alert = pn.pane.Alert(f'実験パッケージを{output_dir}に作成しました。',sizing_mode="stretch_width",alert_type='info')
        self._msg_output.append(alert)

    @classmethod
    def generateFormScetion(cls, working_path:str):
        task_director = ExperimentPackageMaker(working_path)
        # タスク開始によるサブフローステータス管理JSONの更新
        task_director.doing_task(script_file_name)

        # フォーム定義
        task_director.set_template_form()

        # フォーム表示
        pn.extension()
        form_section = pn.WidgetBox()
        form_section.append(task_director._form_box)
        form_section.append(task_director._msg_output)
        display(form_section)


    @classmethod
    def completed_task(cls, working_path:str):
        # タスク実行の完了情報を該当サブフローステータス管理JSONに書き込む
        task_director = ExperimentPackageMaker(working_path)
        task_director.done_task(script_file_name)
