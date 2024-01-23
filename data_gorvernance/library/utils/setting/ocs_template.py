import os
from pathlib import Path
from typing import List

from ..file import JsonFile

# ocs_template.jsonのファイルパス
script_dir_path = os.path.dirname(__file__)
p = Path(script_dir_path)
ocs_template_json_file = p.joinpath('../../data/ocs-template.json').resolve()

class OCSTemplate:
    __FIELD = "ocs_template"
    __ID = "id"
    __FIELD_NAME = "ocs_template_name"
    __OCS_TEMPLATE_PATH = "ocs_template_path"
    __IS_ACTIVE = "is_active"

    def __init__(self) -> None:
        contents = JsonFile(str(ocs_template_json_file)).read()
        self.ocs_template = contents[self.__FIELD]

    def get_name(self):
        return [fld[self.__FIELD_NAME] for fld in self.ocs_template]

    def get_disabled_ids(self)->List[str]:
        disabled = []
        for fld in self.ocs_template:
            if not fld[self.__IS_ACTIVE]:
                disabled.append(fld[self.__FIELD_NAME])
        return disabled

    def get_id(self, target_name):
        for fld in self.ocs_template:
            if fld[self.__FIELD_NAME] == target_name:
                return fld[self.__ID]

    def get_template_path(self, target_name):
        for fld in self.ocs_template:
            if fld[self.__FIELD_NAME] == target_name:
                return fld[self.__OCS_TEMPLATE_PATH]
