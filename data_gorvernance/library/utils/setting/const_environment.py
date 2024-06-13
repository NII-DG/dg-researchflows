import os
from pathlib import Path

from ..file import JsonFile

# const_environment.jsonのファイルパス
json_path = Path(os.path.dirname(__file__)).joinpath('../../data/const_environment.json').resolve()


class ConstEnvironment:
    __FIELD = 'const_environment'
    __ID = 'id'
    __NAME = 'env_name'
    __IS_ACTIVE = 'is_active'

    def __init__(self):
        contents = JsonFile(str(json_path)).read()
        self.const_environment = contents[self.__FIELD]

    def get_names(self):
        return [fld[self.__NAME] for fld in self.const_environment]

    def get_id(self, target_name):
        for fld in self.const_environment:
            if fld[self.__NAME] == target_name:
                return fld[self.__ID]