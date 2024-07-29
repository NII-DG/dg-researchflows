""" HTMLボタン生成のモジュールです"""
from typing import List


def create_button(
            url:str='',
            msg:str='',
            disable:bool=False,
            target='_self',
            a_character_color='#ffffff',
            a_font_size='15px',
            button_width='300px',
            button_height='30px',
            button_border_radius='5px',
            border:List[str] = [],
            button_background_color='#0072B5',
):
    """ HTMLのボタンを作成する関数です。

    Args:
        url (str, optional): ボタンがクリックされたときに遷移するURLを設定します。
        msg (str, optional): ボタン上に表示するメッセージを設定します。
        disable (bool, optional): ボタンを無効化するかどうかを設定します。Trueの場合、ボタンは無効化されます。
        target (str, optional): リンクの開き方を指定します。'_self'は同じタブで開くことを意味します。
        a_character_color (str, optional): ボタンの文字色を指定します。
        a_font_size (str, optional): ボタンのフォントサイズを指定します。
        button_width (str, optional): タンの幅を指定します。
        button_height (str, optional): ボタンの高さを指定します。
        button_border_radius (str, optional): ボタンの角の丸みを指定します。
        border (List[str], optional): ボタンの枠線のスタイルを指定します。
        button_background_color (str, optional): ボタンの背景色を指定します。

    Returns:
        str: 生成されたHTMLボタンの文字列を返す。
    """
    border_value = ''
    if len(border) == 0:
        border_value = '0px none'
    else:
        border_value = ' '.join(border)
    if not disable:
        # able button
        return f'<a style="font-size:{a_font_size};"href="{url}" target="{target}" ><button style="width: {button_width}; height: {button_height}; border-radius: {button_border_radius}; background-color: {button_background_color}; border: {border_value}; color: {a_character_color};">{msg}</button></a>'
    else:
        # disable button
        return f'<button style="width: {button_width}; height: {button_height}; border-radius: {button_border_radius}; background-color: {button_background_color}; border: {border_value};" disable>{msg}</button>'
