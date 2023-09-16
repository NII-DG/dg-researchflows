from typing import Any
from .file import File
import nbformat
from .config import message as msg_config
from .html import security

class NbFile(File):

    def __init__(self, file_path: str):
        super().__init__(file_path)

    def embed_subflow_name_on_header(self, subflow_name:str):
        """サブフローメニュNotebookのヘッダーサブフロー名を埋める

        Args:
            subflow_name (str): [サブフロー名]
        """
        notebook = self.read()
        for cell in notebook.cells:
             if cell.cell_type == 'markdown' and msg_config.get('DEFAULT', 'param_subflow_name') in cell.source:
                cell.source = cell.source.replace(msg_config.get('DEFAULT', 'param_subflow_name'), security.escape_html_text(subflow_name))
        self.write(notebook)


    def read(self):
        with open(self.path, 'r', encoding='utf-8') as file:
            return nbformat.read(file, as_version=4)

    def write(self, notebook_data: Any):
         with open(self.path, 'w', encoding='utf-8') as file:
            nbformat.write(notebook_data, file)
