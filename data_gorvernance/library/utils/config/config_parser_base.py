""" 設定ファイルから情報を読み取るためのモジュールです。

設定ファイルを読み込むための基底クラスが記載されています。
"""
from __future__ import annotations
import configparser

class ConfigParserBase:
    """ 設定ファイルを保持するシングルトンクラスです。

    Args:
        class:
            _instance (ConfigParserBase): シングルトンインスタンスを格納する
        instance:
            _config_file (ConfigParser): 設定ファイルの情報を保持するインスタンス
    """
    _instance = None

    def __new__(cls, *args, **kwargs) -> ConfigParserBase:
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
        return self._config_file[section][option]