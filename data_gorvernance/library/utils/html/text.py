""" メッセージ用HTML生成モジュールです。"""
from typing import Optional

from IPython.core.display import HTML
from IPython.display import display


def create_html_msg(
    msg: str = '', fore: Optional[str] = None, back: Optional[str] = None, tag: str = 'p'
) -> str:
    """ HTMLを生成する関数です。

    Args:
        msg (str): メッセージ文字列を設定します。 デフォルトは''です。
        fore (str|None): 文字色を設定します。 デフォルトはNoneです。
        back (str|None): 背景色を設定します。 デフォルトはNoneです。
        tag (str): HTMLタグを設定します。 デフォルトは'p'です。

    Returns:
        str: htmlコードを返す。

    """
    if fore is not None and back is not None:
        style: str = 'color:' + fore + ';' + 'background-color:' + back + ";"
    elif fore is not None and back is None:
        style = 'color:' + fore
    elif fore is None and back is not None:
        style = 'background-color:' + back
    else:
        style = ""

    if style != "":
        return "<" + tag + " style='" + style + "'>" + msg + "</" + tag + ">"
    else:
        return "<" + tag + " style='" + style + "'>" + msg + "</" + tag + ">"


def create_html_msg_info(msg: str = '', tag: str = 'p') -> str:
    """ infoメッセージを生成する関数です。

    Args:
        msg (str):メッセージ文字列を設定します。
        tag (str): HTMLタグを設定します。

    Returns:
        str: htmlコードを返す。

    """
    return create_html_msg(msg=msg, back='#9eff9e', tag=tag)


def create_html_msg_warm(msg: str = '', tag: str = 'p') -> str:
    """ warnメッセージを生成する関数です。

    Args:
        msg (str):メッセージ文字列を設定します。
        tag (str): HTMLタグを設定します。

    Returns:
        str: htmlコードを返す。

    """
    return create_html_msg(msg=msg, back='#ffff93', tag=tag)


def create_html_msg_err(msg: str = '', tag: str = 'p') -> str:
    """ errメッセージを生成する関数です。

    Args:
        msg (str):メッセージ文字列を設定します。
        tag (str): HTMLタグを設定します。

    Returns:
        str: htmlコードを返す。

    """
    return create_html_msg(msg=msg, back='#ffa8a8', tag=tag)


def create_html_msg_log(msg: str = '', tag: str = 'p') -> str:
    """ 標準メッセージを生成する関数です。

    Args:
        msg (str):メッセージ文字列を設定します。
        tag (str): HTMLタグを設定します。

    Returns:
        str: htmlコードを返す。

    """
    return create_html_msg(msg=msg, tag=tag)


def display_msg_info(msg: str = '', tag: str = 'p') -> None:
    """Infoメッセージを表示する関数です。

    Args:
        msg (str):メッセージ文字列を設定します。
        tag (str): HTMLタグを設定します。

    """
    display(HTML(create_html_msg_info(msg, tag)))


def display_msg_warm(msg: str = '', tag: str = 'p') -> None:
    """Warningメッセージを表示する関数です。

    Args:
        msg (str):メッセージ文字列を設定します。
        tag (str): HTMLタグを設定します。

    """
    display(HTML(create_html_msg_warm(msg, tag)))


def display_msg_err(msg: str = '', tag: str = 'p') -> None:
    """Errorsメッセージを表示する関数です。

    Args:
        msg (str):メッセージ文字列を設定します。
        tag (str): HTMLタグを設定します。

    """
    display(HTML(create_html_msg_err(msg, tag)))


def display_msg_log(msg: str = '', tag: str = 'p') -> None:
    """標準メッセージを表示する関数です。

    Args:
        msg (str):メッセージ文字列を設定します。
        tag (str): HTMLタグを設定します。

    """
    display(HTML(create_html_msg_log(msg, tag)))
