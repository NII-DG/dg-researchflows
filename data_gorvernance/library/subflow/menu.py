import os
from pathlib import Path
import xml.etree.ElementTree as ET
from tempfile import TemporaryDirectory

import panel as pn
from IPython.display import display, Javascript, HTML

from .subflow import SubFlow, get_subflow_type_and_id
from ..utils.config import path_config, message
from ..utils.html import button as html_button
from ..utils import file

def access_main_menu(working_file: str):
    root_folder = Path(
        path_config.get_abs_root_form_working_dg_file_path(working_file)
    )
    main_menu = str(root_folder / path_config.MAIN_MENU_PATH)

    link = file.relative_path(main_menu, os.path.dirname(working_file))
    display(HTML(
        html_button.create_button(
            url=f'{link}?init_nb=true',
            msg=message.get('subflow_menu', 'access_main_menu'),
        )
    ))
    display(Javascript('IPython.notebook.save_checkpoint();'))


class SubflowMenu:

    def __init__(self) -> None:

        # サブフロー図
        # SVGにするとファイルとして出してしまうのでHTMLとして埋め込む
        self.diagram = pn.pane.HTML()
        # ラジオボタン
        self.selector = pn.widgets.RadioBoxGroup()
        self.selector_options = [
            message.get('subflow_menu', 'select_abled_task'),
            message.get('subflow_menu', 'select_all_task')
        ]
        self.selector.options = self.selector_options
        self.selector.value = self.selector_options[0]
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

    def get_contents(self, svg_file_path: str):
        return file.File(svg_file_path).read()

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

    def set_diagram(self, subflow: SubFlow, root_folder: Path, display_all=False):
        with TemporaryDirectory() as workdir:
            tmp_diag = Path(workdir) / 'skeleton.diag'
            skeleton = Path(workdir) / 'skeleton.svg'
            subflow.generate(
                svg_path=str(skeleton),
                tmp_diag=str(tmp_diag),
                font=str(root_folder / '.fonts/ipag.ttf'),
                display_all=display_all
            )
            self.diagram.object = self.get_contents(str(skeleton))
            self.diagram.width = self.get_svg_size(str(skeleton))

    @classmethod
    def render(cls, working_file: str, is_selected=False):
        parent = Path(os.path.dirname(working_file))
        root_folder = Path(
            path_config.get_abs_root_form_working_dg_file_path(working_file)
        )

        # get subflow type and id from path
        subflow_type, subflow_id = get_subflow_type_and_id(working_file)
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
            str(parent), str(status_file), str(diag_file), str(using_task_dir)
        )
        subflow.setup_tasks(str(souce_task_dir))

        # panel activation
        pn.extension()
        subflow_menu = cls()
        if is_selected:
            display(pn.Row(subflow_menu.selector, subflow_menu.button))
        subflow_menu.set_diagram(subflow, root_folder)
        display(subflow_menu.diagram)
        display(Javascript('IPython.notebook.save_checkpoint();'))
