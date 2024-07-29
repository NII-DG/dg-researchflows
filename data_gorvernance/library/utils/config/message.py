""" メッセージ取得ののモジュールです。
メッセージ取得の関数が記載されています。
"""
import configparser
import os

MESSAGE_CONFIG_PATH = '../../data/message.ini'
script_dir = os.path.dirname(os.path.abspath(__file__))
message_ini_path = os.path.abspath(os.path.join(script_dir, MESSAGE_CONFIG_PATH))


def get(section:str, option:str) -> str:
    """ メッセージを取得する関数です。

    Args:
        section (str): message.iniのセクション
        key (str): message.iniのキー
    Returns:
        str: メッセージを返す。
    """
    config = configparser.ConfigParser()
    config.read(message_ini_path, encoding='utf-8')

    return config[section][option]