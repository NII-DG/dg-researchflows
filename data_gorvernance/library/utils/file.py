""" ファイル操作のモジュールです。

"""
import os
import shutil
import json
from pathlib import Path


def copy_file(source_path, destination_path):
    """ ファイルをコピーする関数です。

    引数1のファイルを引数2へコピーする関数です。

    Args:
        source_path(str): コピー元ファイルパスを設定します。
        destination_path(str): コピー先ファイルパスを設定します。

    Note:
        既にファイルが存在する場合は上書きします。

    """
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    shutil.copyfile(source_path, destination_path)


def copy_dir(src, dst, overwrite=False):
    """ src から dst へディレクトリをコピーする関数です。

    Args:
        src(str): コピー元ディレクトリを設定します。
        dst(str): コピー先ディレクトリを設定します。
        overwrite(bool): ファイルが既に存在する場合、上書きするかどうかを設定します。

    Note:
        指定したディレクトリがなければ作成される。

    """
    def f_exists(base, dst):
        """ わかりません

        Args:
            base(str):
            dst(str):

        Returns:
            str:
        """
        base, dst = Path(base), Path(dst)
        def _ignore(path, names):   # サブディレクトリー毎に呼び出される
            """ わかりません

            Args:
                path(str):
                names(str):

            Returns:
                set[str]:
            """
            names = set(names)
            rel = Path(path).relative_to(base)
            return {f.name for f in (dst/ rel).glob('*') if f.name in names}
        return _ignore

    if overwrite:
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        shutil.copytree(src, dst, ignore=f_exists(src, dst), dirs_exist_ok=True)


def relative_path(target_path, start_dir):
    """ target_pathをstart_dirからの相対パスに変換する関数です。

    Args:
        target_path (str): 変換したいパスを設定します。
        start_dir (str): 基準となるディレクトリのパスを設定します。

    Returns:
        str: start_dirからtarget_pathまでの相対パス

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

    Attributes:
        instance:
            path(Path): ファイルのパス


    """

    def __init__(self, file_path: str):
        """ クラスのインスタンスの初期化処理を実行するメソッドです。

        Args:
            file_path(str): ファイルパスを設定します。

        """
        self.path = Path(file_path)

    def read(self):
        """ ファイルから内容を読み込み、その内容を返すメソッドです。

        Returns:
            str: ファイルの内容を返す。

        """
        with self.path.open('r') as file:
            content = file.read()
        return content

    def write(self, content: str):
        """ 指定された内容をファイルに書き込むメソッドです。

        Args:
            content(str): 書き込む内容を設定します。

        """
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('w') as file:
            file.write(content)

    def create(self, exist_ok=True):
        """ 新しいファイルを作成するメソッドです。

        Args:
            exist_ok(bool): 既存のディレクトリを指定してエラーにならないかを設定します。

        """
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=exist_ok)

    def remove(self, missing_ok=False):
        """ ファイルを削除するメソッドです。

        Args:
            missing_ok(bool): 存在しないファイルを指定してエラーにならないかを設定します。

        """
        self.path.unlink(missing_ok)


class JsonFile(File):
    """ JSONファイルを読み書きするクラスです。

    """
    def __init__(self, file_path: str):
        """ クラスのインスタンスの初期化処理を実行するメソッドです。

        Args:
            file_path(str): ファイルパスを設定します。
        """
        super().__init__(file_path)

    def read(self):
        """ ファイルの内容をjsonとして読み込むメソッドです。

        Returns:
            dict: ファイルの内容を返す。
        """
        content = super().read()
        return json.loads(content)

    def write(self, data:dict):
        """ 与えられた内容をjsonとしてファイルに書き込むメソッドです。

        Args:
            data(dict): 書き込む内容を設定します。
        """
        json_data = json.dumps(data, ensure_ascii=False, indent=4)
        super().write(json_data)
