import os
from pathlib import Path
from tempfile import TemporaryDirectory

import panel as pn
from IPython.display import display

from .subflow import SubFlow
from ..utils import file
from ..utils.config import path_config, message


class SubflowMenu:
    def __init__(self) -> None:
        pass

    def render(self, working_path: str, option=False):
        # get subflow type and id from path
        subflow_type_dir, subflow_id = path_config.get_subflow_type_and_id(working_path)
        subflow_type = ''
        subflow_rel_path = Path()
        if subflow_type_dir:
            subflow_type = subflow_type_dir
            subflow_rel_path = Path(subflow_type)
            if subflow_id:
                subflow_rel_path = subflow_rel_path / subflow_id
        else:
            raise ValueError

        # create path
        parent = Path(os.path.dirname(working_path))
        status_file = parent / path_config.STATUS_JSON
        diag_file = (
            Path(path_config.DG_SUB_FLOW_BASE_DATA_FOLDER)
            / subflow_type / path_config.FLOW_DIAG
        )
        using_task_dir = (
            Path(path_config.DG_WORKING_FOLDER)
            / subflow_rel_path / path_config.TASK
        )
        root_folder = Path(path_config.get_abs_root_form_working_dg_file_path(working_path))

        # setup
        subflow = SubFlow(working_path, str(status_file), str(diag_file), str(using_task_dir))
        subflow.setup_tasks(path_config.get_dg_task_base_data_folder())
        subflow.update_status()

        # panel activation
        pn.extension()
        with TemporaryDirectory() as workdir:
            subflow.generate(
                workdir=workdir,
                font=str(root_folder / '.fonts/ipag.ttf')
            )
            diagram = pn.pane.SVG(workdir)
            if option:
                options = [
                    message.get('subflow_menu', 'select_abled_task'),
                    message.get('subflow_menu', 'select_all_task')
                ]
                selector = pn.widgets.RadioBoxGroup(options=options, value=options[0])
                button = pn.widgets.Button(
                    name=message.get('subflow_menu', 'select_button_name'),
                    button_type= "default"
                )
                button.on_click(self.submit_callback(selector, button, diagram))
                display(pn.Column(selector, button))
            display(diagram)


    def submit_callback(self, selector, button, diagram):

        def callback(event):
            pass

        return callback

