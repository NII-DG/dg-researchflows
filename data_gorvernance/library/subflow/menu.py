"""サブフローメニューの表示

   サブフローメニュークラスを始め、サブフロー図などの画像を表示させたり、メインメニューにアクセスするメソッドがあります。
"""
import os
from pathlib import Path
import xml.etree.ElementTree as ET
from tempfile import TemporaryDirectory
import traceback

import panel as pn
from IPython.display import display
from IPython.core.display import Javascript

from .subflow import SubFlowManager
from ..utils.config import path_config, message
from ..utils.html.button import create_button
from ..utils import file
from ..utils.log import TaskLog
from ..task_director import get_subflow_type_and_id
from ..utils.widgets import MessageBox

def access_main_menu(working_file: str):
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
            diagram(pn.pane.HTML):サブフロー図
            title(pn.pane.Markdown):サブフロー図のタイトル
            diagram_widgetbox(pn.WidgetBox):サブフロー図をHTMLとして埋め込む
            selector(pn.widgets.RadioBoxGroup):ラジオボタン
            selector_options(list[str]):ラジオボタンのオプション
            working_file (str): 実行Notebookファイルパス
    """

    def __init__(self, working_file) -> None:
        """SubflowMenu コンストラクタのメソッドです

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

        # ラジオボタン
        self.selector = pn.widgets.RadioBoxGroup()
        self.selector_options = [
            message.get('subflow_menu', 'select_abled_task'),
            message.get('subflow_menu', 'select_all_task')
        ]
        self.selector.options = self.selector_options
        self.selector.value = self.selector_options[0] # type: ignore

        self.button = pn.widgets.Button(
            name=message.get('subflow_menu', 'select_button_name'),
            button_type= "primary",
            align= 'end'
        )
        # ボタンの配置
        self.select_widgetbox = pn.WidgetBox()
        self.select_widgetbox.append(
            pn.Row(self.selector, self.button, margin=(10,10,10,25))
        )

    # イベント
    def select_flow(self, subflow: SubFlowManager, font_folder: Path):
        """ラジオボタンの選択時にサブフロー図の表示を切り替えるメソッドです。

        Args:
            subflow (SubFlowManager): サブフロー図
            font_folder (Path): フォントフォルダのパス

        Returns:
            callback(function):サブフロー図を表示する。

        """
        def callback(event):
            """サブフロー図の生成と表示を行うメソッドです。"""
            self.diagram_widgetbox.disabled = True
            self.set_title()
            self.set_diagram(subflow, font_folder, self.is_display_all())
            self.diagram_widgetbox.disabled = False
        return callback

    # 各要素の設定
    def set_title(self):
        """タイトルを設定するメソッドです。"""
        if self.is_display_all():
            self.title.object = f'### {message.get("subflow_menu", "title_all_task")}'
        else:
            self.title.object = f'### {message.get("subflow_menu", "title_abled_task")}'

    def _set_width(self):
        """フロー図の大きさをもとにwidgetboxの大きさを統一するメソッドです。"""
        d = self.diagram.width + 20
        self.menu_widgetbox.width = d
        self.diagram_widgetbox.width = d
        self.select_widgetbox.width = d
        self._msg_output = d

    def set_diagram(self, subflow: SubFlowManager, font_folder: Path, display_all=True):
        """フロー図の生成と表示設定のメソッドです。
        
        Args:
            subflow(SubFlowManager):サブフロー図
            font_folder(Path):フォントフォルダー
            display_all(bool):全てのタスクを表示させるかどうか
        """
        with TemporaryDirectory() as workdir:
            tmp_diag = Path(workdir) / 'skeleton.diag'
            skeleton = Path(workdir) / 'skeleton.svg'
            subflow.generate(
                svg_path=str(skeleton),
                tmp_diag=str(tmp_diag),
                font=str(font_folder / '.fonts/ipag.ttf'),
                display_all=display_all
            )
            self.diagram.object = self._get_contents(str(skeleton))
            self.diagram.width = self._get_svg_size(str(skeleton))
            self._set_width()

    # その他
    def is_display_all(self):
        """フロー図の表示を制御するメソッドです。

        Returns:
            display_all(bool):TrueまたはFalseの値を返す。
        """
        display_all = True
        if self.selector.value == self.selector_options[0]:
            display_all = False
        return display_all

    def _get_contents(self, svg_file_path: str):
        """フロー図を取得するメソッドです。

        Args:
            svg_file_path (str): svgファイルのパス

        Returns:
            File:svgファイルの内容を返す。
        """
        return file.File(svg_file_path).read()

    def _get_svg_size(self, svg_file_path: str):
        """svgの画像の横幅を返すメソッドです。
        
        Args:
            svg_file_path (str): svgファイルのパス

        Returns:
            viewbox_width(int):svgの画像の横幅の値を返す 
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
    def render(cls, working_file: str, is_selected=False):
        """サブフローメニューを表示させるメソッドです。

        Args:
            working_file (str): 実行Notebookファイルパス
            is_selected (bool, optional): サブフローメニューを表示させるかどうか。 デフォルトでは False.
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

            # panel activation
            if is_selected:
                subflow_menu.set_title()
                subflow_menu.set_diagram(
                    subflow, font_folder, subflow_menu.is_display_all()
                )
                subflow_menu.button.on_click(
                    subflow_menu.select_flow(subflow, font_folder)
                )
                subflow_menu.menu_widgetbox.append(subflow_menu.select_widgetbox)
            else:
                subflow_menu.set_diagram(subflow, font_folder, True)
            subflow_menu.menu_widgetbox.append(subflow_menu.diagram_widgetbox)
        except Exception:
            message_box = MessageBox().update_error(f'## [INTERNAL ERROR] : {traceback.format_exc()}')
            subflow_menu.menu_widgetbox.append(message_box)
        display(subflow_menu.menu_widgetbox)
        display(Javascript('IPython.notebook.save_checkpoint();'))
        subflow_menu.log.finish()
