
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
            button_background_color='#2185d0',
):
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
