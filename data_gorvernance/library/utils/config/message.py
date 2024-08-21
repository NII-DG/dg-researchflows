""" 設定ファイルからメッセージを取得するためのモジュールです。"""
import os

from .config_parser_base import ConfigParserBase

MESSAGE_CONFIG_PATH = '../../data/message.ini'
script_dir = os.path.dirname(os.path.abspath(__file__))
message_ini_path = os.path.abspath(os.path.join(script_dir, MESSAGE_CONFIG_PATH))

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
