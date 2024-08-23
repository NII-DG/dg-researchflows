"""解析環境の情報を取得するためのメソッドを記載したモジュールです。"""
import os
from pathlib import Path

from library.utils.file import JsonFile


# analysis_environment.jsonのファイルパス
json_path = Path(os.path.dirname(__file__)).joinpath('../../data/analysis_environment.json').resolve()


class AnalysisEnvironment:
    """ジェイソンファイルを読み出し、特定の解析環境の情報を取得するためのメソッドを記載したクラスです。

    Attributes:
        class:
            __FIELD(str):解析環境のキー名
            __ID(str):解析環境のidのキー名
            __NAME(str):解析環境の名前のキー名
            __DESCRIPTION(str):解析環境の説明のキー名
            __IS_ACTIVE(str):アクティブかの判定に用いるフラグのキー名
        instance:
            analysis_environment(list「object]):解析環境のリスト

    """
    __FIELD = 'analysis_environment'
    __ID = 'id'
    __NAME = 'env_name'
    __DESCRIPTION = 'description'
    __IS_ACTIVE = 'is_active'

    def __init__(self):
        """クラスのインスタンスの初期化を行うメソッドです。コンストラクタ

        解析環境の情報を取得する際に共通の処理となるファイルの読み込みを行います。

        """
        contents = JsonFile(str(json_path)).read()
        self.analysis_environment = contents[self.__FIELD]

    def get_names(self) -> list:
        """保存されている環境名をリストで取得するメソッドです。

        Returns:
            list: 環境名のリスト

        """
        return [fld[self.__NAME] for fld in self.analysis_environment]

    def get_id(self, target_name: str) -> str:
        """指定した解析環境のidを取得するメソッドです。

        Args:
            target_name (str): 目的の解析環境の名前

        Returns:
            str:target_nameに対応したid

        """
        for fld in self.analysis_environment:
            if fld[self.__NAME] == target_name:
                return fld[self.__ID]

    def get_description(self, target_name: str) -> str:
        """指定した解析環境の概要を取得するメソッドです。

        Args:
            target_name (str): 目的の解析環境の名前

        Returns:
            str:target_nameに対応した解析環境の説明

        """
        for fld in self.analysis_environment:
            if fld[self.__NAME] == target_name:
                return fld[self.__DESCRIPTION]
