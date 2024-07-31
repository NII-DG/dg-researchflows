"""メッセージ用HTML生成モジュールです。"""
from IPython.display import display
from IPython.core.display import HTML

def creat_html_msg(msg:str='', fore:str=None, back:str=None, tag:str='p')->str:
    """ HTMLを生成する関数です。

    Args:
        msg (str, optional): メッセージ文字列を設定します。 デフォルトは''です。
        fore (str, optional): 文字色を設定します。 デフォルトはNoneです。
        back (str, optional): 背景色を設定します。 デフォルトはNoneです。
        tag (str, optional): HTMLタグを設定します。 デフォルトは'p'です。

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

def creat_html_msg_info(msg:str='', tag:str='p')->str:
    """ infoメッセージの生成

    Args:
        msg (str, optional):メッセージ文字列を設定します。
        tag (str, optional): HTMLタグを設定します。

    Returns:
        str: htmlコードを返す。

    """
    return creat_html_msg(msg=msg, back='#9eff9e', tag=tag)

def creat_html_msg_warm(msg:str='', tag:str='p')->str:
    """ warnメッセージの生成

    Args:
        msg (str, optional):メッセージ文字列を設定します。
        tag (str, optional): HTMLタグを設定します。

    Returns:
        str: htmlコードを返す。

    """
    return creat_html_msg(msg=msg, back='#ffff93', tag=tag)

def creat_html_msg_err(msg:str='', tag:str='p')->str:
    """ errメッセージの生成

    Args:
        msg (str, optional):メッセージ文字列を設定します。
        tag (str, optional): HTMLタグを設定します。

    Returns:
        str: htmlコードを返す。

    """
    return creat_html_msg(msg=msg, back='#ffa8a8', tag=tag)

def creat_html_msg_log(msg:str='', tag:str='p')->str:
    """ 標準メッセージの生成

    Args:
        msg (str, optional):メッセージ文字列を設定します。
        tag (str, optional): HTMLタグを設定します。

    Returns:
        str: htmlコードを返す。

    """
    return creat_html_msg(msg=msg, tag=tag)

def display_msg_info(msg:str='', tag:str='p')->None:
    """Infoメッセージの表示

    Args:
        msg (str, optional):メッセージ文字列を設定します。
        tag (str, optional): HTMLタグを設定します。

    """
    display(HTML(creat_html_msg_info(msg, tag)))

def display_msg_warm(msg:str='', tag:str='p')->None:
    """Warningメッセージの表示

    Args:
        msg (str, optional):メッセージ文字列を設定します。
        tag (str, optional): HTMLタグを設定します。

    """
    display(HTML(creat_html_msg_warm(msg, tag)))

def display_msg_err(msg:str='', tag:str='p')->None:
    """Errorsメッセージの表示

    Args:
        msg (str, optional):メッセージ文字列を設定します。
        tag (str, optional): HTMLタグを設定します。

    """
    display(HTML(creat_html_msg_err(msg, tag)))

def display_msg_log(msg:str='', tag:str='p')->None:
    """標準メッセージの表示

    Args:
        msg (str, optional):メッセージ文字列を設定します。
        tag (str, optional): HTMLタグを設定します。

    """
    display(HTML(creat_html_msg_log(msg, tag)))
