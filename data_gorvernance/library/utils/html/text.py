"""メッセージ用HTML生成モジュールです。"""
from IPython.display import display
from IPython.core.display import HTML

def creat_html_msg(msg='', fore=None, back=None, tag='p'):
    """ HTMLを生成する関数です。

    Args:
        msg (str, optional): メッセージ文字列を設定します。 デフォルトは''
        fore (str, optional): 文字色を設定します。 デフォルトはNone
        back (str, optional): 背景色を設定します。 デフォルトはNone
        tag (str, optional): HTMLタグを設定します。 デフォルトは'p'

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

def creat_html_msg_info(msg='', tag='p'):
    """ infoメッセージの生成

    Args:
        msg (str, optional):メッセージ文字列を設定します。
        tag (str, optional): HTMLタグを設定します。

    Returns:
        str: htmlコードを返す。
    """
    return creat_html_msg(msg=msg, back='#9eff9e', tag=tag)

def creat_html_msg_warm(msg='', tag='p'):
    """ warnメッセージの生成

    Args:
        msg (str, optional):メッセージ文字列を設定します。
        tag (str, optional): HTMLタグを設定します。

    Returns:
        str: htmlコードを返す。
    """
    return creat_html_msg(msg=msg, back='#ffff93', tag=tag)

def creat_html_msg_err(msg='', tag='p'):
    """ errメッセージの生成

    Args:
        msg (str, optional):メッセージ文字列を設定します。
        tag (str, optional): HTMLタグを設定します。

    Returns:
        str: htmlコードを返す。
    """
    return creat_html_msg(msg=msg, back='#ffa8a8', tag=tag)

def creat_html_msg_log(msg='', tag='p'):
    """ 標準メッセージの生成

    Args:
        msg (str, optional):メッセージ文字列を設定します。
        tag (str, optional): HTMLタグを設定します。

    Returns:
        str: htmlコードを返す。
    """
    return creat_html_msg(msg=msg, tag=tag)

def display_msg_info(msg='', tag='p'):
     """Infoメッセージの表示
     
     Args:
        msg (str, optional):メッセージ文字列を設定します。
        tag (str, optional): HTMLタグを設定します。
     """
     display(HTML(creat_html_msg_info(msg, tag)))

def display_msg_warm(msg='', tag='p'):
     """Warningメッセージの表示
     
     Args:
        msg (str, optional):メッセージ文字列を設定します。
        tag (str, optional): HTMLタグを設定します。
     """
     display(HTML(creat_html_msg_warm(msg, tag)))

def display_msg_err(msg='', tag='p'):
     """Errorsメッセージの表示
     
     Args:
        msg (str, optional):メッセージ文字列を設定します。
        tag (str, optional): HTMLタグを設定します。
     """
     display(HTML(creat_html_msg_err(msg, tag)))

def display_msg_log(msg='', tag='p'):
     """標準メッセージの表示
     
     Args:
        msg (str, optional):メッセージ文字列を設定します。
        tag (str, optional): HTMLタグを設定します。
     """
     display(HTML(creat_html_msg_log(msg, tag)))
