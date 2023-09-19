from subprocess import run
from pathlib import Path

from lxml import etree
from nbformat import read, NO_CONVERT

from ..file import File


class DiagManager:

    def __init__(self, file_path: str) -> None:
        self.path = Path(file_path)
        # 以下暫定措置としてファイル書き変えのために用いる
        self.content = File(str(self.path)).read()

    def change_group_color(self, group_id: str, color: str):
        pass

    def update_mark(self, node_id: str, value: str):
        pass

    def change_node_style(self, node_id, style):
        pass

    def delete_node(self, node_id):
        pass
