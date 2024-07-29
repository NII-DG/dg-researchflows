import os
from typing import Any

import nbformat

from .file import File
from .html import security


class NbFile(File):

    def __init__(self, file_path: str):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f'Not Found File. file path : {file_path}')
        super().__init__(file_path)

    def embed_subflow_name_on_header(self, subflow_name:str):
        """サブフローメニュNotebookのヘッダーサブフロー名を埋める

        Args:
            subflow_name (str): [サブフロー名]
        """
        notebook = self.read()
        for cell in notebook.cells:
            if cell.cell_type == 'markdown' and ':subflow_name' in cell.source:
                cell.source = cell.source.replace(':subflow_name', security.escape_html_text(subflow_name))
        self.write(notebook)

    def read(self):
        return nbformat.read(self.path, as_version=4)

    def write(self, notebook_data: Any):
        nbformat.write(notebook_data, self.path)
