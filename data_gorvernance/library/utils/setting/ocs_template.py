"""ocs_template.jsonのファイルのデータを扱うモジュールです。"""
import os
from pathlib import Path
from typing import List

from ..file import JsonFile

# ocs_template.jsonのファイルパス
script_dir_path = os.path.dirname(__file__)
p = Path(script_dir_path)
ocs_template_json_file = p.joinpath('../../data/ocs-template.json').resolve()

class OCSTemplate:
    """ocs_template.jsonファイルのデータを操作するメソッドを記載したクラスです。

    Attributes:
        class:
            __FIELD(str):OCSテンプレートデータのキー名
            __ID(str):idのキー名
            __FIELD_NAME(str):OCSテンプレート名のキー名
            __OCS_TEMPLATE_PATH(str):OCSテンプレートパスのキー名
            __IS_ACTIVE(str):アクティブ状態かの判定に用いるフラグのキー名
        instance:
           ocs_template(list(object)):OCSテンプレートデータのリスト

    """
    __FIELD = "ocs_template"
    __ID = "id"
    __FIELD_NAME = "ocs_template_name"
    __OCS_TEMPLATE_PATH = "ocs_template_path"
    __IS_ACTIVE = "is_active"

    def __init__(self) -> None:
        """クラスのインスタンスの初期化を行うメソッドです。コンストラクタ

        ocs_template.jsonファイルのデータを扱う際に共通の処理である読み出し行います。

        """
        contents = JsonFile(str(ocs_template_json_file)).read()
        self.ocs_template = contents[self.__FIELD]

    def get_name(self)->list[str]:
        """OCSテンプレート名のリストを作成するメソッドです。

        Returns:
            list:OCSテンプレート名のリスト

        """
        return [fld[self.__FIELD_NAME] for fld in self.ocs_template]

    def get_disabled_ids(self)->List[str]:
        """アクティブ状態でないデータのリストを作成するメソッドです。

        Returns:
            list[str]:アクティブ状態でないOCSテンプレート名のリスト

        """
        disabled = []
        for fld in self.ocs_template:
            if not fld[self.__IS_ACTIVE]:
                disabled.append(fld[self.__FIELD_NAME])
        return disabled

    def get_id(self, target_name:str)->str:
        """指定したOCSテンプレートのIDを取得するメソッドです。

        Args:
            target_name (str):目的のOCSテンプレートIDを指定するOCSテンプレート名

        Returns:
            str:目的のOCSテンプレートID

        """
        for fld in self.ocs_template:
            if fld[self.__FIELD_NAME] == target_name:
                return fld[self.__ID]

    def get_template_path(self, target_name:str)->str:
        """指定したOCSテンプレートのパスを取得するメソッドです。

        Args:
            target_name (str):目的のOCSテンプレートパスを指定するOCSテンプレート名

        Returns:
            str:目的のOCSテンプレート名

        """
        for fld in self.ocs_template:
            if fld[self.__FIELD_NAME] == target_name:
                return fld[self.__OCS_TEMPLATE_PATH]
