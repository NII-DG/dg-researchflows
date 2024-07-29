"""ocs_template.jsonのファイルのデータを扱うモジュールです。
OCSテンプレートデータの操作を行うクラスを記載しています。
"""
import os
from pathlib import Path
from typing import List

from ..file import JsonFile

# ocs_template.jsonのファイルパス
script_dir_path = os.path.dirname(__file__)
p = Path(script_dir_path)
ocs_template_json_file = p.joinpath('../../data/ocs-template.json').resolve()

class OCSTemplate:
    """ocs_template.jsonのファイルのデータを扱うクラスです。

    OCSテンプレートのリスト作成やパスの取り出しなどOCSテンプレートデータの操作を行うメソッドを記載しています。

    Attributes:
        class:
            __FIELD:OCSテンプレートデータ
            __ID:id
            __FIELD_NAME:OCSテンプレート名
            __OCS_TEMPLATE_PATH:OCSテンプレートパス
            __IS_ACTIVE:アクティブかの判定を行う
        instance:
           ocs_template:OCSテンプレートデータを保存する。

    """
    __FIELD = "ocs_template"
    __ID = "id"
    __FIELD_NAME = "ocs_template_name"
    __OCS_TEMPLATE_PATH = "ocs_template_path"
    __IS_ACTIVE = "is_active"

    def __init__(self) -> None:
        """クラスのインスタンスの初期化を行うメソッドです。コンストラクタ

        ocs_template.jsonのファイルを読み出し、フィールドのデータを自身のインスタンスに保存します。

        """
        contents = JsonFile(str(ocs_template_json_file)).read()
        self.ocs_template = contents[self.__FIELD]

    def get_name(self):
        """OCSテンプレート名のリストを作成するメソッドです。

        コンストラクタでインスタンスに保存したデータからocs_template_nameに対応するデータをリストとして取り出します。

        Returns:
            list:OCSテンプレート名のリスト

        """
        return [fld[self.__FIELD_NAME] for fld in self.ocs_template]

    def get_disabled_ids(self)->List[str]:
        """アクティブでないデータのリストを作成するメソッドです。

        OCSテンプレートデータがアクティブな状態かを判別し、アクティブでないデータの名前をリストして返します。

        Returns:
            list[str]:アクティブでないOCSテンプレート名のリスト

        """
        disabled = []
        for fld in self.ocs_template:
            if not fld[self.__IS_ACTIVE]:
                disabled.append(fld[self.__FIELD_NAME])
        return disabled

    def get_id(self, target_name):
        """指定したOCSテンプレートのIDを取得するメソッドです。

        引数として受けとったtarget_nameと一致するOCSテンプレート名のOCSテンプレートのIDを取得し、戻り値として返します。

        Args:
            target_name (Any):目的のOCSテンプレートIDを指定するOCSテンプレート名

        Returns:
            戻り値の型が分かりませんでした。:目的のOCSテンプレートID

        """
        for fld in self.ocs_template:
            if fld[self.__FIELD_NAME] == target_name:
                return fld[self.__ID]

    def get_template_path(self, target_name):
        """指定したOCSテンプレートパスを取得するメソッドです。

        引数として受けとったtarget_nameと一致するOCSテンプレート名のOCSテンプレートパスを取得し、戻り値として返します。

        Args:
            target_name (Any):目的のOCSテンプレートパスを指定するOCSテンプレート名

        Returns:
            戻り値の型が分かりませんでした。:目的のOCSテンプレート名

        """
        for fld in self.ocs_template:
            if fld[self.__FIELD_NAME] == target_name:
                return fld[self.__OCS_TEMPLATE_PATH]
