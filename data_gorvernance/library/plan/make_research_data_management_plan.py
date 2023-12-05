import os
import traceback
from typing import Any, List
from pathlib import Path
import json

import panel as pn
from panel.widgets import Checkbox
from IPython.display import display

from ..utils.config import path_config, message as msg_config
from ..task_director import TaskDirector
from ..utils.setting import get_dg_customize_config, SubflowStatusFile, SubflowStatus
from ..utils.widgets import MessageBox

script_file_name = os.path.splitext(os.path.basename(__file__))[0]
notebook_name = script_file_name+'.ipynb'
script_dir_path = os.path.dirname(__file__)
p = Path(script_dir_path)
# DGカスタマイズJSON定義書パス(data_gorvernance\library\data\data_governance_customize.json)
data_governance_customize_file = p.joinpath('..', 'data/data_governance_customize.json').resolve()



class DGPlaner(TaskDirector):
    """フェーズ：研究準備、タスク：研究データ管理計画を立てるのコントローラークラス"""

    def __init__(self, working_path:str) -> None:
        # working_path = .data_gorvernance/researchflow/plan/task/plan/make_research_data_management_plan.ipynbが想定値
        super().__init__(working_path, notebook_name)

        # α設定JSON定義書(plan.json)
        # 想定値：data_gorvernance\researchflow\plan\plan.json
        self._plan_path =  os.path.join(self._abs_root_path, path_config.PLAN_FILE_PATH)

    @TaskDirector.task_cell("1")
    def get_dmp(self):
        # タスク開始による研究準備のサブフローステータス管理JSONの更新
        self.doing_task(script_file_name)

        # フォーム定義

        # フォーム表示
        pn.extension()
        form_section = pn.WidgetBox()
        display(form_section)


    @TaskDirector.task_cell("2")
    def generateFormScetion(self):
        """フォームセクション用"""

        # フォーム定義
        dg_customize = DGCustomizeSetter(self.nb_working_file_path)
        dg_customize.define_form()

        # フォーム表示
        pn.extension()
        form_section = pn.WidgetBox()
        form_section.append(dg_customize._form_box)
        form_section.append(dg_customize._msg_output)
        display(form_section)

    @TaskDirector.task_cell("3")
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


class DMPGetter(TaskDirector):

    def __init__(self, working_path:str) -> None:
        # working_path = .data_gorvernance/researchflow/plan/task/plan/make_research_data_management_plan.ipynbが想定値
        super().__init__(working_path, notebook_name)

        # フォームボックス
        self._form_box = pn.WidgetBox()
        self._form_box.width = 900
        # メッセージ用ボックス
        self._msg_output = MessageBox()
        self._msg_output.width = 900





class DGCustomizeSetter(TaskDirector):

    def __init__(self, working_path:str) -> None:
        # working_path = .data_gorvernance/researchflow/plan/task/plan/make_research_data_management_plan.ipynbが想定値
        super().__init__(working_path, notebook_name)

        # α設定JSON定義書(plan.json)
        # 想定値：data_gorvernance\researchflow\plan\plan.json
        self._plan_path =  os.path.join(self._abs_root_path, path_config.PLAN_FILE_PATH)

        # フォームボックス
        self._form_box = pn.WidgetBox()
        self._form_box.width = 900
        # メッセージ用ボックス
        self._msg_output = MessageBox()
        self._msg_output.width = 900

    def define_form(self):
        """フォーム定義"""
        # α設定チェックボックスリスト
        self._checkbox_list = pn.Column()
        for id in self.get_data_governance_customize_ids():
            check_book = pn.widgets.Checkbox(name=msg_config.get('data_governance_customize_property', id))
            self._checkbox_list.append(check_book)
        self.submit_button = pn.widgets.Button()
        self.change_submit_button_init(name=msg_config.get('form', 'submit_select'))
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
            # タスクの無効化処理
            self.disable_task_by_phase()

            # 登録内容を出力する
            registration_msg = f"""### {msg_config.get("form", "registration_content")}

<hr>

{registration_content}
            """
            self._msg_output.clear()
            alert = pn.pane.Alert(registration_msg, sizing_mode="stretch_width",alert_type='info')
            self._msg_output.append(alert)
            self.change_submit_button_success(msg_config.get('form', 'accepted'))
            # タスク実行の完了情報を該当サブフローステータス管理JSONに書き込む
            # NOTE: 開発中の仮置き
            self.done_task(script_file_name)

        except Exception as e:
            self._msg_output.clear()
            alert = pn.pane.Alert(f'## [INTERNAL ERROR] : {traceback.format_exc()}',sizing_mode="stretch_width",alert_type='danger')
            self._msg_output.append(alert)

    def get_msg_disable_or_able(self, b:bool)->str:
        if b:
            return f'<span style="color: red; ">**{msg_config.get("DEFAULT", "able")}**</span>'
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

    def disable_task_by_phase(self):
        """各サブフローの各タスクステータスのdisabledを更新"""
        disable_task_ids_data = self.get_disable_task_ids_on_phase()
        for phase, disable_task_ids in disable_task_ids_data.items():
            # data_gorvernance\base\subflow\<フェーズ>\status.jsonを更新する。
            status_path = os.path.join(self._abs_root_path, path_config.get_base_subflow_pahse_status_file_path(phase))

            sf = SubflowStatusFile(status_path)
            sub_flow_status:SubflowStatus = sf.read()
            for task in sub_flow_status._tasks:
                if task.id in disable_task_ids and not task.is_required:
                    # 無効化タスクIDリストに標的タスクIDが含まれ、かつ必須タスクではない場合、disabledを真にする
                    task.disable = True
                else:
                    task.disable = False
            sf.write(sub_flow_status)


    def change_submit_button_init(self, name):
        self.submit_button.name = name
        self.submit_button.button_type = 'primary'
        self.submit_button.button_style = 'solid'
        self.submit_button.icon = 'settings-plus'

    def change_submit_button_processing(self, name):
        self.submit_button.name = name
        self.submit_button.button_type = 'primary'
        self.submit_button.button_style = 'outline'

    def change_submit_button_success(self, name):
        self.submit_button.name = name
        self.submit_button.button_type = 'success'
        self.submit_button.button_style = 'solid'

    def change_submit_button_warning(self, name):
        self.submit_button.name = name
        self.submit_button.button_type = 'warning'
        self.submit_button.button_style = 'solid'

    def change_submit_button_error(self, name):
        self.submit_button.name = name
        self.submit_button.button_type = 'danger'
        self.submit_button.button_style = 'solid'
