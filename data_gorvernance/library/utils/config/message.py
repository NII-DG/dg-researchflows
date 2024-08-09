""" メッセージ取得のモジュールです。"""
import configparser
import os

MESSAGE_CONFIG_PATH = '../../data/message.ini'
script_dir = os.path.dirname(os.path.abspath(__file__))
message_ini_path = os.path.abspath(os.path.join(script_dir, MESSAGE_CONFIG_PATH))

class Message(configparser.ConfigParser):
    """ メッセージファイルを保持するためのシングルトンなクラスです。

    Args:
        class:
            _instance (Message): シングルトンインスタンスを格納する

    """

    def __new__(cls, *args, **kwargs)->'Message':
        """ 新しいインスタンス作成時に既存のインスタンスを返すメソッドです。

        Returns:
            Message: シングルトンインスタンスを返す。

        """
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, *args, **kwargs):
        """ インスタンスの初期化処理を実行するメソッドです。

        インスタンス初期化時に設定ファイルを読み込みます。

        """
        super().__init__(*args, **kwargs)
        self.read(message_ini_path, encoding='utf-8')


def get(section:str, option:str) -> str:
    """ メッセージを取得する関数です。

    Args:
        section (str): message.iniのセクションを設定します。
        option (str): message.iniのキーを設定します。
    Returns:
        str: メッセージを返す。

    """
    config = Message()
    return config[section][option]
