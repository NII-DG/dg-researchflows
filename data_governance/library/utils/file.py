""" ファイル操作のモジュールです。

JSONファイルを操作するためのクラスやファイルをコピーする関数が記載されています。

"""
import json
import os
import shutil
from pathlib import Path
from typing import Callable, Set


def copy_file(source_path: str, destination_path: str) -> None:
    """ ファイルをコピーする関数です。

    Args:
        source_path(str): コピー元ファイルパスを設定します。
        destination_path(str): コピー先ファイルパスを設定します。

    Note:
        既にファイルが存在する場合は上書きします。

    """
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    shutil.copyfile(source_path, destination_path)


def copy_dir(src: str, dst: str, overwrite: bool = False) -> None:
    """ ディレクトリをコピーする関数です。

    Args:
        src(str): コピー元ディレクトリを設定します。
        dst(str): コピー先ディレクトリを設定します。
        overwrite(bool): ファイルが既に存在する場合、上書きするかどうかを設定します。

    Note:
        指定したディレクトリがなければ作成される。

    """
    def f_exists(base: str, dst: str) -> Callable[[str, list[str]], Set[str]]:
        """ 指定したベースディレクトリと目的のディレクトリの間で存在するファイル名を返す関数です。

        Args:
            base(str): ベースとなるディレクトリのパスを設定します。
            dst(str): 比較対象のディレクトリのパスを設定します。

        Returns:
            Callable[[str, list[str]], Set[str]]: 相対的なディレクトリ名およびファイル名のセットを返す関数を返す。

        """
        base, dst = Path(base), Path(dst)

        # サブディレクトリー毎に呼び出される
        def _ignore(path: str, names: list[str]) -> Set[str]:
            """ 指定したパスと名前で存在するファイル名のセットを返す関数です。

            Args:
                path(str): サブディレクトリのパスを設定します。
                names(list[str]): サブディレクトリ内のファイル名のリストを設定します。

            Returns:
                set[str]: ベースディレクトリと目的ディレクトリの間で存在するファイル名のセットを返す。

            """
            names = set(names)
            rel = Path(path).relative_to(base)
            return {f.name for f in (dst / rel).glob('*') if f.name in names}
        return _ignore

    if overwrite:
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        shutil.copytree(src, dst, ignore=f_exists(src, dst), dirs_exist_ok=True)


def relative_path(target_path: str, start_dir: str) -> str:
    """ target_pathをstart_dirからの相対パスに変換する関数です。

    Args:
        target_path (str): 変換したいパスを設定します。
        start_dir (str): 基準となるディレクトリのパスを設定します。

    Returns:
        str: start_dirからtarget_pathまでの相対パスを返す。

    """
    if target_path and start_dir:
        return os.path.relpath(
            path=os.path.normpath(target_path),
            start=os.path.normpath(start_dir)
        )
    else:
        return ""


class File:
    """ ファイル操作のクラスです。

    ファイルの読み書きや作成、削除をします。

    Attributes:
        instance:
            path(Path): ファイルのパスを返す。

    """

    def __init__(self, file_path: str) -> None:
        """ クラスのインスタンスの初期化処理を実行するメソッドです。

        Args:
            file_path(str): ファイルパスを設定します。

        """
        self.path = Path(file_path)

    def read(self) -> str:
        """ ファイルから内容を読み込み、その内容を返すメソッドです。

        Returns:
            str: ファイルの内容を返す。

        """
        with self.path.open('r') as file:
            content = file.read()
        return content

    def write(self, content: str) -> None:
        """ 指定された内容をファイルに書き込むメソッドです。

        Args:
            content(str): 書き込む内容を設定します。

        """
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('w') as file:
            file.write(content)

    def create(self, exist_ok=True) -> None:
        """ 新しいファイルを作成するメソッドです。

        Args:
            exist_ok(bool): 既存のディレクトリを指定してエラーにならないかを設定します。

        """
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=exist_ok)

    def remove(self, missing_ok=False) -> None:
        """ ファイルを削除するメソッドです。

        Args:
            missing_ok(bool): 存在しないファイルを指定してエラーにならないかを設定します。

        """
        self.path.unlink(missing_ok)


class JsonFile(File):
    """ JSONファイル操作のクラスです。

    JSONファイルの読み込みや書き込みをします。

    """

    def __init__(self, file_path: str) -> None:
        """ クラスのインスタンスの初期化処理を実行するメソッドです。

        Args:
            file_path(str): ファイルパスを設定します。

        """
        super().__init__(file_path)

    def read(self) -> dict:
        """ ファイルの内容をjsonとして読み込むメソッドです。

        Returns:
            dict: ファイルの内容を返す。

        """
        content = super().read()
        return json.loads(content)

    def write(self, content: dict) -> None:
        """ 与えられた内容をjsonとしてファイルに書き込むメソッドです。

        Args:
            content(dict): 書き込む内容を設定します。

        """
        json_data = json.dumps(content, ensure_ascii=False, indent=4)
        super().write(json_data)
