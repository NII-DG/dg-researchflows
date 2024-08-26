""" メッセージ取得のモジュールです。"""
from mailbox import Message
import os

MESSAGE_CONFIG_PATH = '../../data/message.ini'
script_dir = os.path.dirname(os.path.abspath(__file__))
message_ini_path = os.path.abspath(os.path.join(script_dir, MESSAGE_CONFIG_PATH))


def get(section: str, option: str) -> str:
    """ メッセージを取得する関数です。

    Args:
        section (str): message.iniのセクションを設定します。
        option (str): message.iniのキーを設定します。
    Returns:
        str: メッセージを返す。

    """
    config = Message(message_ini_path)
    return config[section][option]
