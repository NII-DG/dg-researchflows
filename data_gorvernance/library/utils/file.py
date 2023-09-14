import os
import shutil
import json
from pathlib import Path


def copy_file(source_path, destination_path, exist_ok=True):
    os.makedirs(os.path.dirname(destination_path), exist_ok=exist_ok)
    shutil.copyfile(source_path, destination_path)


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

    def read_json(self):
        content = self.read()
        if content:
            return json.loads(content)
        return None

    def write_json(self, data:dict):
        json_data = json.dumps(data, indent=4)
        self.write(json_data)
