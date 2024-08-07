""" サブフローを管理するモジュールです。"""
import os
from itertools import chain, zip_longest
from pathlib import Path

from nbformat import NO_CONVERT, read

from ..utils import file
from ..utils.config import path_config
from ..utils.diagram import DiagManager, init_config, update_svg
from ..utils.setting import SubflowStatusFile, SubflowTask

script_dir = os.path.dirname(os.path.abspath(__file__))

class SubFlowManager:
    """ サブフローを管理するクラスです。

    Attributes:
        instance:
            current_dir(str): サブフローメニューの親ディレクトリ
            tasks(List[SubflowTask]): サブフローのタスクの設定値
            diag_file(str): ダイアグラムのファイルへのパス
            task_dir(str): タスクが格納されているディレクトリ
            diag(DiagManager): ダイアグラムを管理するインスタンス
            svg_config(dict): SVGの設定用の辞書

    """

    def __init__(self, current_dir: str, status_file :str, diag_file :str, using_task_dir: str) -> None:
        """ インスタンスの初期化処理を実行するメソッドです。

        Args:
            current_dir(str) : サブフローメニューの親ディレクトリを設定します。
            status_file(str) : ステータスファイルへのパスを設定します。
            diag_file(str) : ダイアグラムのファイルへのパスを設定します。
            using_task_dir(str) : タスクが格納されているディレクトリを設定します。

        """
        self.current_dir = current_dir
        self.tasks = SubflowStatusFile(status_file).read().tasks
        self.diag_file = diag_file
        self.task_dir = using_task_dir

    def setup_tasks(self, souce_task_dir: str):
        """ タスクの原本があるディレクトリからタスクファイルをコピーするメソッドです。

        Args:
            souce_task_dir(str) : タスクの原本があるディレクトリのパスを設定します。

        """
        if os.path.isdir(souce_task_dir):
            for task in self.tasks:
                self._copy_file_by_name(task.name, souce_task_dir, self.task_dir)

    def _copy_file_by_name(self, target_file: str, search_directory :str, destination_directory: str) -> None:
        """ 指定した名前のファイルを検索ディレクトリから目的のディレクトリにコピーするメソッドです。

        Args:
            target_file(str) : コピー元のファイルを設定します。
            search_directory(str) : ファイルを検索するディレクトリを設定します。
            destination_directory(str) : コピー先のディレクトリを設定します。

        """
        for root, dirs, files in os.walk(search_directory):
            for filename in files:
                if not filename.startswith(target_file):
                    continue
                # if filename.startswith(target_file) のとき
                source_dir = root
                relative_path = file.relative_path(root, search_directory)
                destination_dir = os.path.join(destination_directory, relative_path)
                # タスクノートブックのコピー
                source_file = os.path.join(source_dir, filename)
                destination_file = os.path.join(destination_dir, filename)
                if not os.path.isfile(destination_file):
                    file.copy_file(source_file, destination_file)
                # imagesのシンボリックリンク
                source_images = os.path.join(
                    path_config.get_abs_root_form_working_dg_file_path(root),
                    path_config.DG_IMAGES_FOLDER
                )
                destination_images = os.path.join(destination_dir, path_config.IMAGES)
                if not os.path.isdir(destination_images):
                    os.symlink(source_images, destination_images, target_is_directory=True)


    def generate(self, svg_path: str, tmp_diag: str, font: str, display_all:bool = True) -> None:
        """ ダイアグラムを生成するメソッドです。

        Args:
            svg_path (str): SVGファイルの出力パスを設定します。
            tmp_diag (str): 一時的なダイアグラムファイルへのパスを設定します。
            font (str): ダイアグラムに使用するフォントを設定します。
            display_all (bool): 非推奨のタスクを推奨タスクと同じように表示するかどうかを設定します。

        """
        # 毎回元ファイルを読み込む
        self.diag = DiagManager(self.diag_file)
        # tmp_diagは暫定的なもの。将来的にはself.diagを利用できるようにする
        self.svg_config = {}
        for task in self.tasks:
            self.svg_config.update(init_config(task.id, task.name))
            self.parse_headers(task)
        self._update(display_all)
        for task in self.tasks:
            self.change_id(task)
        self.diag.generate_svg(tmp_diag, svg_path, font)
        update_svg(svg_path, self.current_dir, self.svg_config)

    def _update(self, display_all: bool = True) -> None:
        """ タスクの状態に基づいてダイアグラムを更新するメソッドです。

        Args:
            display_all (bool): 非推奨のタスクを推奨タスクと同じように表示するかどうかを設定します。

        """
        for task in self.tasks:
            self._adjust_by_status(task, display_all)
            self._adjust_by_optional(task, display_all)

    def _adjust_by_optional(self, task: SubflowTask, display_all: bool = True) -> None:
        """ 非推奨のタスクをグレーアウトし、リンクが押せない状態にするメソッドです。

        Args:
            task (SubflowTask): 調整するタスクを設定します。
            display_all (bool): 非推奨のタスクを通常通りに表示するかどうかを設定します。

        """
        if task.disable:
            if display_all:
                #self.diag.update_node_style(task.id, 'dotted')
                pass
            else:
                # self.diag.delete_node(task.id)
                # 以下暫定処理
                self.diag.update_node_color(task.id, "#77787B")
                self.svg_config[task.id]['is_link'] = False

    def _adjust_by_status(self, task: SubflowTask, display_all: bool = True) -> None:
        """ フロー図の見た目をタスクの状態によって変えるメソッドです。

        Args:
            task (SubflowTask): 調整するタスクを設定します。
            display_all (bool): 非推奨のタスクを推奨タスクと同じように調整するかどうかを設定します。

        """
        if task.disable and not display_all:
            return

        if task.is_multiple:
            self.diag.update_node_stacked(task.id)

        icon_dir = "../data/icon"
        icon_dir = os.path.abspath(os.path.join(script_dir, icon_dir))
        icon_dir = file.relative_path(icon_dir, self.current_dir)

        if task.status == task.STATUS_UNFEASIBLE:
            self.diag.update_node_color(task.id, "#e6e5e3")
            self.diag.update_node_icon(task.id, icon_dir + "/lock.png")
            self.svg_config[task.id]['is_link'] = False
            return

        if task.status == task.STATUS_DONE:
            self.diag.update_node_icon(task.id, icon_dir + "/check_mark.png")
            self.svg_config[task.id]['path'] += "?init_nb=true"
        elif task.status == task.STATUS_DOING:
            self.diag.update_node_icon(task.id, icon_dir + "/loading.png")

    def parse_headers(self, task: SubflowTask) -> None:
        """ タスクタイトルとパスを取得するメソッドです。

        Args:
            task (SubflowTask): 対象とするタスクを設定します。

        """
        nb_dir = Path(self.task_dir)
        for nb_path in nb_dir.glob("**/*.ipynb"):
            nb = read(str(nb_path), as_version=NO_CONVERT)
            lines = [
                line.strip()
                for line in chain.from_iterable(
                    cell['source'].split('\n')
                    for cell in nb.cells
                    if cell['cell_type'] == 'markdown'
                )
                if len(line.strip()) > 0 and not line.startswith('---')
            ]
            # h1, h2 の行とその次行の最初の１文を取り出す
            headers = [
                (' '.join(line0.split()[1:]),
                    line1.split("。")[0] if line1 is not None else '')
                for (line0, line1) in zip_longest(lines, lines[1:])
                if line0.startswith('# ') or line0.startswith('## ')
            ]

            title = headers[0][0] if not headers[0][0].startswith('About:') else headers[0][0][6:]
            if task.name in str(nb_path):
                self.svg_config[task.id]['path'] = str(nb_path)
                self.svg_config[task.id]['text'] = title
                break

    def change_id(self, task: SubflowTask) -> None:
        """diagファイルのタスクIDをタスクタイトルに置き換えるメソッドです。

        Args:
            task (SubflowTask): タスクIDをタスクタイトルに置き換えるタスクを設定します。

        """
        lines = self.diag.content.splitlines()
        new_lines = []
        for line in lines:
            if task.id in line:
                find = task.id
                replace = self.svg_config[task.id]['text']
                update = line.replace(find, replace, 1)
                new_lines.append(update)
            else:
                new_lines.append(line)
        self.diag.content = '\n'.join(new_lines)