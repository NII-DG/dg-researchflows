"""メッセージ用HTML生成モジュール
"""
from IPython.display import display, HTML

def creat_html_msg(msg='', fore=None, back=None, tag='p'):
    """HTMLを生成するメソッド

    ARG
    ---------------
    msg : str
        Description : メッセージ文字列
        Default : ''
    fore : str
        Description : 文字色
        Default : None
    back : str
        Description : 背景色
        Default : None
    tag : str
        Description : HTMLタグ
        Default : 'h1'
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
    return creat_html_msg(msg=msg, back='#9eff9e', tag=tag)

def creat_html_msg_warm(msg='', tag='p'):
    return creat_html_msg(msg=msg, back='#ffff93', tag=tag)

def creat_html_msg_err(msg='', tag='p'):
    return creat_html_msg(msg=msg, back='#ffa8a8', tag=tag)

def creat_html_msg_log(msg='', tag='p'):
    return creat_html_msg(msg=msg, tag=tag)

def display_msg_info(msg='', tag='p'):
     """Infoメッセージの表示"""
     display(HTML(creat_html_msg_info(msg, tag)))

def display_msg_warm(msg='', tag='p'):
     """Warningメッセージの表示"""
     display(HTML(creat_html_msg_warm(msg, tag)))

def display_msg_err(msg='', tag='p'):
     """Errorsメッセージの表示"""
     display(HTML(creat_html_msg_err(msg, tag)))

def display_msg_log(msg='', tag='p'):
     """標準メッセージの表示"""
     display(HTML(creat_html_msg_log(msg, tag)))
