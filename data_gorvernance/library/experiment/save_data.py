import os

import panel as pn
from IPython.display import display

from ..task_director import TaskDirector
from ..utils.config import path_config, message as msg_config

# 本ファイルのファイル名
script_file_name = os.path.splitext(os.path.basename(__file__))[0]
notebook_name = script_file_name+'.ipynb'

DEFAULT_WIDTH = 600

class DataSaver(TaskDirector):

    def __init__(self, working_path:str) -> None:
        """DataSaver コンストラクタ

        Args:
            nb_working_file_path (str): [実行Notebookファイルパス]
        """
        super().__init__(working_path, notebook_name)

    @TaskDirector.task_cell("1")
    def generateFormScetion(self):
        # タスク開始によるサブフローステータス管理JSONの更新
        self.doing_task(script_file_name)

        # フォーム定義
        source = [
            os.path.join(self._abs_root_path, path_config.DATA_GOVERNANCE),
            os.path.join(self._abs_root_path, path_config.DATA)
        ]
        self.save_define_form(source, script_file_name)
        # フォーム表示
        pn.extension()
        form_section = pn.WidgetBox()
        form_section.append(self._save_form_box)
        form_section.append(self._msg_output)
        display(form_section)
