""" サブフローを管理するモジュールです。"""
from itertools import chain, zip_longest
import os
from pathlib import Path

from nbformat import NO_CONVERT, read

from library.utils import file
from library.utils.config import path_config
from library.utils.setting import SubflowStatusFile
from library.main_menu.subflow_controller import utils
from .diag import DiagManager


class SubFlowManager:
    """ サブフローを管理するクラスです。

    Attributes:
        instance:
            current_dir(str): サブフローメニューの親ディレクトリ
            tasks(list[SubflowTask]): サブフローのタスクの設定値
            order(dict): サブフローのタスクの順序情報
            task_dir(str): タスクが格納されているディレクトリ

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

    def setup_tasks(self, souce_task_dir: str):
        """ タスクの原本があるディレクトリからタスクファイルをコピーするメソッドです。

        Args:
            souce_task_dir(str) : タスクの原本があるディレクトリのパスを設定します。

        """
        if os.path.isdir(souce_task_dir):
            for task in self.tasks:
                if task.active:
                    utils._copy_file_by_name(task.name, souce_task_dir, self.task_dir)

    def generate(self) -> str:
        """ ダイアグラムを生成するメソッドです。

        Returns:
            str: svg形式で書かれたダイアグラムデータの文字列

        """
        diag = DiagManager()
        node_config = {}
        for task in self.tasks:
            if task.active:
                title, nb_path = self.parse_headers(task.name)
                node_config[task.id] = {
                    'path': nb_path,
                    'text': title
                }
        svg_data = diag.generate_diagram(self.current_dir, self.tasks, node_config, self.order)

        return svg_data

    def parse_headers(self, task_name: str) -> tuple[str, str]:
        """ タスクタイトルとパスを取得するメソッドです。

        Args:
            task_name (str): 対象とするタスクの名前
            node_config(dict): ノードに設定する情報の辞書

        Returns:
            str: タスクのタイトル
            str: タスク実行時に遷移するノートブックのパス

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
            if task_name in str(nb_path):
                return title, str(nb_path)
