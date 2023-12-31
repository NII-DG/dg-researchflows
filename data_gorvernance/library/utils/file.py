import os
import shutil
import json
from pathlib import Path


def copy_file(source_path, destination_path):
    """ファイルをコピーする

    既にファイルが存在する場合は上書き

    """
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    shutil.copyfile(source_path, destination_path)


def relative_path(target_path, start_dir):
    """target_pathをstart_dirからの相対パスに変換する

    Args:
        target_path (_type_): 変換したいパス
        start_dir (_type_): 基準となるディレクトリのパス

    Returns:
        str: start_dirからtarget_pathまでの相対パス
    """
    if target_path and start_dir:
        return os.path.relpath(
                    path=os.path.normpath(target_path),
                    start=os.path.normpath(start_dir)
                )
    else:
        return ""


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
