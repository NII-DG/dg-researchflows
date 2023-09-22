import os
import traceback
from typing import Any, List
import panel as pn
from panel.widgets import Checkbox
from IPython.display import display, Javascript
from pathlib import Path
import json

from ..utils.config import path_config, message as msg_config
from ..subflow.status import StatusFile, SubflowStatus, TaskStatus
from ..subflow.subflow import get_return_sub_flow_menu_relative_url_path
from ..utils.html.button import create_button
from ..task_director import TaskDirector
from ..utils.dg_customize_config import get_dg_customize_config

script_file_name = os.path.splitext(os.path.basename(__file__))[0]
script_dir_path = os.path.dirname(__file__)
p = Path(script_dir_path)
# DGカスタマイズJSON定義書パス(data_gorvernance\library\data\data_governance_customize.json)
data_governance_customize_file = p.joinpath('..', 'data/data_governance_customize.json').resolve()



class DGPlaner(TaskDirector):
    """フェーズ：研究準備、タスク：研究データ管理計画を立てるのコントローラークラス"""

    def __init__(self, working_path:str) -> None:
        # working_path = .data_gorvernance/researchflow/plan/task/plan/make_research_data_management_plan.ipynbが想定値
        super().__init__(working_path)

        # α設定JSON定義書(plan.json)
        # 想定値：data_gorvernance\researchflow\plan\plan.json
        self._plan_path =  os.path.join(self._abs_root_path, path_config.PLAN_FILE_PATH)

        # フォームボックス
        self._form_box = pn.WidgetBox()
        self._form_box.width = 900
        # メッセージ用ボックス
        self._msg_output = pn.WidgetBox()
        self._msg_output.width = 900

    def define_form(self):
        """フォーム定義"""
        # α設定チェックボックスリスト
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

    def get_plan_data(self)->dict:
        plan_path = Path(self._plan_path)
        with plan_path.open('r') as file:
            return json.loads(file.read())

    def update_plan_data(self, data:dict):
        plan_path = Path(self._plan_path)
        with plan_path.open('w') as file:
            file.write(json.dumps(data, indent=4))

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
            registration_msg = f'## {msg_config.get("form", "registration_content")}'

            registration_msg = f"""### {msg_config.get("form", "registration_content")}

<hr>

{registration_content}
            """
            self._msg_output.clear()
            alert = pn.pane.Alert(registration_msg, sizing_mode="stretch_width",alert_type='info')
            self._msg_output.append(alert)

        except Exception as e:
            self._msg_output.clear()
            alert = pn.pane.Alert(f'## [INTERNAL ERROR] : {traceback.format_exc()}',sizing_mode="stretch_width",alert_type='danger')
            self._msg_output.append(alert)

    def get_msg_disable_or_able(self, b:bool)->str:
        if b:
            return msg_config.get('DEFAULT', 'able')
        else:
            return msg_config.get('DEFAULT', 'disable')

    def get_data_governance_customize_id_by_index(self, index)->str:
        ids = self.get_data_governance_customize_ids()
        return ids[index]

    def get_data_governance_customize_data(self)->List[dict]:
        with data_governance_customize_file.open('r') as file:
            data_governance_customize_data = json.loads(file.read())
            return data_governance_customize_data['dg_customize']

    def get_data_governance_customize_ids(self)->List:
        return [p['id'] for p in self.get_data_governance_customize_data()]

    def get_disable_task_ids_on_phase(self)->dict[str, list[str]]:
        """無効化（非表示：任意タスク）のタスクIDをフェーズごとに集計する"""
        # α設定JSON定義書の設定値を取得
        plan_data = self.get_plan_data()
        # DGカスタマイズ定義データを取得する
        dg_customize_config = get_dg_customize_config()

        # 無効化タスクIDデータ
        disable_task_ids_on_phase:dict[str, list[str]] = {}
        # 無効化タスクIDデータの初期化
        for phase in dg_customize_config[0]._customize:
            if phase._subflow_type_name != 'plan':
                disable_task_ids_on_phase[phase._subflow_type_name] = []
            else:
                continue

        # DGカスタマイズプロパティの設定値とDGカスタマイズJSONデータから無効にするタスクIDを取得する
        for plan_property in plan_data['governance_plan']:
            if plan_property['is_enabled'] == False:
                # 無効なDGカスタマイズプロパティ（α項目）のIDを取得する
                alpha_id = plan_property['id']
                for alpha_config in dg_customize_config:
                    if alpha_config._id == alpha_id:
                        # DGカスタマイズプロパティ（α項目）のIDとDGカスタマイズ定義データIDが一致しているのみ処理
                        for subflow_rule in alpha_config._customize:
                            if subflow_rule._subflow_type_name != 'plan':
                                disable_task_ids_on_phase[subflow_rule._subflow_type_name].extend(subflow_rule._task_ids)

        return disable_task_ids_on_phase

    # def get_disable_task_ids_on_phase(self)->dict[str, list[str]]:
    #     """無効化（非表示：任意タスク）のタスクIDをフェーズごとに集計する"""

    #     # α設定JSON定義書の設定値を取得
    #     plan_data:dict[str, list[dict]] = self.get_plan_data()

    #     # DGカスタマイズJSONデータを取得する
    #     data_governance_customize_data = self.get_data_governance_customize_data()


    #     # 無効化タスクIDデータ
    #     disable_task_ids_on_phase:dict[str, list[str]] = {}
    #     # 無効化タスクIDデータの初期化
    #     for phase in data_governance_customize_data[0]['customize'].keys():
    #         if phase != 'plan':
    #             disable_task_ids_on_phase[phase] = []
    #         else:
    #             continue


    #     # DGカスタマイズプロパティの設定値とDGカスタマイズJSONデータから無効にするタスクIDを取得する
    #     for plan_property in plan_data['governance_plan']:
    #         if plan_property['is_enabled'] == False:
    #             # 無効なDGカスタマイズプロパティ（α項目）のIDを取得する
    #             alpha_id = plan_property['id']
    #             for customize_rule_set in data_governance_customize_data:
    #                 if customize_rule_set['id'] == alpha_id:
    #                     customize_rule:dict = customize_rule_set['customize']
    #                     for phase, rule in customize_rule.items():
    #                         if phase != 'plan':
    #                             disable_task_ids_on_phase[phase].extend(rule['task_ids'])
    #                         else:
    #                             continue
    #                 else:
    #                     continue
    #         else:
    #             continue

    #     return disable_task_ids_on_phase

    def disable_task_by_phase(self):
        disable_task_ids_data = self.get_disable_task_ids_on_phase()
        for phase, disable_task_ids in disable_task_ids_data.items():
            # data_gorvernance\base\subflow\<フェーズ>\status.jsonを更新する。
            status_path = os.path.join(self._abs_root_path, path_config.get_base_subflow_pahse_status_file_path(phase))

            sf = StatusFile(status_path)
            sub_flow_status:SubflowStatus = sf.read()
            for task in sub_flow_status._tasks:
                if task.id in disable_task_ids and not task.is_required:
                    # 無効化タスクIDリストに標的タスクIDが含まれ、かつ必須タスクではない場合、disabledを真にする
                    task.disable = True
            sf.write(sub_flow_status)


    @classmethod
    def generateFormScetion(cls, working_path:str):
        """フォームセクション用"""

        task_director = DGPlaner(working_path)
        # タスク開始による研究準備のサブフローステータス管理JSONの更新
        task_director.doing_task(script_file_name)

        # フォーム定義
        task_director.define_form()

        # フォーム表示
        pn.extension()
        form_section = pn.WidgetBox()
        form_section.append(task_director._form_box)
        form_section.append(task_director._msg_output)
        display(form_section)



    @classmethod
    def customize_research_flow(cls, working_path:str):
        task_director = DGPlaner(working_path)
        # タスクの無効化処理
        task_director.disable_task_by_phase()

    @classmethod
    def completed_task(cls, working_path:str):

        task_director = DGPlaner(working_path)
        # タスク実行の完了情報を研究準備のサブフローステータス管理JSONに書き込む
        task_director.done_task(script_file_name)

    @classmethod
    def return_subflow_menu(cls, working_path:str):
        sub_flow_menu_relative_url = get_return_sub_flow_menu_relative_url_path(working_path)
        sub_flow_menu_link_button = pn.pane.HTML()
        sub_flow_menu_link_button.object = create_button(
            url=sub_flow_menu_relative_url,
            msg=msg_config.get('task', 'retun_sub_flow_menu'),
            button_width='500px'
        )
        sub_flow_menu_link_button.width = 500
        display(sub_flow_menu_link_button)
        display(Javascript('IPython.notebook.save_checkpoint();'))
