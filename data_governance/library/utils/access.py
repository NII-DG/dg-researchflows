""" タブを開くボタンを表示するモジュールです。"""
import os
from pathlib import Path

from IPython.display import display
from IPython.core.display import Javascript
import urllib
import panel as pn

from . import file
from .config import path_config, message as msg_config
from .html import create_button
from .setting import get_data_dir


def open_main_menu(working_file: str) -> None:
    """ 別タブでメインメニューを開くボタンを表示する関数です。

    Args:
        working_file(str): 移動元のファイルパスを設定します。

    """
    button_width = 500
    root_folder = Path(path_config.get_abs_root_form_working_dg_file_path(working_file))
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


def open_data_folder(working_file: str, folder_name:str = None) -> pn.pane.HTML:
    """ 別タブでデータフォルダを開くボタンを表示する関数です。

    Args:
        working_file(str): 移動元のファイルパスを設定します。
        folder_name(str): 開くフォルダの名前

    Return:
        pn.pane.HTML: 作成したボタンオブジェクト

    """
    home = os.environ['HOME']
    # homeからdataディレクトリまで
    data_dir = get_data_dir(working_file)
    data_dir = file.relative_path(data_dir, home)
    # 現在地からhomeまで
    script_dir = os.path.dirname(working_file)
    script_dir = file.relative_path(home, script_dir)
    # ディレクトリを表示するのでtreeにする
    url = os.path.join(script_dir, '../tree/', data_dir)

    #特定のフォルダ名が指定されていた場合
    if folder_name:
        url = os.path.join(url, folder_name)

    button_width = 500
    obj = create_button(
        url=url,
        target='_blank',
        msg=msg_config.get('task', 'access_data_dir'),
        button_width=f'{button_width}px'
    )
    return pn.pane.HTML(obj)

def open_data_file(working_file:str, file_path:str) -> pn.pane.HTML:
    """別タブでデータファイルを開くボタンを表示する関数です。

    Args:
        working_file(str) : 移動元のファイルパスを設定します。
        file_name(str): /home/jovyan/<フェーズ名>/<データフォルダ名>以下のファイル名を含むパス

    """

    home = os.environ['HOME']
    # homeからdataディレクトリまで
    data_dir = get_data_dir(working_file)
    data_dir = file.relative_path(data_dir, home)
    encoded_file_path = urllib.parse.quote(file_path)
    file_path = os.path.join(data_dir, encoded_file_path)
    # 現在地からhomeまで
    script_dir = os.path.dirname(working_file)
    script_dir = file.relative_path(home, script_dir)
    # ノートブックを表示するのでnotebooksにする
    url = os.path.join(script_dir, '../notebooks/', file_path)

    button_width = 500
    obj = create_button(
        url=url,
        target='_blank',
        msg=msg_config.get('task', 'access_notebook_file'),
        button_width=f'{button_width}px'
    )
    return pn.pane.HTML(obj)

def list_files_recursively(base_path):
    """
    base_path以下の全ファイルをサブディレクトリ構造を保持した相対パスで返す
    """
    file_list = []
    for root, dirs, files in os.walk(base_path):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, base_path)
            file_list.append(rel_path)
    return file_list

def create_copy_selector(working_file: str, folder_name: str = None):
    """コピーするファイルを選択するためのウィジェットを作成します。"""

    # homeからdataディレクトリまで
    data_dir = get_data_dir(working_file)
    working_dir = os.path.dirname(working_file)
    relative_path = os.path.relpath(data_dir, start=working_dir)

    files = list_files_recursively(relative_path)

    # チェックボックスを格納する辞書とリストを初期化
    checkbox_dict = {}
    # チェックボックスの表示要素をリストに追加
    checkbox_widgets = []

    for file in files:
        label = file
        checkbox = pn.widgets.Checkbox(name=label, value=False)
        checkbox_dict[label] = checkbox
        checkbox_widgets.append(checkbox)

            # チェックボックス群を縦に並べる
    checkbox_column = pn.Column(*checkbox_widgets)
    return checkbox_column, relative_path, checkbox_dict
