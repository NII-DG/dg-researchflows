import os
import traceback

import panel as pn
from IPython.display import display

from ..task_director import TaskDirector
from ..utils.widgets import MessageBox
from ..utils.config import path_config, message as msg_config
from ..utils.setting import OCSTemplate
from ..utils.html.button import create_button

# 本ファイルのファイル名
script_file_name = os.path.splitext(os.path.basename(__file__))[0]
notebook_name = script_file_name+'.ipynb'

DEFAULT_WIDTH = 600

class ExperimentEnvBuilder(TaskDirector):

    def __init__(self, working_path:str) -> None:
        """ExperimentEnvBuilder コンストラクタ

        Args:
            working_path (str): [実行Notebookファイルパス]
        """
        super().__init__(working_path, notebook_name)

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

        self.ocs_template = OCSTemplate()
        options = []
        options.extend(self.ocs_template.get_name())

        self.ocs_template_list = pn.widgets.Select(
                name=msg_config.get('select_ocs_template', 'ocs_template_title'),
                options=options,
                disabled_options=self.ocs_template.get_disabled_ids(),
                size=4,
                width=600
            )

        self.ocs_template_list.param.watch(self._ocs_template_select_callback, 'value')
        self._form_box.append(self.ocs_template_list)

    def _ocs_template_select_callback(self, event):
        try:
            self.selected = self.ocs_template_list.value
            self.set_templatelink_form()
        except Exception:
            message = f'## [INTERNAL ERROR] : {traceback.format_exc()}'
            self._msg_output.update_error( message )
            return

    def set_templatelink_form(self):
        try:
            self._msg_output.clear()
            self._template_form_box.clear()

            self.construction_procedure_id = self.ocs_template.get_id(self.selected)
            self.template_path = self.ocs_template.get_template_path(self.selected)

            if self.construction_procedure_id == "T001":
                # 解析基盤をそのまま利用
                md = pn.pane.Markdown( msg_config.get('select_ocs_template', 'use_computing_service') )
                self._template_form_box.extend(
                    pn.Column( md,self.get_ocs_template_button_object() )
                )
                self._form_box.append(self._template_form_box)

            elif self.construction_procedure_id == "T999":
                # ポータブル版VCCを利用して構築する。
                message = msg_config.get('select_ocs_template', 'use_portable_vcc') \
                            + '<br>' \
                            + msg_config.get('select_ocs_template', 'success')

                self.template_link = self.template_path

                md = pn.pane.Markdown( message )
                self._template_form_box.extend(
                    pn.Column( md,self.get_ocs_template_button_object() )
                )
                self._form_box.append(self._template_form_box)

            else:
                # OCSテンプレートを利用して構築する。
                message = msg_config.get('select_ocs_template', 'use_ocs_template') \
                            + '<br>' \
                            + msg_config.get('select_ocs_template', 'success')

                self.template_link =  path_config.get_ocs_template_dir() + self.template_path

                md = pn.pane.Markdown( message )
                self._template_form_box.extend(
                    pn.Column( md,self.get_ocs_template_button_object() )
                )
                self._form_box.append(self._template_form_box)

        except Exception:
            message = f'## [INTERNAL ERROR] : {traceback.format_exc()}'
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

    @TaskDirector.task_cell("1")
    def generateFormScetion(self):
        # タスク開始によるサブフローステータス管理JSONの更新
        self.doing_task()

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
        self.done_task()

        # フォーム定義
        save_target_path = os.path.join( self._abs_root_path, path_config.DATA, path_config.PLAN, "build_experiment_environment")
        source = self.get_sync_source(save_target_path)
        self.define_save_form(source)

        # フォーム表示
        pn.extension()
        form_section = pn.WidgetBox()
        form_section.append(self.save_form_box)
        form_section.append(self.save_msg_output)
        display(form_section)

    def get_sync_source(self, search_directory :str):
        source = []
        for root, dirs, files in os.walk(search_directory):
            for filename in files:
                if filename.endswith(".ipynb"):
                    path = os.path.join(root, filename)
                    source.append(path)
        return source