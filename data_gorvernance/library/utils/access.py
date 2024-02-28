import os
from pathlib import Path

import panel as pn
from IPython.display import display
from IPython.core.display import Javascript

from .html.button import create_button
from .config import path_config, message as msg_config
from library.utils.setting import get_data_dir
from . import file




def open_main_menu(working_file):
    """別タブでメインメニューを開くボタンを表示する

    Args:
        working_file (str): 移動元のファイルパス
    """
    button_width = 500
    root_folder = Path(
        path_config.get_abs_root_form_working_dg_file_path(working_file)
    )
    main_menu = str(root_folder / path_config.MAIN_MENU_PATH)

    link = file.relative_path(main_menu, os.path.dirname(working_file))
    obj = create_button(
        url=f'{link}?init_nb=true',
        target='_blank',
        msg=msg_config.get('subflow_menu', 'access_main_menu'),
        button_width=f'{button_width}px'
    )
    pn.extension()
    display(pn.pane.HTML(obj, width=button_width))
    display(Javascript('IPython.notebook.save_checkpoint();'))


def open_data_folder(working_file):
    home = os.environ['HOME']
    # homeからdataディレクトリまで
    data_dir = get_data_dir(working_file)
    data_dir = file.relative_path(data_dir, home)
    # 現在地からhomeまで
    script_dir = os.path.dirname(working_file)
    script_dir = file.relative_path(home, script_dir)
    # ディレクトリを表示するのでtreeにする
    url = os.path.join(script_dir, '../tree/', data_dir)
    button_width = 500
    obj = create_button(
        url=url,
        target='_blank',
        msg=msg_config.get('task', 'access_data_dir'),
        button_width=f'{button_width}px'
    )
    pn.extension()
    display(pn.pane.HTML(obj, width=button_width))
    display(Javascript('IPython.notebook.save_checkpoint();'))


