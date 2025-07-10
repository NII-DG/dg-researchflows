""" HTMLエスケープのモジュールです。"""
import html


# HTMLエンティティエスケープを行う
def escape_html_text(original_string: str) -> str:
    """HTMLエンティティエスケープを行う関数です。

    Args:
        original_string (str): HTMLエンティティエスケープを行う文字列を設定します。

    Returns:
        str: HTMLエンティティエスケープを行った文字列を返す。

    """
    return html.escape(original_string)
