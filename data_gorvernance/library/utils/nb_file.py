""" Notebookファイル操作のモジュールです。"""
import os

import nbformat

from .file import File
from .html import security


class NbFile(File):
    """ Notebookファイル操作のクラスです。"""

    def __init__(self, file_path: str) -> None:
        """ クラスのインスタンスの初期化処理を実行するメソッドです。

        Args:
            file_path (str): ファイルのパスを設定します。

        Raises:
            FileNotFoundError: ファイルが存在しない

        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f'Not Found File. file path : {file_path}')
        super().__init__(file_path)

    def embed_subflow_name_on_header(self, subflow_name: str) -> None:
        """サブフローメニュNotebookのヘッダーサブフロー名を埋めるメソッドです。

        Args:
            subflow_name (str): サブフロー名を設定します。

        """
        notebook = self.read()
        for cell in notebook.cells:
            if cell.cell_type == 'markdown' and ':subflow_name' in cell.source:
                cell.source = cell.source.replace(
                    ':subflow_name', security.escape_html_text(subflow_name)
                    )
        self.write(notebook)

    def read(self) -> nbformat.NotebookNode:
        """ ファイルからNotebookを読み込むメソッドです。

        Returns:
            nbformat.NotebookNode: 読み込んだNotebookを返す。

        """
        return nbformat.read(self.path, as_version=4)

    def write(self, notebook_data: nbformat.NotebookNode) -> None:
        """ ファイルにNotebookを書き込むメソッドです。

        Args:
            notebook_data (nbformat.NotebookNode): 書き込むNotebookを設定します。

        """
        nbformat.write(notebook_data, self.path)
