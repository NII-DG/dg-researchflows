import os
import shutil
import json
from pathlib import Path


def copy_file(source_path, destination_path):
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    shutil.copyfile(source_path, destination_path)


def relative_path(target_path, current_path):
    return os.path.relpath(target_path, start=current_path)


def get_next_directory(path: str, target_directory: str):
    """pathの中でtarget_directoryの一つ下のディレクトリ名を返す

    Args:
        path (str): _description_
        target_directory (str): _description_
    """
    # ファイルパスをパーツに分割
    parts = os.path.normpath(path).split(os.sep)
    # ディレクトリ名が存在する場合、そのディレクトリ名を返す
    if target_directory in parts:
        index = parts.index(target_directory)
        if index < len(parts) - 1:
            return parts[index + 1]
    # ディレクトリ名が見つからない場合(エラーハンドリングは後日)


class File:

    def __init__(self, file_path: str):
        self.path = Path(file_path)

    def read(self):
        with self.path.open('r') as file:
            content = file.read()
        return content

    def write(self, content: str):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('w') as file:
            file.write(content)

    def create(self):
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.touch()
        else:
            raise FileExistsError


class JsonFile(File):

    def __init__(self, file_path: str):
        super().__init__(file_path)

    def read(self):
        content = super().read()
        return json.loads(content)

    def write(self, data:dict):
        json_data = json.dumps(data, indent=4)
        super().write(json_data)
