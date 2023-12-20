import os
import traceback
import webbrowser

import panel as pn
from IPython.display import display
from IPython.core.display import Javascript

from ..task_director import TaskDirector, get_subflow_type_and_id, get_return_sub_flow_menu_relative_url_path
from ..utils.widgets import Button, MessageBox
from ..utils.package import MakePackage, OutputDirExistsException
from ..utils.config import path_config, message as msg_config
from ..utils.setting import ocs_template, ResearchFlowStatusOperater
from ..utils.html.button import create_button

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
        self._template_form_box.clear()

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
        try:
            self.selected = self.field_list.value
            self.set_templatelink_form()  
        except Exception:
            message = f'## [INTERNAL ERROR] : {traceback.format_exc()}'
            self._msg_output.update_error( message )
            return
        
    def set_templatelink_form(self):
        try:
            #pn.extension()
            self._msg_output.clear()
            #self._form_box.clear()
            self._template_form_box.clear()

            self.ConstructionProcedureId = self.ocs_template.get_id(self.selected)
            self.template_path = self.ocs_template.get_template_path(self.selected)

            if self.ConstructionProcedureId == "T001":
                # 解析基盤をそのまま利用
                self._msg_output.update_success( msg_config.get('select_ocs_template', 'use_computing_service'))

            elif self.ConstructionProcedureId == "T999":
                # ポータブル版VCCを利用して構築する。
                message = msg_config.get('select_ocs_template', 'use_portable_vcc') \
                            + '\n' \
                            + msg_config.get('select_ocs_template', 'success') 

                #self._msg_output.update_success( message )
                self.template_link = self.template_path
                
                # メッセージを作成
                #message = pn.pane.Markdown("## これはメッセージです")

                # ボタンを作成
                #button = pn.widgets.Button(name='Click me!', button_type='primary')

                md = pn.pane.Markdown( message )
                self._template_form_box.extend(
                    pn.Column( md,self.get_ocs_template_button_object() )
                )
                self._form_box.append(self._template_form_box)
                self._msg_output.update_success( self.template_link )
            else:
                # OCSテンプレートを利用して構築する。
                message = msg_config.get('select_ocs_template', 'use_ocs_template') \
                            + '<br>' \
                            + msg_config.get('select_ocs_template', 'success') 

                #self._msg_output.update_success( message )

                relative_url = "../../../../.."
                self.template_link = relative_url + "/working/researchflow/plan/task/plan/ocs-templates/" + self.template_path
                self._msg_output.update_success( self.template_link )
                md = pn.pane.Markdown( message )
                self._template_form_box.extend(
                    pn.Column( md,self.get_ocs_template_button_object() )
                )
                self._form_box.append(self._template_form_box)
                
            #if self.template_link:
            #    self.field_list = pn.widgets.Button(
            #        name=msg_config.get('select_ocs_template', 'go_template_link'),
            #        button_type='primary',
            #        width=600
            #    )
            #    self._template_form_box.append(self.field_list)

            #self.return_ocs_template_button()

            # ボタンを作成

            #button.on_click( webbrowser.open('http://www.google.com') )
            #button.servable()
            #display(self.ocs_template_link_button)
            #display(Javascript('IPython.notebook.save_checkpoint();'))
            
        except Exception:
            message = f'## [INTERNAL ERROR] : {traceback.format_exc()}'
            #message = f' selected ={ print(self.selected)} ConstructionProcedureId = {print(self.ConstructionProcedureId)} template_path = {print(self.template_path)}'
            self._msg_output.update_error( message )
            return

    #########################
    #  ocs-template link    #
    #########################
    def get_ocs_template_button_object(self)-> pn.pane.HTML:
        """OCS-Templateへのボタンpanel.HTMLオブジェクトの取得
        Returns:
            [panel.pane.HTML]: [HTMLオブジェクト]
        """
        button_width = 500
        ocs_template_link_button = pn.pane.HTML()
        ocs_template_link_button.object = create_button(
            url=self.template_link,
            msg=msg_config.get('select_ocs_template', 'go_template_link'),
            target='_blank',
            button_width=f'{button_width}px'
        )
        ocs_template_link_button.width = button_width
        return ocs_template_link_button

    # ここではログを吐かない
    def return_ocs_template_button(self):
        pn.extension()
        #self.ocs_template_link_button  = self.get_ocs_template_button_object()
        # メッセージを作成
        message = pn.pane.Markdown("## これはメッセージです")

        # ボタンを作成
        button = pn.widgets.Button(name=msg_config.get('select_ocs_template', 'go_template_link'), button_type='primary')
        button.on_click( webbrowser.open('http://www.google.com') )

        # メッセージとボタンを同時に表示
        pn.Column(message, button).servable()

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
