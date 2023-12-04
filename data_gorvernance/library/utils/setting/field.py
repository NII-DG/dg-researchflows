import os
from pathlib import Path
from typing import List

from ..file import JsonFile

# field.jsonのファイルパス
script_dir_path = os.path.dirname(__file__)
p = Path(script_dir_path)
field_json_file = p.joinpath('../../data/field.json').resolve()

class Field:
    __FIELD = "field"
    __ID = "id"
    __FIELD_NAME = "field_name"
    __EXPERIMENT_PACKAGE = "experiment_package"
    __IS_ACTIVE = "is_active"

    def __init__(self) -> None:
        contents = JsonFile(str(field_json_file)).read()
        self.field = contents[self.__FIELD]

    def get_name(self):
        return [fld[self.__FIELD_NAME] for fld in self.field]

    def get_disabled_ids(self)->List[str]:
        disabled = []
        for fld in self.field:
            if not fld[self.__IS_ACTIVE]:
                disabled.append(fld[self.__FIELD_NAME])
        return disabled

    def get_template_path(self, target_name):
        for fld in self.field:
            if fld[self.__FIELD_NAME] == target_name:
                return fld[self.__EXPERIMENT_PACKAGE]
