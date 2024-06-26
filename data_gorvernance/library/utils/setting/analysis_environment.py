import os
from pathlib import Path

from ..file import JsonFile

# analysis_environment.jsonのファイルパス
json_path = Path(os.path.dirname(__file__)).joinpath('../../data/analysis_environment.json').resolve()


class AnalysisEnvironment:
    __FIELD = 'analysis_environment'
    __ID = 'id'
    __NAME = 'env_name'
    __DESCRIPTION = 'description'
    __IS_ACTIVE = 'is_active'

    def __init__(self):
        contents = JsonFile(str(json_path)).read()
        self.analysis_environment = contents[self.__FIELD]

    def get_names(self):
        return [fld[self.__NAME] for fld in self.analysis_environment]

    def get_id(self, target_name):
        for fld in self.analysis_environment:
            if fld[self.__NAME] == target_name:
                return fld[self.__ID]

    def get_description(self, target_name):
        for fld in self.analysis_environment:
            if fld[self.__NAME] == target_name:
                return fld[self.__DESCRIPTION]