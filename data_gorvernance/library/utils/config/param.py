import os
from pathlib import Path

from ...utils.file import JsonFile

# param.jsonのファイルパス
script_dir_path = os.path.dirname(__file__)
p = Path(script_dir_path)
param_json_file = p.joinpath('../../..', 'researchflow/params.json').resolve()


class ParamConfig():
    __SIBLINGS = 'siblings'
    __RCOSBINDERURL = 'rcosBinderUrl'
    __DGCORE = 'dgCore'
    __REPOSITORY = 'repository'

    def __init__(self):
        self._param_file = JsonFile(str(param_json_file))
        data = self._param_file.read()

        self._siblings = Siblings(data[self.__SIBLINGS])
        self._rcosBinderUrl = data[self.__RCOSBINDERURL]
        self._dg_core = GgCore(data[self.__DGCORE])
        self._repository = Repository(data[self.__REPOSITORY])

    def update(self):
        data = {}
        data[self.__SIBLINGS] = self._siblings.to_dict()
        data[self.__RCOSBINDERURL] = self._rcosBinderUrl
        data[self.__DGCORE] = self._dg_core.to_dict()
        data[self.__REPOSITORY] = self._repository.to_dict()
        self._param_file.write(data)

    @classmethod
    def get_param_data(cls):
        pc = ParamConfig()
        return pc

    @classmethod
    def get_siblings_ginHttp(cls):
        pc = ParamConfig()
        return pc._siblings._ginHttp

    @classmethod
    def get_repo_id(cls):
        pc = ParamConfig()
        return pc._repository._id



class Siblings():
    __GINHTTP = 'ginHttp'
    __GINSSH = 'ginSsh'
    __GITHUGIBHTTP = 'gitHugibHttp'
    __GITHUBSSH = 'gitHubSsh'

    def __init__(self, siblings_data: dict) -> None:
        self._ginHttp = siblings_data[self.__GINHTTP]
        self._ginSsh = siblings_data[self.__GINSSH]
        self._gitHugibHttp = siblings_data[self.__GITHUGIBHTTP]
        self._gitHubSsh = siblings_data[self.__GITHUBSSH]

    def to_dict(self):
        data = {}
        data[self.__GINHTTP] = self._ginHttp
        data[self.__GINSSH] = self._ginSsh
        data[self.__GITHUGIBHTTP] = self._gitHugibHttp
        data[self.__GITHUBSSH] = self._gitHubSsh
        return data

class GgCore():
    __SCHEME = 'Scheme'
    __NETLOC = 'Netloc'

    def __init__(self, dg_core_data: dict) -> None:
        self._scheme = dg_core_data[self.__SCHEME]
        self._netloc = dg_core_data[self.__NETLOC]

    def to_dict(self):
        data = {}
        data[self.__SCHEME] = self._scheme
        data[self.__NETLOC] = self._netloc
        return data

class Repository():
    __ID = 'id'

    def __init__(self, repo_data: dict) -> None:
        self._id = repo_data[self.__ID]

    def to_dict(self):
        data = {}
        data[self.__ID] = self._id
        return data
