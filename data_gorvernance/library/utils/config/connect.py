""" 設定ファイルから接続先を取得するためのモジュールです。"""
import os

from .config_parser_base import ConfigParserBase

CONNECT_CONFIG_PATH = '../../data/connect.ini'
script_dir = os.path.dirname(os.path.abspath(__file__))
connect_ini_path = os.path.abspath(os.path.join(script_dir, CONNECT_CONFIG_PATH))

class Connect(ConfigParserBase):
    """ connect.iniを読み込むためのクラスです。"""


def get(section: str, option: str) -> str:
    """ 接続先を取得する関数です。

    Args:
        section (str): connect.iniのセクションを設定します。
        option (str): connect.iniのキーを設定します。
    Returns:
        str: 接続先を返す。
    """
    config = Connect(connect_ini_path)
    return config.get(section, option)