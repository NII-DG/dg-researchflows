"""サブフローメニューの表示をするモジュールです。

サブフローメニュークラスを始め、サブフロー図などの画像を表示させたり、メインメニューにアクセスするメソッドがあります。
"""
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import traceback
from typing import Callable
import xml.etree.ElementTree as ET

from IPython.core.display import Javascript
from IPython.display import display
import panel as pn

from library.task_director import get_subflow_type_and_id
from library.utils import file
from library.utils.config import path_config, message
from library.utils.html.button import create_button
from library.utils.log import TaskLog
from library.utils.widgets import MessageBox
from .subflow import SubFlowManager


def access_main_menu(working_file:str):
    """メインメニューにアクセスするメソッドです。

    Args:
        working_file (str): 実行Notebookファイルパス
    """
    root_folder = Path(
        path_config.get_abs_root_form_working_dg_file_path(working_file)
    )
    main_menu = str(root_folder / path_config.MAIN_MENU_PATH)

    link = file.relative_path(main_menu, os.path.dirname(working_file))

    main_menu_button = pn.pane.HTML()
    main_menu_button.object = create_button(
            url=f'{link}?init_nb=true',
            msg=message.get('subflow_menu', 'access_main_menu'),
            button_width='500px'
        )
    pn.extension()
    display(main_menu_button)
    display(Javascript('IPython.notebook.save_checkpoint();'))


class SubflowMenu(TaskLog):
    """サブフローメニューのクラスです。

    Attributes:
        instance:
            menu_widgetbox(pn.WidgetBox):表示するウィジェットを格納する
            diagram(pn.pane.HTML):サブフロー図を格納する
            title(pn.pane.Markdown):サブフロー図のタイトル
            diagram_widgetbox(pn.WidgetBox):サブフロー図をHTMLとして埋め込む
            working_file (str): 実行Notebookファイルパス
    """

    def __init__(self, working_file:str) -> None:
        """SubflowMenu コンストラクタのメソッドです。

        Args:
            working_file (str): 実行Notebookファイルパス
        """
        super().__init__(working_file, path_config.MENU_NOTEBOOK)

        # 表示するウィジェットを格納する
        self.menu_widgetbox = pn.WidgetBox()

        # サブフロー図
        # SVGにするとファイルとして出してしまうのでHTMLとして埋め込む
        self.diagram = pn.pane.HTML()
        # フロー図の配置
        self.title = pn.pane.Markdown()
        self.diagram_widgetbox = pn.WidgetBox(self.title, self.diagram)

    # 各要素の設定
    def _set_width(self):
        """フロー図の大きさをもとにwidgetboxの大きさを統一するメソッドです。"""
        d = self.diagram.width + 20
        self.menu_widgetbox.width = d
        self.diagram_widgetbox.width = d
        self._msg_output = d
        
    def set_diagram(self, subflow: SubFlowManager, font_folder: Path):
        """フロー図の生成と表示設定のメソッドです。

        Args:
            subflow(SubFlowManager):サブフロー図
            font_folder(Path):フォントフォルダー
        """
        with TemporaryDirectory() as workdir:
            tmp_diag = Path(workdir) / 'skeleton.diag'
            skeleton = Path(workdir) / 'skeleton.svg'
            subflow.generate(
                svg_path=str(skeleton),
                tmp_diag=str(tmp_diag),
                font=str(font_folder / '.fonts/ipag.ttf')
            )
            self.diagram.object = self._get_contents(str(skeleton))
            self.diagram.width = self._get_svg_size(str(skeleton))
            self._set_width()

    # その他
    def _get_contents(self, svg_file_path: str) -> str:
        """フロー図を取得するメソッドです。

        Args:
            svg_file_path (str): svgファイルのパス

        Returns:
            str:svgファイルの内容を返す。
        """
        return file.File(svg_file_path).read()

    def _get_svg_size(self, svg_file_path:str) -> int:
        """svgの画像の横幅を返すメソッドです。

        Args:
            svg_file_path (str): svgファイルのパス

        Returns:
            int:svgの画像の横幅の値を返す
        """
        # SVGファイルをパース
        tree = ET.parse(svg_file_path)
        root = tree.getroot()
        # <svg>要素からviewBox属性を取得
        viewbox_value = root.get('viewBox')
        # viewbox_valueを解析して幅と高さを取得
        viewbox_width = 0
        if viewbox_value:
            viewbox_parts = viewbox_value.split()
            if len(viewbox_parts) == 4:
                viewbox_width = int(viewbox_parts[2])
                viewbox_height = int(viewbox_parts[3])
        # 大きさを調節
        if 800 < viewbox_width:
            viewbox_width = 800
        elif viewbox_width < 200:
            viewbox_width = 200
        return viewbox_width

    @classmethod
    def render(cls, working_file: str):
        """サブフローメニューを表示させるメソッドです。

        Args:
            working_file (str): 実行Notebookファイルパス
        """
        subflow_menu = cls(working_file)
        pn.extension()
        # log
        subflow_menu.log.start()

        # base path
        parent = Path(os.path.dirname(working_file))
        root_folder = Path(
            path_config.get_abs_root_form_working_dg_file_path(working_file)
        )

        # get subflow type and id from path
        subflow_type, subflow_id = get_subflow_type_and_id(working_file)
        if not subflow_type:
            raise ValueError('don\'t get subflow type.')
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
        font_folder = Path(os.environ['HOME'])

        try:
            # setup
            subflow = SubFlowManager(
                str(parent), str(status_file), str(diag_file), str(using_task_dir)
            )
            subflow.setup_tasks(str(souce_task_dir))
            subflow_menu.set_diagram(subflow, font_folder)
            subflow_menu.menu_widgetbox.append(subflow_menu.diagram_widgetbox)
        except Exception:
            message_box = MessageBox().update_error(
                f'## [INTERNAL ERROR] : {traceback.format_exc()}'
                )
            subflow_menu.menu_widgetbox.append(message_box)
        display(subflow_menu.menu_widgetbox)
        display(Javascript('IPython.notebook.save_checkpoint();'))
        subflow_menu.log.finish()
