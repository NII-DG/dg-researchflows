import os
from typing import Any, List
import panel as pn
from panel.widgets import Checkbox
from IPython.display import display, Javascript
from pathlib import Path
import json

from ..utils.config import path_config, message as msg_config
from ..subflow.status import StatusFile, SubflowStatus, TaskStatus

script_file_name = os.path.splitext(os.path.basename(__file__))[0]
script_dir_path = os.path.dirname(__file__)
p = Path(script_dir_path)
# DGカスタマイズJSON定義書パス(data_gorvernance\library\data\data_governance_customize.json)
data_governance_customize_file = p.joinpath('..', 'data/data_governance_customize.json').resolve()



class DGPlaner():
    """フェーズ：研究準備、タスク：研究データ管理計画を立てるのコントローラークラス"""

    def __init__(self, working_path:str) -> None:
        # working_path = .data_gorvernance/researchflow/plan/task/plan/make_research_data_management_plan.ipynbが想定値

        # 絶対rootディレクトリを取得する
        self._abs_root_path = path_config.get_abs_root_form_working_dg_file_path(working_path)

        # 研究準備のサブフローステータス管理JSONパス
        # 想定値：data_gorvernance\researchflow\plan\status.json
        self._plan_sub_flow_status_file_path = os.path.join(self._abs_root_path, path_config.PLAN_TASK_STATUS_FILE_PATH)

        # α設定JSON定義書(plan.json)
        # 想定値：data_gorvernance\researchflow\plan\plan.json
        self._plan_path =  os.path.join(self._abs_root_path, path_config.PLAN_FILE_PATH)

        # フォームボックス
        self._form_box = pn.WidgetBox()
        self._form_box.width = 900
        # エラーメッセージ用ボックス
        self._err_output = pn.WidgetBox()
        self._err_output.width = 900

    def define_form(self):
        """フォーム定義"""
        # DGカスタマイズプロパティチェックボックスリスト
        self._checkbox_list = pn.Column()
        for id in self.get_data_governance_customize_ids():
            check_book = pn.widgets.Checkbox(name=msg_config.get('data_governance_customize_property', id))
            self._checkbox_list.append(check_book)
        self.submit_button = pn.widgets.Button(name=msg_config.get('form', 'submit_button'))
        self.submit_button.on_click(self.callback_submit_input)
        # フォームボックスを更新
        self.update_form_box(
            title=msg_config.get('plan', 'form_title_set_data_governance_customize_property'), objects=[self._checkbox_list, self.submit_button]
        )


    def update_form_box(self, title:str, objects:List[Any]):
        self._form_box.clear()
        self._form_box.append(f'## {title}')
        for object in objects:
            self._form_box.append(object)

    def callback_submit_input(self, event):
        # 適応するDGカスタマイズプロパティの設定値をplan.json(data_gorvernance\researchflow\plan\plan.json)に記録する。
        plan_path = Path(self._plan_path)

        with plan_path.open('r') as file:
            plan_file = json.loads(file.read())

        for index, cb in enumerate(self._checkbox_list):
            if type(cb) is Checkbox:
                plan_file['governance_plan'][index]['is_enabled'] = cb.value
            else:
                self._err_output.clear()
                alert = pn.pane.Alert(f'## [INTERNAL ERROR] : cb variable is not panel.widgets.Checkbox',sizing_mode="stretch_width",alert_type='danger')
                self._err_output.append(alert)

        with plan_path.open('w') as file:
            file.write(json.dumps(plan_file, indent=4))



    def get_data_governance_customize_id_by_index(self, index)->str:
        ids = self.get_data_governance_customize_ids()
        return ids[index]











    def get_data_governance_customize_data(self)->List[dict]:
        with data_governance_customize_file.open('r') as file:
            data_governance_customize_data = json.loads(file.read())
            return data_governance_customize_data['dg_customize']

    def get_data_governance_customize_ids(self)->List:
        return [p['id'] for p in self.get_data_governance_customize_data()]





    @classmethod
    def generateFormScetion(cls, working_path:str):
        dg_planer = DGPlaner(working_path)
        """フォームセクション用"""
        # 研究準備のサブフローステータス管理JSONの更新
        sf = StatusFile(dg_planer._plan_sub_flow_status_file_path)
        plan_status: SubflowStatus = sf.read()
        for task in plan_status.tasks:
            if task.name == script_file_name:
                # 更新タスク情報（make_research_data_management_plan）
                ## status を実行中ステータスへ更新
                task.status = TaskStatus.STATUS_DOING
                ## 実行環境IDを記録
                execution_environment_id = os.environ["JUPYTERHUB_SERVER_NAME"]
                task.add_execution_environments(execution_environment_id)
            else:
                continue
        # 更新内容を記録する。
        sf.write(plan_status)

        # フォーム定義



        # フォーム表示
        pn.extension()
        form_section = pn.WidgetBox()
        form_section.append(dg_planer._form_box)
        form_section.append(dg_planer._err_output)
        display(form_section)
