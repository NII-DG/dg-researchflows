import re
from subprocess import run
from pathlib import Path
from itertools import chain, zip_longest

from lxml import etree
from nbformat import read, NO_CONVERT


class DiagManager:

    def __init__(self, file_path: str) -> None:
        self.path = Path(file_path)

    def change_group_color(self, group_id: str, color: str):
        pass

    def update_mark(self, node_id:str, value: str):
        pass
