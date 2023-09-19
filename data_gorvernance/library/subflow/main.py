import os
from pathlib import Path
from tempfile import TemporaryDirectory

import panel as pn
from IPython.display import display

from .subflow import SubFlow
from ..utils import file
from ..utils.config import path_config


class SubflowMenu:
    def __init__(self) -> None:
        pass

    def render(self, working_path: str, option=False):
        parent = Path(os.path.dirname(working_path))
        subflow_type = ''
        dir_name = file.get_next_directory(working_path, path_config.RESEARCHFLOW)
        if dir_name:
            subflow_type = dir_name
        # create path
        status_file = parent / path_config.STATUS_JSON
        diag_file = (
            Path(path_config.get_dg_sub_flow_base_data_folder())
            / subflow_type / 'flow.diag'
        )
        using_task_dir = (
            Path(path_config.get_dg_researchflow_folder(is_dot=True))
            / subflow_type / 'task'
        )
        # setup
        subflow = SubFlow(working_path, str(status_file), str(diag_file), str(using_task_dir))

        subflow.setup_tasks()

        subflow.update_status()

        pn.extension()

        with TemporaryDirectory() as workdir:
            subflow.generate(workdir)
            diagram = pn.pane.SVG(workdir)
            if option:
                selector = 
                button = pn.widgets.Button(name=name, button_type= "default")
                button.on_click(submit_callback())
                display()
            display(diagram)


    def submit_callback(self):

        def callback(event):
            pass

        return callback

