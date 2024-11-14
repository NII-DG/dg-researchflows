""" サブフローを管理するモジュールです。"""
from itertools import chain, zip_longest
import os
from pathlib import Path

from nbformat import NO_CONVERT, read

from library.utils import file
from library.utils.config import path_config
from library.utils.setting import SubflowStatusFile, SubflowTask
from .diag import DiagManager


class SubFlowManager:
    """ サブフローを管理するクラスです。

    Attributes:
        instance:
            current_dir(str): サブフローメニューの親ディレクトリ
            tasks(list[SubflowTask]): サブフローのタスクの設定値
            order(dict): サブフローのタスクの順序情報
            task_dir(str): タスクが格納されているディレクトリ
            diag(DiagManager): ダイアグラムを管理するインスタンス
            node_config(dict): ダイアグラムのノード設定用の辞書

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

    def generate(self) -> str:
        """ ダイアグラムを生成するメソッドです。

        Returns:
            str: svg形式で書かれたダイアグラムデータの文字列

        """
        self.diag = DiagManager()
        self.node_config = {}
        for task in self.tasks:
            self.node_config[task.id] = {'name': task.name}
            self.parse_headers(task)
        self.diag.update(self.current_dir, self.tasks, self.order, self.node_config)
        svg_data = self.diag.generate_svg()

        return svg_data

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
