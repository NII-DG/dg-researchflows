""" ウィジェットを整形するモジュールです。"""
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


def open_data_folder(working_file: str, folder_name: str = "", button_name:str = "") -> pn.pane.HTML:
    """ 別タブでデータフォルダを開くボタンを表示する関数です。

    Args:
        working_file(str): 移動元のファイルパスを設定します。
        folder_name(str): 開くフォルダの名前
        button_name(str): ボタンに表示するテキスト

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

    if not button_name:
        button_name = msg_config.get('task', 'access_data_dir')

    button_width = 500
    obj = create_button(
        url=url,
        target='_blank',
        msg=button_name,
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

def create_file_selector_checkbox(files: list[str]) -> tuple[pn.Column, dict]:
    """
    ファイル選択のためのチェックボックスをツリー構造で作成する関数です。

    Args:
        files (list[str]): ファイルパスのリスト

    Returns:
        pn.Column: ファイル選択のフォーム
        dict: ファイルパスとチェックボックスの辞書
    """
    # ファイルパスと対応するCheckboxウィジェットのインスタンスを保持する辞書
    file_checkbox_map = {}

    # ツリー構造を作る
    tree = {}

    for file_path in files:
        parts = file_path.split(os.sep)
        current = tree
        for part in parts[:-1]:
            current = current.setdefault(part, {})

        display_name = os.path.basename(file_path)  # ファイル名のみ表示
        checkbox = pn.widgets.Checkbox(name=display_name, value=False, width=500)

        file_checkbox_map[file_path] = checkbox  # キーはフルパスのまま
        current[parts[-1]] = checkbox

    def build_panel(node):
        """
        再帰的にPanelオブジェクトを構築する関数
        node: dict
        """
        items = []
        for key, value in sorted(node.items()):
            if isinstance(value, dict):
                content = build_panel(value)
                card = pn.Accordion((key, content), width=500)
                card.active = []
                items.append(card)
            else:
                value.width = 500
                items.append(value)

        return pn.Column(*items, width=500)

    ui = build_panel(tree)
    return ui, file_checkbox_map


def create_copy_selector(working_file: str, folder_name: str = "") -> tuple[pn.Column, str, dict]:
    """コピーするファイルを選択するためのウィジェットを作成します。

    Args:
        working_file (str): コピー元のワーキングディレクトリ
        folder_name (str): コピー元のデータディレクトリのフォルダ名. Defaults to "".

    Returns:
        pn.Column: ファイル選択のフォーム
        str: コピー元サブフローのワーキングディレクトリからコピー元サブフローのデータディレクトリまでの相対パス
        dict: ファイルパスとチェックボックスの辞書
    """

    # homeからdataディレクトリまで
    data_dir = get_data_dir(working_file)
    working_dir = os.path.dirname(working_file)
    relative_path = os.path.relpath(data_dir, start=working_dir)
    if folder_name:
        relative_path = os.path.join(relative_path, folder_name)
    files = list_files_recursively(relative_path)

    # ファイル一覧からツリー構造のチェックボックスを作成
    ui, checkbox_dict = create_file_selector_checkbox(files)

    return ui, relative_path, checkbox_dict

def create_single_file_selector(working_file: str, folder_name: str = "") -> tuple[pn.Column, str, dict]:
    """ファイルを選択するためのウィジェットを作成します。
    ファイル選択はツリー構造のチェックボックスで、1つだけ選択可能に制御。

    Args:
        working_file (str): コピー元のワーキングディレクトリ
        folder_name (str): コピー元のデータディレクトリのフォルダ名. Defaults to "".

    Returns:
        pn.Column: ファイル選択のフォーム
        str: コピー元サブフローのワーキングディレクトリからコピー元サブフローのデータディレクトリまでの相対パス
        dict: ファイルパスとチェックボックスの辞書
    """

    data_dir = get_data_dir(working_file)
    working_dir = os.path.dirname(working_file)
    relative_path = os.path.relpath(data_dir, start=working_dir)
    if folder_name:
        relative_path = os.path.join(relative_path, folder_name)
    files = list_files_recursively(relative_path)

    ui, checkbox_dict = create_file_selector_checkbox(files)

    # 一つだけ選択できるようにチェックボックスの相互排他制御をセット
    def checkbox_callback(event):
        # どれかがTrueになったら他をFalseにする
        if event.new:
            for path, cb in checkbox_dict.items():
                if cb is not event.obj:
                    cb.value = False

    for file_path, checkbox in checkbox_dict.items():
        checkbox.file_path = os.path.abspath(os.path.join(relative_path, file_path))
        checkbox.param.watch(checkbox_callback, 'value')

    ui = pn.Column(
        pn.pane.Markdown("### ファイルを選択してください", width=500),
        ui,
        width=500
    )

    return ui, relative_path, checkbox_dict
