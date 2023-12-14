import os
import traceback

import panel as pn
from IPython.display import display

from ..task_director import TaskDirector, get_subflow_type_and_id
from ..utils.widgets import Button, MessageBox
from ..utils.package import MakePackage, OutputDirExistsException
from ..utils.config import path_config, message as msg_config
from ..utils.setting import ocs_template, ResearchFlowStatusOperater


# 本ファイルのファイル名
script_file_name = os.path.splitext(os.path.basename(__file__))[0]
notebook_name = script_file_name+'.ipynb'

DEFAULT_WIDTH = 600

class ExperimentEnvBuilder(TaskDirector):

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
        options.extend(self.ocs_template.get_name())

        self.field_list = pn.widgets.Select(
                name=msg_config.get('select_ocs_template', 'ocs_template_title'),
                options=options,
                disabled_options=self.ocs_template.get_disabled_ids(),
                size=4,
                width=600
            )

        self.field_list.param.watch(self._ocs_template_select_callback, 'value')
        self._form_box.append(self.field_list)


    def _ocs_template_select_callback(self, event):
        self.selected = self.field_list.value
        self._template_form_box.clear()
        self._msg_output.clear()
        self.set_templatelink_form()  

    def set_templatelink_form(self):

        try:

            self._msg_output.clear()
            self.ConstructionProcedureId = self.ocs_template.get_id(self.selected)
            self.template_path = self.ocs_template.get_template_path(self.selected)

            if self.ConstructionProcedureId == "T001":
                # 解析基盤をそのまま利用
                self._msg_output.update_success( msg_config.get('select_ocs_template', 'use_computing_service'))
            if self.ConstructionProcedureId == "T999":
                # ポータブル版VCCを利用して構築する。
                messsage = msg_config.get('select_ocs_template', 'use_portable_vcc')
                self._msg_output.update_success( messsage )
                self._msg_output.add_success( self.template_path )
            else:
                # OCSテンプレートを利用して構築する。
                messsage = msg_config.get('select_ocs_template', 'use_ocs_template')
                self._msg_output.update_success( messsage )
                self._msg_output.add_success( self._abs_root_path + "data_gorvernance/working/researchflow/plan/task/plan/ocs-templates" + self.template_path )
              
        except Exception:
            message = f'## [INTERNAL ERROR] : {traceback.format_exc()}'
            self._msg_output.update_error( message )
            return

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
