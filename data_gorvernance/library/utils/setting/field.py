"""field.jsonファイルのデータを操作するクラスを記載したモジュールです。"""
import os
from pathlib import Path
from typing import List

from ..file import JsonFile

# field.jsonのファイルパス
script_dir_path = os.path.dirname(__file__)
p = Path(script_dir_path)
field_json_file = p.joinpath('../../data/field.json').resolve()

class Field:
    """field.jsonファイルのデータ操作を行うメソッドを記載したクラスです。

    Attributes:
        class:
            __FIELD(str):フィールドデータのキー名
            __ID(int):id
            __FIELD_NAME(str):フィールド名
            __EXPERIMENT_PACKAGE(str):実験パッケージ
            __IS_ACTIVE(str):アクティブかの判定を行う
        instance:
            field(list(object)):フィールドデータのキー名のリスト

    """
    __FIELD = "field"
    __ID = "id"
    __FIELD_NAME = "field_name"
    __EXPERIMENT_PACKAGE = "experiment_package"
    __IS_ACTIVE = "is_active"

    def __init__(self) -> None:
        """クラスのインスタンスの初期化を行うメソッドです。コンストラクタ

        field.jsonのファイルからフィールドデータを読み込みます。

        """
        contents = JsonFile(str(field_json_file)).read()
        self.field = contents[self.__FIELD]

    def get_name(self)->list[str]:
        """フィールド名のリストを作成するメソッドです。

        Returns:
            list[str]:フィールド名のリスト

        """
        return [fld[self.__FIELD_NAME] for fld in self.field]

    def get_disabled_ids(self)->List[str]:
        """アクティブ状態でないフィールドのリストを作成するメソッドです。

        Returns:
            list[str]:アクティブ状態でないフィールド名のリスト

        """
        disabled = []
        for fld in self.field:
            if not fld[self.__IS_ACTIVE]:
                disabled.append(fld[self.__FIELD_NAME])
        return disabled

    def get_template_path(self, target_name:str)->str:
        """指定したフィールド名の実験パッケージを取得するメソッドです。

        Args:
            target_name (str):目的の実験パッケージを指定するフィールド名

        Returns:
            str:目的の実験パッケージ

        """
        for fld in self.field:
            if fld[self.__FIELD_NAME] == target_name:
                return fld[self.__EXPERIMENT_PACKAGE]
