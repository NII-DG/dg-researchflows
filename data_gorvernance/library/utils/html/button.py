""" HTMLボタン生成のモジュールです。"""


def create_button(
            url:str='',
            msg:str='',
            disable:bool=False,
            target:str='_self',
            a_character_color:str='#ffffff',
            a_font_size:str='15px',
            button_width:str='300px',
            button_height:str='30px',
            button_border_radius:str='5px',
            border:list[str] = [],
            button_background_color:str='#0072B5',
) -> str:
    """ HTMLのボタンを作成する関数です。

    Args:
        url (str): ボタンがクリックされたときに遷移するURLを設定します。
        msg (str): ボタン上に表示するメッセージを設定します。
        disable (bool): ボタンを無効化するかどうかを設定します。Trueの場合、ボタンは無効化されます。
        target (str): リンクの開き方を指定します。'_self'は同じタブで開くことを意味します。
        a_character_color (str): ボタンの文字色を指定します。
        a_font_size (str): ボタンのフォントサイズを指定します。
        button_width (str: ボタンの幅を指定します。
        button_height (str): ボタンの高さを指定します。
        button_border_radius (str): ボタンの角の丸みを指定します。
        border (list[str]): ボタンの枠線のスタイルを指定します。
        button_background_color (str): ボタンの背景色を指定します。

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
        return(
            f'<a style="font-size:{a_font_size};"href="{url}" target="{target}" >'
            f'<button style="width: {button_width}; height: {button_height};'
            f'border-radius: {button_border_radius}; background-color: {button_background_color};'
            f'border: {border_value}; color: {a_character_color};">{msg}</button></a>'
        )
    else:
        # disable button
        return(
            f'<button style="width: {button_width}; height: {button_height};'
            f'border-radius: {button_border_radius}; background-color: {button_background_color};'
            f'border: {border_value};" disable>{msg}</button>'
        )
