import os
import traceback
from typing import Any, List
from pathlib import Path
import json
from requests.exceptions import RequestException

import panel as pn
from panel.widgets import Checkbox
from IPython.display import display

from ..utils.config import path_config, message as msg_config
from ..task_director import TaskDirector
from ..utils.setting import get_dg_customize_config, SubflowStatusFile, SubflowStatus, DMPManager
from ..utils.widgets import MessageBox, Button, Alert
from ..utils.storage_provider import grdm
from ..utils.error import MetadataNotExist, UnauthorizedError

script_file_name = os.path.splitext(os.path.basename(__file__))[0]
notebook_name = script_file_name+'.ipynb'
script_dir_path = os.path.dirname(__file__)
p = Path(script_dir_path)
# DGカスタマイズJSON定義書パス(data_gorvernance\library\data\data_governance_customize.json)
data_governance_customize_file = p.joinpath('..', 'data/data_governance_customize.json').resolve()
# dmp.json(data_gorvernance\researchflow\plan\dmp.json)
dmp_file = p.joinpath('../../researchflow/plan/dmp.json').resolve()


class DGPlaner(TaskDirector):
    """フェーズ：研究準備、タスク：研究データ管理計画を立てるのコントローラークラス"""

    def __init__(self, working_path:str) -> None:
        # working_path = .data_gorvernance/researchflow/plan/task/plan/make_research_data_management_plan.ipynbが想定値
        super().__init__(working_path, notebook_name)

        # α設定JSON定義書(plan.json)
        # 想定値：data_gorvernance\researchflow\plan\plan.json
        self._plan_path =  os.path.join(self._abs_root_path, path_config.PLAN_FILE_PATH)

        self.dmp_getter = DMPGetter(dmp_file)

    @TaskDirector.task_cell("1")
    def get_dmp(self):
        # タスク開始による研究準備のサブフローステータス管理JSONの更新
        self.doing_task(script_file_name)

        # フォーム定義
        self.dmp_getter.define_form()
        self.dmp_getter.set_get_dmp_button_callback(self._token_callback)
        self.dmp_getter.set_dmp_select_button_callback(self._dmp_select_callback)

        # フォーム表示
        pn.extension()
        form_section = pn.WidgetBox()
        form_section.append(self.dmp_getter.form_box)
        form_section.append(self.dmp_getter.msg_output)
        display(form_section)

    @TaskDirector.callback_form('get_dmp')
    def _token_callback(self, event):
        """dmpを取得する"""
        is_ok, message = self.dmp_getter.validate_token_form()
        if not is_ok:
            self.log.warning(message)
            return

        try:
            self.dmp_getter.get_project_metadata(
                scheme=grdm.SCHEME,
                domain=grdm.DOMAIN
            )
        except UnauthorizedError:
            message = msg_config.get('form', 'token_unauthorized')
            self.log.warning(message)
            self.dmp_getter.get_dmp_button.set_looks_warning(message)
            return
        except MetadataNotExist:
            message = msg_config.get('make_research_data_management_plan', 'metadata_not_exist')
            self.log.warning(message)
            self.dmp_getter.form_box.clear()
            self.dmp_getter.msg_output.update_warning(message)
            return
        except RequestException:
            message = msg_config.get('DEFAULT', 'connection_error')
            self.log.error(message)
            self.dmp_getter.get_dmp_button.set_looks_error(message)
            return
        except Exception:
            message = msg_config.get('DEFAULT', 'unexpected_error')
            self.log.error(message)
            self.dmp_getter.get_dmp_button.set_looks_error(message)
            return

        self.dmp_getter.make_select_dmp_form()

    @TaskDirector.callback_form('selected_dmp')
    def _dmp_select_callback(self, event):
        is_ok, index = self.dmp_getter.validate_dmp_selector()
        if not is_ok:
            message = msg_config.get('form', 'select_warning')
            self._save_submit_button.set_looks_warning("message")
            self.log.warning(message)
            return

        self.dmp_getter.register_dmp(index)


    @TaskDirector.task_cell("2")
    def generateFormScetion(self):
        """フォームセクション用"""
        # タスク開始による研究準備のサブフローステータス管理JSONの更新
        self.doing_task(script_file_name)

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


class DMPGetter():

    def __init__(self, dmp_path) -> None:
        # working_path = .data_gorvernance/researchflow/plan/task/plan/make_research_data_management_plan.ipynbが想定値
        self.dmp_file = DMPManager(dmp_path)
        self.token = ""
        self.project_id = grdm.get_project_id()
        self.metadata = {}

        # フォームボックス
        self.form_box = pn.WidgetBox()
        self.form_box.width = 900
        # メッセージ用ボックス
        self.msg_output = MessageBox()
        self.msg_output.width = 900

        # display registrated dmp
        self.display_dmp = Alert.info()
        self.make_form_button = Button(width=600)
        # get dmp form
        self.token_form = pn.widgets.TextInput(name="GRDM Token", width=600)
        self.project_form = pn.widgets.TextInput(name="Project ID", width=600)
        self.get_dmp_button = Button(width=600)
        # select dmp form
        self.dmp_selector = pn.widgets.Select(width=600)
        self.dmp_select_button = Button(width=600)

    def set_get_dmp_button_callback(self, func):
        self.get_dmp_button.on_click(func)

    def set_dmp_select_button_callback(self, func):
        self.dmp_select_button.on_click(func)

    def define_form(self):
        """セル実行時の表示を制御する"""
        if os.path.isfile(dmp_file):
            self._display_registrated_dmp()
        else:
            self._make_token_form()

    ##### display registrated dmp ######

    def _display_registrated_dmp(self):
        self.form_box.clear()
        self.msg_output.clear()

        self.make_form_button.on_click(self._make_form_button_callback)
        self.form_box.append(self.make_form_button)

        dmp = self.dmp_file.read()
        self.display_dmp.object = self.dmp_file.display_format(dmp)
        self.form_box.append(self.display_dmp)

    def _make_form_button_callback(self, event):
        self._make_token_form()

    ##### get dmp form #####

    def _make_token_form(self):
        """DMPを取得するためにトークン等を入力させる"""
        self.form_box.clear()
        self.msg_output.clear()

        self.form_box.append(self.token_form)

        if not self.project_id:
            self.form_box.append(self.project_form)

        self.get_dmp_button.set_looks_init()
        self.form_box.append(self.get_dmp_button)

    def validate_token_form(self):
        message = ""

        token = self.token_form.value_input
        if len(token) <= 0:
            message = msg_config.get('form', 'none_input_value').format("GRDM Token")
            self.get_dmp_button.set_looks_warning(message)
            return False, message
        self.token = token

        if not self.project_id:
            project_id = self.project_form.value_input
            if len(project_id) <= 0:
                message = msg_config.get('form', 'none_input_value').format("Project ID")
                self.get_dmp_button.set_looks_warning(message)
                return False, message
            self.project_id = project_id

        return True, message

    def get_project_metadata(self, scheme, domain):
        """入力されたトークンを利用してDMPを取得する"""
        if not self.token or not self.project_id:
            raise Exception(f"don't have token or project id.")
        self.dmps = grdm.get_project_metadata(scheme, domain, self.token, self.project_id)

    ##### select dmp form #####

    def make_select_dmp_form(self):
        """取得したDMPの中から任意のものを選択する"""
        self.form_box.clear()
        self.msg_output.clear()

        options = dict()
        options[msg_config.get('form', 'selector_default')] = False
        options.update(self.dmp_file.create_dmp_options(self.dmps))
        self.dmp_selector.options = options
        self.dmp_selector.size = len(options)
        self.form_box.append(self.dmp_selector)

        self.dmp_select_button.set_looks_init()
        self.form_box.append(self.dmp_select_button)

    def validate_dmp_selector(self):
        index = self.dmp_selector.value
        if not index:
            return False, index
        return True, index

    def register_dmp(self, selected_value):

        dmp = self.dmp_file.get_dmp(self.dmps, selected_value)
        self.dmp_file.write(dmp)
        self.form_box.clear()
        info = Alert.info(self.dmp_file.display_format(dmp))
        self.msg_output.update_info(info)


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
