import os
import traceback
from typing import Any, List
from pathlib import Path
import json

import panel as pn
from IPython.display import display

from ..task_director import TaskDirector, get_subflow_type_and_id
from ..utils.widgets import Button, MessageBox
from ..utils.package import MakePackage
from ..utils.config import path_config, message as msg_config
from ..utils.setting import ocs_template, ResearchFlowStatusOperater


# 本ファイルのファイル名
script_file_name = os.path.splitext(os.path.basename(__file__))[0]
notebook_name = script_file_name+'.ipynb'

script_dir_path = os.path.dirname(__file__)
p = Path(script_dir_path)
# DGカスタマイズJSON定義書パス(data_gorvernance\library\data\data_governance_customize.json)
data_governance_customize_file = p.joinpath('..', 'data/data_governance_customize.json').resolve()

DEFAULT_WIDTH = 600

class ExperimentEnvBuilder(TaskDirector):

    def __init__(self, working_path:str) -> None:
        """ExperimentPackageMaker コンストラクタ

        Args:
            working_path (str): [実行Notebookファイルパス]
        """
        super().__init__(working_path, notebook_name)
        self.make_package = MakePackage()

        # α設定JSON定義書(plan.json)
        # 想定値：data_gorvernance\researchflow\plan\plan.json
        self._plan_path =  os.path.join(self._abs_root_path, path_config.PLAN_FILE_PATH)

        # フォームボックス
        self._form_box = pn.WidgetBox()
        self._form_box.width = 900
        
        # 可変フォームボックス
        self._template_form_box = pn.WidgetBox()
        self._template_form_box.width = 900

        # メッセージ用ボックス
        self._msg_output = MessageBox()
        self._msg_output.width = 900
 
    def set_ocs_template_selector(self):
        self._form_box.clear()

        self.ocs_template = ocs_template()
        options = []
        self.field_list_default = msg_config.get('form', 'selector_default')

        options.append(self.field_list_default)
        options.extend(self.ocs_template.get_name())

        self.field_list = pn.widgets.Select(
                name=msg_config.get('select_ocs_template', 'ocs_template_title'),
                options=options,
                disabled_options=self.field.get_disabled_ids(),
                value=self.field_list_default
            )

        self.field_list.param.watch(self._ocs_template_select_callback, 'value')
        self._form_box.append(self.field_list)


    def _ocs_template_select_callback(self, event):
        self.selected = self.ocs_template_list.value
        self._template_form_box.clear()
        self._msg_output.clear()

        if self.selected == self.ocs_template_list_default:
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
        self.radio.param.watch(self._radiobox_callback, 'value')
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

        # NOTE: この位置ならば無効化される
        self.radio.param.trigger('value')

    def get_data_governance_customize_id_by_index(self, index)->str:
        ids = self.get_data_governance_customize_ids()
        return ids[index]

    def get_data_governance_customize_data(self)->List[dict]:
        with data_governance_customize_file.open('r') as file:
            data_governance_customize_data = json.loads(file.read())
            return data_governance_customize_data['dg_customize']

    def get_data_governance_customize_ids(self)->List:
        return [p['id'] for p in self.get_data_governance_customize_data()]

    def change_submit_button_init(self, name):
        self.submit_button.name = name
        self.submit_button.button_type = 'primary'
        self.submit_button.button_style = 'solid'
        self.submit_button.icon = 'settings-plus'

    def callback_submit_input(self, event):
        try:
            # 適応するDGカスタマイズプロパティの設定値をα設定JSON定義書(data_gorvernance\researchflow\plan\plan.json)に記録する。
            plan_data = self.get_plan_data()

            registration_content = ''
            for index, cb in enumerate(self._checkbox_list):
                if type(cb) is Checkbox and type(cb.value) is bool:
                    plan_data['governance_plan'][index]['is_enabled'] = cb.value
                    governance_plan_id = plan_data['governance_plan'][index]['id']
                    registration_content += f'{msg_config.get("data_governance_customize_property", governance_plan_id)} : {self.get_msg_disable_or_able(cb.value)}<br>'
                else:
                    raise Exception('cb variable is not panel.widgets.Checkbox or cb value is not bool type')

            self.update_plan_data(plan_data)

            # 登録内容を出力する
            registration_msg = f"""### {msg_config.get("form", "registration_content")}

<hr>

{registration_content}
            """
            self._msg_output.clear()
            alert = pn.pane.Alert(registration_msg, sizing_mode="stretch_width",alert_type='info')
            self._msg_output.append(alert)
            self.change_submit_button_success(msg_config.get('form', 'accepted'))

        except Exception as e:
            self._msg_output.clear()
            alert = pn.pane.Alert(f'## [INTERNAL ERROR] : {traceback.format_exc()}',sizing_mode="stretch_width",alert_type='danger')
            self._msg_output.append(alert)


    @TaskDirector.task_cell("1")
    def generateFormScetion(self):
        # タスク開始によるサブフローステータス管理JSONの更新
        self.doing_task(script_file_name)

        # フォーム定義
        self.set_ocs_template_selector()

        # フォーム表示
        pn.extension()
        form_section = pn.WidgetBox()
        form_section.append(self._form_box)
        form_section.append(self._msg_output)
        display(form_section)

    TaskDirector.task_cell("2")
    def completed_task(self):
        # タスク実行の完了情報を該当サブフローステータス管理JSONに書き込む
        self.done_task(script_file_name)
