""" 設定ファイルのモジュールです。

設定ファイルの操作のクラスや各種設定情報を保持するクラスが記載されています。

"""
import os
from pathlib import Path

from library.utils.file import JsonFile


# param.jsonのファイルパス
script_dir_path = os.path.dirname(__file__)
p = Path(script_dir_path)
param_json_file = p.joinpath('../../..', 'researchflow/params.json').resolve()


class ParamConfig():
    """ 設定ファイル操作のクラスです。

    Attributes:
        class:
            __SIBLINGS(str): siblingsのキー
            __RCOS_BINDER_URL(str): rcosBinderUrlのキー
            __DGCORE(str): dgCoreのキー
            __REPOSITORY(str): repositoryのキー
        instance:
            _param_file(JsonFile): 設定ファイルを操作するためのインスタンス
            _siblings(Siblings): Siblingsクラスのインスタンス
            _rcos_binder_url: RCOSのBinderのURL
            _dg_core(Dgcore): Dgcoreクラスのインスタンス
            _repository(Repository): Repositoryクラスのインスタンス

    """
    __SIBLINGS = 'siblings'
    __RCOS_BINDER_URL = 'rcosBinderUrl'
    __DGCORE = 'dgCore'
    __REPOSITORY = 'repository'

    def __init__(self) -> None:
        """ インスタンスの初期化処理を実行するメソッドです。"""
        self._param_file = JsonFile(str(param_json_file))
        data = self._param_file.read()

        self._siblings = Siblings(data[self.__SIBLINGS])
        self._rcos_binder_url = data[self.__RCOS_BINDER_URL]
        self._dg_core = Dgcore(data[self.__DGCORE])
        self._repository = Repository(data[self.__REPOSITORY])

    def update(self) -> None:
        """ JSONファイルを書き換えるメソッドです。"""
        data = {}
        data[self.__SIBLINGS] = self._siblings.to_dict()
        data[self.__RCOS_BINDER_URL] = self._rcos_binder_url
        data[self.__DGCORE] = self._dg_core.to_dict()
        data[self.__REPOSITORY] = self._repository.to_dict()
        self._param_file.write(data)

    @classmethod
    def get_param_data(cls) -> 'ParamConfig':
        """ 各種データを取得するメソッドです。

        Returns:
            ParamConfig: 各種パラメータを持つオブジェクトを返す。

        """
        pc = ParamConfig()
        return pc

    @classmethod
    def get_siblings_gin_http(cls) -> str:
        """ ginHTTPを取得するメソッドです。

        Returns:
            str: gin_httpの値を返す。

        """
        pc = ParamConfig()
        return pc._siblings._gin_http

    @classmethod
    def get_repo_id(cls) -> str:
        """ リポジトリのIDを取得するメソッドです。

        Returns:
            str: リポジトリのIDを返す。

        """
        pc = ParamConfig()
        return pc._repository._id


class Siblings():
    """ siblingsの情報を保持するクラスです。

    Attributes:
        class:
            __GINHTTP(str): gin_httpのキー
            __GINSSH(str): gin_sshのキー
            __GITHUGIBHTTP(str): git_hugib_httpのキー
            __GITHUBSSH(str): git_hub_sshのキー
        instance:
            _gin_http(str): gin_httpの値
            _gin_ssh(str): gin_sshの値
            _git_hugib_http(str): git_hugib_httpの値
            _git_hub_ssh(str): git_hub_sshの値

    """
    __GINHTTP = 'gin_http'
    __GINSSH = 'gin_ssh'
    __GITHUGIBHTTP = 'git_hugib_http'
    __GITHUBSSH = 'git_hub_ssh'

    def __init__(self, siblings_data: dict) -> None:
        """ インスタンスの初期化処理を実行するメソッドです。

        Args:
            siblings_data (dict): 設定する値を含む辞書

        """
        self._gin_http = siblings_data[self.__GINHTTP]
        self._gin_ssh = siblings_data[self.__GINSSH]
        self._git_hugib_http = siblings_data[self.__GITHUGIBHTTP]
        self._git_hub_ssh = siblings_data[self.__GITHUBSSH]

    def to_dict(self) -> dict:
        """ インスタンス変数を辞書に変換するメソッドです。

        Returns:
            dict: インスタンス変数の値を持つ辞書を返す。

        """
        data = {}
        data[self.__GINHTTP] = self._gin_http
        data[self.__GINSSH] = self._gin_ssh
        data[self.__GITHUGIBHTTP] = self._git_hugib_http
        data[self.__GITHUBSSH] = self._git_hub_ssh
        return data


class Dgcore():
    """ dgcoreの情報を保持するクラスです。

    Attributes:
        class:
            __SCHEME(str): スキーマのキー
            __NETLOC(str): ネットワークロケーションのキー
        instance:
            _scheme(str): スキーマの値
            _netloc(str): ネットワークロケーションの値

    """
    __SCHEME = 'Scheme'
    __NETLOC = 'Netloc'

    def __init__(self, dg_core_data: dict) -> None:
        """ インスタンスの初期化処理を実行するメソッドです。

        Args:
            dg_core_data (dict): インスタンス変数に設定する値を持つ辞書

        """
        self._scheme = dg_core_data[self.__SCHEME]
        self._netloc = dg_core_data[self.__NETLOC]

    def to_dict(self) -> dict:
        """ インスタンス変数を辞書に変換するメソッドです。

        Returns:
            dict: インスタンス変数の値を持つ辞書を返す。

        """
        data = {}
        data[self.__SCHEME] = self._scheme
        data[self.__NETLOC] = self._netloc
        return data


class Repository():
    """ リポジトリの情報を保持するクラスです。

    Attributes:
        class:
            __ID(str): リポジトリidのキー
        instance:
            _id(str): リポジトリidの値

    """
    __ID = 'id'

    def __init__(self, repo_data: dict) -> None:
        """ インスタンスの初期化処理を実行するメソッドです。

        Args:
            repo_data (dict): 設定する値を含む辞書

        """
        self._id = repo_data[self.__ID]

    def to_dict(self) -> dict:
        """ インスタンス変数を辞書に変換するメソッドです。

        Returns:
            dict: インスタンス変数の値を持つ辞書を返す。

        """
        data = {}
        data[self.__ID] = self._id
        return data
