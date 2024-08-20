""" 設定ファイルからメッセージを取得するためのモジュールです。"""
import configparser
import os

MESSAGE_CONFIG_PATH = '../../data/message.ini'
script_dir = os.path.dirname(os.path.abspath(__file__))
message_ini_path = os.path.abspath(os.path.join(script_dir, MESSAGE_CONFIG_PATH))

class ConfigParserBase:
    """ 設定ファイルを保持するシングルトンクラスです。

    Args:
        class:
            _instance (ConfigParserBase): シングルトンインスタンスを格納する

    """
    _instance = None

    def __new__(cls, *args, **kwargs) -> "ConfigParserBase":
        """ 新しいインスタンス作成時に既存のインスタンスを返すメソッドです。

        Returns:
            ConfigParserBase: このクラスのシングルトンインスタンスを返す。

        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialize(*args, **kwargs)
        return cls._instance

    def initialize(self, config_path: str, encoding: str = 'utf-8'):
        """  設定ファイルを読み込むメソッドです。

        Args:
            config_path (str): 設定ファイルのパス
            encoding (str): 設定ファイルのエンコーディング
        """
        self._config_path = config_path
        self._config_file = configparser.ConfigParser()
        self._config_file.read(config_path, encoding=encoding)

    def get(self, section: str, option: str) -> str:
        """ 指名されたセクションの項目名に対応する値を取得するメソッドです。

        Args:
            section (str): 設定ファイルのセクションを設定します。
            option (str): 設定ファイルの項目名を設定します。
        Returns:
            str: 対応する設定値を返す。

        """
        return self._config_file.get(section,option)


class Message(ConfigParserBase):
    """ message.iniを読み込むためのクラスです。"""


def get(section: str, option: str) -> str:
    """ メッセージを取得する関数です。

    Args:
        section (str): message.iniのセクションを設定します。
        option (str): message.iniのキーを設定します。
    Returns:
        str: メッセージを返す。

    """
    config = Message(message_ini_path)
    return config.get(section, option)
