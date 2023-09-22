import os
from pathlib import Path
import xml.etree.ElementTree as ET
from tempfile import TemporaryDirectory

import panel as pn
from IPython.display import display, Javascript, HTML

from .subflow import SubFlow, get_subflow_type_and_id
from ..utils.config import path_config, message
from ..utils.html import button as html_button


def access_main_menu(working_path: str):
    root_folder = Path(
        path_config.get_abs_root_form_working_dg_file_path(working_path)
    )
    main_menu = root_folder / path_config.MAIN_MENU_PATH
    return display(HTML(
            html_button.create_button(
                url=str(main_menu),
                msg=message.get('subflow_menu', 'access_main_menu'),
            )
        ))


class SubflowMenu:

    def __init__(self) -> None:
        # サブフロー図
        self.diagram = pn.pane.SVG()
        # ラジオボタン
        self.selector = pn.widgets.RadioBoxGroup()
        options = [
            message.get('subflow_menu', 'select_abled_task'),
            message.get('subflow_menu', 'select_all_task')
        ]
        self.selector.options = options
        self.selector.value = options[0]
        # ボタン
        self.button = pn.widgets.Button(
            name=message.get('subflow_menu', 'select_button_name'),
            button_type= "default",
            align= 'end'
        )
        self.button.on_click(self.select_flow)
        # エラー出力
        self.error_output = pn.WidgetBox()

    def select_flow(self, event):
        pass

    def get_svg_size(self, svg_file_path: str):
        """svgの画像の横幅を返す

        Args:
            svg_file_path (str): svgファイルのパス

        Returns:
            _type_: _description_
        """
        # SVGファイルをパース
        tree = ET.parse(svg_file_path)
        root = tree.getroot()
        # <svg>要素からviewBox属性を取得
        viewbox_value = root.get('viewBox')

        viewbox_width = 0
        # viewbox_valueを解析して幅と高さを取得
        if viewbox_value:
            viewbox_parts = viewbox_value.split()
            if len(viewbox_parts) == 4:
                viewbox_width = int(viewbox_parts[2])
                viewbox_height = int(viewbox_parts[3])

        if 900 < viewbox_width:
            viewbox_width = 900
        elif viewbox_width < 200:
            viewbox_width = 200

        return viewbox_width

    @classmethod
    def render(cls, working_path: str, is_selected=False):
        parent = Path(os.path.dirname(working_path))
        root_folder = Path(
            path_config.get_abs_root_form_working_dg_file_path(working_path)
        )

        # get subflow type and id from path
        subflow_type, subflow_id = get_subflow_type_and_id(working_path)
        subflow_rel_path = Path(subflow_type)
        if subflow_id:
            subflow_rel_path = subflow_rel_path / subflow_id

        # create path
        status_file = parent / path_config.STATUS_JSON
        diag_file = (
            root_folder / path_config.DG_SUB_FLOW_BASE_DATA_FOLDER
            / subflow_type / path_config.FLOW_DIAG
        )
        using_task_dir = (
            root_folder / path_config.DG_WORKING_RESEARCHFLOW_FOLDER
            / subflow_rel_path / path_config.TASK
        )
        souce_task_dir = root_folder / path_config.DG_TASK_BASE_DATA_FOLDER

        # setup
        subflow = SubFlow(
            working_path, str(status_file), str(diag_file), str(using_task_dir)
        )
        subflow.setup_tasks(str(souce_task_dir))

        # panel activation
        pn.extension()
        subflow_menu = cls()
        if is_selected:
            display(pn.Row(subflow_menu.selector, subflow_menu.button))
        with TemporaryDirectory() as workdir:
            tmp_diag = Path(workdir) / 'skeleton.diag'
            skeleton = Path(workdir) / 'skeleton.svg'
            subflow.generate(
                svg_path=str(skeleton),
                tmp_diag=str(tmp_diag),
                font=str(root_folder / '.fonts/ipag.ttf')
            )
            subflow_menu.diagram.object = skeleton
            subflow_menu.diagram.width = subflow_menu.get_svg_size(str(skeleton))
            display(subflow_menu.diagram)
        display(Javascript('IPython.notebook.save_checkpoint();'))
