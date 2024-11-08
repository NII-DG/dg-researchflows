""" サブフローを管理するモジュールです。"""
from itertools import chain, zip_longest
import os
from pathlib import Path

from nbformat import NO_CONVERT, read

from library.utils import file
from library.utils.config import path_config
from library.utils.diagram import DiagManager
from library.utils.setting import SubflowStatusFile, SubflowTask


script_dir = os.path.dirname(os.path.abspath(__file__))


class SubFlowManager:
    """ サブフローを管理するクラスです。

    Attributes:
        instance:
            current_dir(str): サブフローメニューの親ディレクトリ
            tasks(list[SubflowTask]): サブフローのタスクの設定値
            diag_file(str): ダイアグラムのファイルへのパス
            task_dir(str): タスクが格納されているディレクトリ
            diag(DiagManager): ダイアグラムを管理するインスタンス
            node_config(dict): ダイアグラムのノード設定用の辞書
            order(dict): サブフローのタスクの順序情報

    """

    def __init__(self, current_dir: str, status_file: str, using_task_dir: str) -> None:
        """ インスタンスの初期化処理を実行するメソッドです。

        Args:
            current_dir(str) : サブフローメニューの親ディレクトリを設定します。
            status_file(str) : ステータスファイルへのパスを設定します。
            using_task_dir(str) : タスクが格納されているディレクトリを設定します。

        """
        self.current_dir = current_dir
        self.tasks = SubflowStatusFile(status_file).read().tasks
        self.order = SubflowStatusFile(status_file).read().order
        self.task_dir = using_task_dir

    def _init_node_config(self, id: str, name: str) -> dict:
        """ 初期設定を行う関数です。

        Args:
            id (str): 識別子を設定します。
            name (str): 名前を設定します。

        Returns:
            dict: 初期設定を含む辞書を返す。

        """
        return {
            id: {
                'name': name,
            }
        }

    def setup_tasks(self, souce_task_dir: str):
        """ タスクの原本があるディレクトリからタスクファイルをコピーするメソッドです。

        Args:
            souce_task_dir(str) : タスクの原本があるディレクトリのパスを設定します。

        """
        if os.path.isdir(souce_task_dir):
            for task in self.tasks:
                self._copy_file_by_name(task.name, souce_task_dir, self.task_dir)

    def _copy_file_by_name(self, target_file: str, search_directory: str, destination_directory: str) -> None:
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

    def generate(self, svg_path: str) -> None:
        """ ダイアグラムを生成するメソッドです。

        Args:
            svg_path (str): SVGファイルの出力パスを設定します。

        """
        self.diag = DiagManager()
        self.node_config = {}
        for task in self.tasks:
            self.node_config.update(self._init_node_config(task.id, task.name))
            self.parse_headers(task)
        self._update()
        self.diag.generate_svg(svg_path)

    def _update(self) -> None:
        """ タスクの状態に基づいてダイアグラムを更新するメソッドです。"""
        #実行順が決まっているタスクの更新
        order_sequence = self.order.get("sequence")
        for task in self.tasks:
            if task.id in order_sequence:
                #表示しない場合に何か処理するならここにelse
                if task.active:
                    self._adjust_by_status(task)
                else:
                    order_sequence.remove(task.id)
        if order_sequence:
            self.diag.create_left_subgraph(order_sequence, self.node_config)

        #いつ実行しても構わないタスクの更新
        order_whenever = self.order.get("whenever")
        for task in self.tasks:
            if task.id in order_whenever:
                #表示しない場合に何か処理するならここにelse
                if task.active:
                    self._adjust_by_status(task)
                else:
                    order_whenever.remove(task.id)
        if order_whenever:
            self.diag.create_right_subgraph(order_whenever, self.node_config)

    def _adjust_by_status(self, task: SubflowTask):
        """ フロー図の見た目をタスクの状態によって変えるメソッドです。

        Args:
            task (SubflowTask): 調整するタスクを設定します。

        """
        task_parameter = {}

        icon_dir = "../data/icon"
        icon_dir = os.path.abspath(os.path.join(script_dir, icon_dir))
        icon_dir = file.relative_path(icon_dir, self.current_dir)

        if task.is_multiple:
            self.node_config[task.id]["text"] += "　\U0001F501"


        if task.status == task.STATUS_UNFEASIBLE:
            task_parameter["fontcolor"] = 'black'
            task_parameter["fillcolor"] = "#e6e5e3"
            task_parameter["image"] = str(icon_dir + "/lock.png")#os.path.joinに直す
            self.node_config[task.id]["task_parameter"] = task_parameter

        if task.status == task.STATUS_DONE:
            task_parameter["image"] = str(icon_dir + "/check_mark.png")
            self.node_config[task.id]['path'] += "?init_nb=true"

        elif task.status == task.STATUS_DOING:
            task_parameter["image"] = str(icon_dir + "/loading.png")

        #実行不可以外のタスクにURLを埋め込む
        link = file.relative_path(
            str(self.node_config[task.id]['path']), self.current_dir).replace("../", "./../")
        task_parameter["URL"] = link
        self.node_config[task.id]["task_parameter"] = task_parameter

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

            title = headers[0][0] if not headers[0][0].startswith(
                'About:') else headers[0][0][6:]
            if task.name in str(nb_path):
                self.node_config[task.id]['path'] = str(nb_path)
                self.node_config[task.id]['text'] = title
                break
