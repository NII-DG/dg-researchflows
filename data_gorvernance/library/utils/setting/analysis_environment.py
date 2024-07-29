"""解析環境の取得に関するモジュールです。
特定の解析環境の情報を取得するためのメソッドが記載されています。
"""
import os
from pathlib import Path

from ..file import JsonFile

# analysis_environment.jsonのファイルパス
json_path = Path(os.path.dirname(__file__)).joinpath('../../data/analysis_environment.json').resolve()


class AnalysisEnvironment:
    """解析環境の情報を取得するためのメソッドを記載したクラスです。

    ジェイソンファイルを読み出し、特定の解析環境の情報を取得するためのメソッドが記載されています。

    Attributes:
        class:
            __FIELD:解析環境
            __ID:解析環境のid
            __NAME:解析環境の名前
            __DESCRIPTION:解析環境の説明
            __IS_ACTIVE:アクティブかの判定を行う
        instance:
            analysis_environment:解析環境

    """
    __FIELD = 'analysis_environment'
    __ID = 'id'
    __NAME = 'env_name'
    __DESCRIPTION = 'description'
    __IS_ACTIVE = 'is_active'

    def __init__(self):
        """クラスのインスタンスの初期化を行うメソッドです。コンストラクタ

        パスで指定したジェイソンファイルを読み出し、そこから特定のフィールドの値を取り出しています。

        """
        contents = JsonFile(str(json_path)).read()
        self.analysis_environment = contents[self.__FIELD]

    def get_names(self):
        """環境名をリストで取得するメソッドです。

        コンストラクタで作成したフィールドから環境名を取得し、リストにして返します。

        Returns:
            list: 環境名のリスト

        """
        return [fld[self.__NAME] for fld in self.analysis_environment]

    def get_id(self, target_name):
        """特定の解析環境のidを取得するメソッドです。

        引数として渡された名前と一致する解析環境のidを取得して返します。

        Args:
            target_name (_type_): 目的の解析環境の名前

        Returns:
            戻り値のidの型がわかりませんでした。:target_nameに対応したid

        """
        for fld in self.analysis_environment:
            if fld[self.__NAME] == target_name:
                return fld[self.__ID]

    def get_description(self, target_name):
        """特定の解析環境の説明を取得するメソッドです。

        引数として渡された名前と一致する解析環境の説明を取得して返します。

        Args:
            target_name (_type_): 目的の解析環境の名前

        Returns:
            戻り値のdescriptionの型がわかりませんでした。:target_nameに対応した化石環境の説明

        """
        for fld in self.analysis_environment:
            if fld[self.__NAME] == target_name:
                return fld[self.__DESCRIPTION]