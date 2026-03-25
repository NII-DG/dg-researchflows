"""access.pyのテストモジュールです。"""
# tox exec -- pytest tests/utils/test_access.py -s -vv
import os
import pytest
import urllib.parse

import panel as pn

from data_governance.library.utils import access
from data_governance.library.utils.access import open_main_menu, open_data_folder, open_data_file,create_file_selector_checkbox, list_files_recursively, create_copy_selector, create_single_file_selector


# def open_main_menu(working_file: str) -> None:
# tox exec -- pytest tests/utils/test_access.py::test_open_main_menu -s -vv
def test_open_main_menu(mocker, tmp_path):
    """open_main_menuの正常系テスト。"""
    # ...各種モック...
    display_mock = mocker.patch("data_governance.library.utils.access.display")
    html_mock = mocker.patch("panel.pane.HTML", return_value="HTML_OBJ")
    # ダミーJavascriptクラス
    class DummyJS:
        def __init__(self, data):
            self.data = data
    js_mock = mocker.patch("data_governance.library.utils.access.Javascript", side_effect=DummyJS)
    # 実行
    open_main_menu(str(tmp_path / "notebook.ipynb"))
    # displayが2回呼ばれる
    assert display_mock.call_count == 2
    args1, _ = display_mock.call_args_list[0]
    args2, _ = display_mock.call_args_list[1]
    assert args1[0] == "HTML_OBJ"
    # 2回目はDummyJSインスタンス
    assert isinstance(args2[0], DummyJS)
    html_mock.assert_called_once()
    js_mock.assert_called_once_with('IPython.notebook.save_checkpoint();')


# def open_data_folder(working_file: str, folder_name: str = "", button_name:str = "") -> pn.pane.HTML:
# tox exec -- pytest tests/utils/test_access.py::test_open_data_folder -s -vv
def test_open_data_folder(monkeypatch, mocker, tmp_path):
    """open_data_folderの正常系テスト。"""
    # 準備
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("HOME", str(tmp_path))
    mocker.patch("data_governance.library.utils.access.get_data_dir", return_value=str(data_dir))
    mocker.patch("data_governance.library.utils.file.relative_path", side_effect=lambda a, b: os.path.relpath(a, b))
    create_button_mock = mocker.patch("data_governance.library.utils.access.create_button", return_value="<button>")
    html_mock = mocker.patch("panel.pane.HTML", side_effect=lambda obj, width=None: type("Dummy", (), {"object": obj})())

    # button_name未指定
    working_file = str(tmp_path / "notebook.ipynb")
    html = open_data_folder(working_file)
    # create_buttonの呼び出し引数を確認
    args, kwargs = create_button_mock.call_args
    assert kwargs["url"].endswith("data")  # urlの末尾がdata
    assert kwargs["target"] == "_blank"
    assert kwargs["button_width"] == "500px"
    # htmlモックの引数にcreate_button_mockの返り値が渡されている
    assert html_mock.call_args[0][0] == "<button>"
    # 戻り値がHTMLモック
    assert hasattr(html, "object")

    # button_name指定
    html2 = open_data_folder(working_file, folder_name="f", button_name="b")
    args2, kwargs2 = create_button_mock.call_args
    assert "f" in kwargs2["url"]
    assert kwargs2["msg"] == "b"
    assert html_mock.call_args[0][0] == "<button>"
    assert hasattr(html2, "object")


# def open_data_file(working_file:str, file_path:str) -> pn.pane.HTML:
# tox exec -- pytest tests/utils/test_access.py::test_open_data_file -s -vv
def test_open_data_file(monkeypatch, mocker, tmp_path):
    """open_data_fileの正常系テスト。"""
    # 準備
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("HOME", str(tmp_path))
    mocker.patch("data_governance.library.utils.access.get_data_dir", return_value=str(data_dir))
    mocker.patch("data_governance.library.utils.file.relative_path", side_effect=lambda a, b: os.path.relpath(a, b))
    create_button_mock = mocker.patch("data_governance.library.utils.access.create_button", return_value="<button>")
    html_mock = mocker.patch("panel.pane.HTML", side_effect=lambda obj, width=None: type("Dummy", (), {"object": obj})())
    mocker.patch.object(access.msg_config, "get", return_value="msg")

    # テスト
    working_file = str(tmp_path / "notebook.ipynb")
    file_path = "foo/日本語 file.txt"
    html = open_data_file(working_file, file_path)
    # create_buttonの呼び出し引数を確認
    args, kwargs = create_button_mock.call_args
    # urlにエンコード済みfile_pathが含まれる
    assert urllib.parse.quote(file_path) in kwargs["url"]
    assert kwargs["target"] == "_blank"
    assert kwargs["button_width"] == "500px"
    # msg_config.getで取得した値がmsgに使われている
    assert kwargs["msg"] == "msg"
    # htmlモックの引数にcreate_button_mockの返り値が渡されている
    assert html_mock.call_args[0][0] == "<button>"
    # 戻り値がHTMLモック
    assert hasattr(html, "object")


# def create_file_selector_checkbox(files: list[str]) -> tuple[pn.Column, dict]:
# tox exec -- pytest tests/utils/test_access.py::test_create_file_selector_checkbox_various -s -vv
@pytest.mark.parametrize(
    "files, expected_keys",
    [
        # 単純なファイルリスト
        (["a.txt", "b.txt"], {"a.txt", "b.txt"}),
        # 重複ファイル名
        (["dup.txt", "dup.txt", "sub/dup.txt", "sub/dup.txt"], {"dup.txt", "sub/dup.txt"}),
    ]
)
def test_create_file_selector_checkbox_various(files, expected_keys):
    """
    ファイル名のバリエーションごとにCheckbox生成を確認。
    """
    ui, file_checkbox_map = create_file_selector_checkbox(files)
    assert isinstance(ui, pn.Column)
    assert set(file_checkbox_map.keys()) == expected_keys
    for fname in expected_keys:
        cb = file_checkbox_map[fname]
        assert isinstance(cb, pn.widgets.Checkbox)
        # nameはパス区切りの最後
        assert cb.name == fname.split("/")[-1]
        assert cb.value is False
        assert cb.width == 500


# def create_file_selector_checkbox(files: list[str]) -> tuple[pn.Column, dict]:
# tox exec -- pytest tests/utils/test_access.py::test_create_file_selector_checkbox_with_subdir -s -vv
def test_create_file_selector_checkbox_with_subdir():
    """
    サブディレクトリを含むファイルリストを渡した場合に、
    ツリー構造（Accordion）とCheckboxが正しく生成されることを確認するテストケースです。
    """
    files = ["a.txt", "subdir/b.txt", "subdir/c.txt"]
    ui, file_checkbox_map = create_file_selector_checkbox(files)
    # すべてのファイルがmapに含まれる
    assert set(file_checkbox_map.keys()) == {"a.txt", "subdir/b.txt", "subdir/c.txt"}
    # サブディレクトリ内のCheckboxも正しく生成されている
    for fname in files:
        cb = file_checkbox_map[fname]
        assert isinstance(cb, pn.widgets.Checkbox)
        assert cb.value is False
        assert cb.width == 500
    # Accordionが含まれる（サブディレクトリ用）
    accordions = [child for child in ui if isinstance(child, pn.Accordion)]
    assert len(accordions) == 1
    accordion = accordions[0]
    # Accordionのラベルが'subdir'であること
    assert accordion._names[0] == "subdir"
    # Accordionの中身（pn.Column）を取得
    subdir_column = accordion.objects[0]
    # subdir_columnの中にb.txt, c.txtのCheckboxが含まれること
    checkbox_names = set(w.name for w in subdir_column if isinstance(w, pn.widgets.Checkbox))
    assert checkbox_names == {"b.txt", "c.txt"}


# def create_file_selector_checkbox(files: list[str]) -> tuple[pn.Column, dict]:
# tox exec -- pytest tests/utils/test_access.py::test_create_file_selector_checkbox_multi_subdir_unordered -s -vv
def test_create_file_selector_checkbox_multi_subdir_unordered():
    """
    複数サブディレクトリ・順不同ファイルリストでツリー構造が正しく生成されることを確認するテストケースです。
    """
    files = [
        "foo/bar/c.txt",
        "baz/d.txt",
        "baz/bar/e.txt",
        "foo/bar/a.txt"
    ]
    ui, file_checkbox_map = create_file_selector_checkbox(files)
    # すべてのファイルがmapに含まれる
    assert set(file_checkbox_map.keys()) == set(files)
    # Checkboxの基本属性
    for fname in files:
        cb = file_checkbox_map[fname]
        assert isinstance(cb, pn.widgets.Checkbox)
        assert cb.value is False
        assert cb.width == 500

    # Accordionのラベルを収集
    accordions = [child for child in ui if isinstance(child, pn.Accordion)]
    labels = set(acc._names[0] for acc in accordions)
    assert labels == {"foo", "baz"}

    # foo/barのAccordionの中にc.txt, a.txtがあること
    foo_acc = next(acc for acc in accordions if acc._names[0] == "foo")
    foo_column = foo_acc.objects[0]
    # foo_columnの中にbarのAccordionがある
    foo_bar_acc = next(child for child in foo_column if isinstance(child, pn.Accordion))
    assert foo_bar_acc._names[0] == "bar"
    foo_bar_column = foo_bar_acc.objects[0]
    foo_bar_names = set(w.name for w in foo_bar_column if isinstance(w, pn.widgets.Checkbox))
    assert foo_bar_names == {"c.txt", "a.txt"}

    # bazのAccordionの中にd.txtとbarのAccordionがある
    baz_acc = next(acc for acc in accordions if acc._names[0] == "baz")
    baz_column = baz_acc.objects[0]
    # d.txtが含まれる
    assert any(isinstance(w, pn.widgets.Checkbox) and w.name == "d.txt" for w in baz_column)
    # barのAccordionが含まれる
    baz_bar_acc = next(child for child in baz_column if isinstance(child, pn.Accordion))
    assert baz_bar_acc._names[0] == "bar"
    baz_bar_column = baz_bar_acc.objects[0]
    baz_bar_names = set(w.name for w in baz_bar_column if isinstance(w, pn.widgets.Checkbox))
    assert baz_bar_names == {"e.txt"}


# def create_file_selector_checkbox(files: list[str]) -> tuple[pn.Column, dict]:
# tox exec -- pytest tests/utils/test_access.py::test_create_file_selector_checkbox_empty -s -vv
def test_create_file_selector_checkbox_empty():
    """
    空リストを渡した場合に、空のpn.Columnと空辞書が返ることを確認するテストケースです。
    """
    files = []
    ui, file_checkbox_map = create_file_selector_checkbox(files)
    assert isinstance(ui, pn.Column)
    assert len(list(ui)) == 0
    assert file_checkbox_map == {}


# def list_files_recursively(base_path):
# tox exec -- pytest tests/utils/test_access.py::test_list_files_recursively_cases -s -vv
@pytest.mark.parametrize(
    "structure, expected",
    [
        # 空ディレクトリ
        ({}, []),
        # 単一ファイル
        ({"file.txt": "x"}, ["file.txt"]),
        # サブディレクトリと複数ファイル
        ({"file1.txt": "1", "sub/file2.txt": "2"}, ["file1.txt", os.path.join("sub", "file2.txt")]),
    ]
)
def test_list_files_recursively_cases(tmp_path, structure, expected):
    # ディレクトリ構造を作成
    for rel_path, content in structure.items():
        fpath = tmp_path / rel_path
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(content)
    files = list_files_recursively(str(tmp_path))
    # 結果は順不同なのでsetで比較
    assert set(files) == set(expected)


# def create_copy_selector(working_file: str, folder_name: str = "") -> tuple[pn.Column, str, dict]:
# tox exec -- pytest tests/utils/test_access.py::test_create_copy_selector -s -vv
@pytest.mark.parametrize(
    "folder_name, files_to_create, expected_keys",
    [
        ("", ["file1.txt", "file2.txt"], {"file1.txt", "file2.txt"}),
        ("argument_data", ["argument_data/argfile1.txt", "argument_data/argfile2.txt"], {"argfile1.txt", "argfile2.txt"}),
    ]
)
def test_create_copy_selector(tmp_path, monkeypatch, mocker, folder_name, files_to_create, expected_keys):
    """
    create_copy_selectorの正常系テスト（パラメータ化）。
    folder_nameとファイル名集合の組み合わせで返り値の型・パス・checkbox_dictの内容を確認。
    """

    # working_fileのパス
    working_file = tmp_path / "data_governance" / "notebook.ipynb"
    working_file.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(os.path.dirname(working_file))

    # data_dirのパス
    data_dir = tmp_path / "data" / "writing" / "subdir"
    # ファイル作成
    for rel_path in files_to_create:
        fpath = data_dir / rel_path
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text("dummy")

    # get_data_dirのモック: working_fileからdata_dirを返す
    mocker.patch("data_governance.library.utils.access.get_data_dir", return_value=str(data_dir))

    ui, relative_path, checkbox_dict = create_copy_selector(working_file, folder_name)
    assert isinstance(relative_path, str)
    assert isinstance(checkbox_dict, dict)
    assert isinstance(ui, pn.Column)
    # folder_name指定時はrelative_pathに含まれる
    if folder_name:
        assert relative_path.endswith(folder_name)
    # ファイル名がdictに含まれる
    assert set(checkbox_dict.keys()) == expected_keys
    for cb in checkbox_dict.values():
        assert isinstance(cb, pn.widgets.Checkbox)


# def create_single_file_selector(working_file: str, folder_name: str = "") -> tuple[pn.Column, str, dict]:
# tox exec -- pytest tests/utils/test_access.py::test_create_single_file_selector -s -vv
@pytest.mark.parametrize(
    "folder_name, files_to_create, expected_keys",
    [
        ("", ["file1.txt", "file2.txt"], {"file1.txt", "file2.txt"}),
        ("argument_data", ["argument_data/argfile1.txt", "argument_data/argfile2.txt"], {"argfile1.txt", "argfile2.txt"}),
    ]
)
def test_create_single_file_selector(tmp_path, monkeypatch, mocker, folder_name, files_to_create, expected_keys):
    """
    create_single_file_selectorの正常系テスト（パラメータ化）。
    folder_nameとファイル名集合の組み合わせで返り値の型・パス・checkbox_dictの内容を確認。
    1つだけ選択可能なチェックボックスの相互排他制御はここでは属性確認のみ。
    """

    # working_fileのパス
    working_file = tmp_path / "data_governance" / "notebook.ipynb"
    working_file.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(os.path.dirname(working_file))

    # data_dirのパス
    data_dir = tmp_path / "data" / "writing" / "subdir"
    expected_abs_paths = set()
    # ファイル作成
    for rel_path in files_to_create:
        fpath = data_dir / rel_path
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text("dummy")
        expected_abs_paths.add(str(fpath.resolve()))

    # get_data_dirのモック: working_fileからdata_dirを返す
    mocker.patch("data_governance.library.utils.access.get_data_dir", return_value=str(data_dir))

    ui, relative_path, checkbox_dict = create_single_file_selector(working_file, folder_name)
    assert isinstance(relative_path, str)
    assert isinstance(checkbox_dict, dict)
    assert isinstance(ui, pn.Column)
    # folder_name指定時はrelative_pathに含まれる
    if folder_name:
        assert relative_path.endswith(folder_name)
    # ファイル名がdictに含まれる
    assert set(checkbox_dict.keys()) == expected_keys
    for cb in checkbox_dict.values():
        assert isinstance(cb, pn.widgets.Checkbox)
        # チェックボックスの初期値
        assert cb.value is False
        assert cb.width == 500
        # file_path属性が存在すること
        assert cb.file_path in expected_abs_paths


# def create_single_file_selector(working_file: str, folder_name: str = "") -> tuple[pn.Column, str, dict]:
# tox exec -- pytest tests/utils/test_access.py::test_create_single_file_selector_checkbox_callback -s -vv
def test_create_single_file_selector_checkbox_callback(monkeypatch, mocker, tmp_path):
    """create_single_file_selectorで生成されるチェックボックスの相互排他制御が正しくセットされていることを確認するテストケースです。"""
    # セレクタ生成
    working_file = tmp_path / "notebook.ipynb"
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "a.txt").write_text("a")
    (data_dir / "b.txt").write_text("b")
    mocker.patch("data_governance.library.utils.access.get_data_dir", return_value=str(data_dir))
    monkeypatch.chdir(tmp_path)
    ui, rel_path, checkbox_dict = access.create_single_file_selector(str(working_file))

    # 2つのチェックボックスを取得
    cb1 = checkbox_dict["a.txt"]
    cb2 = checkbox_dict["b.txt"]

    # cb1をTrueに→cb2はFalseのまま
    cb1.value = True
    assert cb1.value is True
    assert cb2.value is False

    # cb2をTrueに→cb1はFalseになる
    cb2.value = True
    assert cb2.value is True
    assert cb1.value is False














