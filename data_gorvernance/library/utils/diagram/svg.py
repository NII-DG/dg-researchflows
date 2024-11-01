""" SVGファイル操作のモジュールです。"""


def init_config(id: str, name: str) -> dict:
    """ 初期設定を行う関数です。

    Args:
        id (str): 識別子を設定します。
        name (str): 名前を設定します。

    Returns:
        dict: 初期設定を含む辞書を返す。

    """
    return {
        id: {
            'name': name,
        }
    }
