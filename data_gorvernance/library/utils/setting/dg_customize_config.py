"""DGカスタマイズJSON定義書に関するモジュールです。
データを解析し、インスタンスとして利用できるリストを作成するメソッドが記載されています。
"""
import os
from pathlib import Path
from typing import Any, Dict, List

from ..file import JsonFile

script_dir_path = os.path.dirname(__file__)
p = Path(script_dir_path)
# DGカスタマイズJSON定義書絶対パス(data_gorvernance\library\data\data_governance_customize.json)
data_governance_customize_file = p.joinpath('../../', 'data/data_governance_customize.json').resolve()


class AlphaProperty:
    """受け取ったサブフローに関するデータを解析し、保持するためのクラスです。

    このクラスでは受け取ったデータの解析を行い、idの取得と新たにSubFlowRule型のリストを作成します。

    Attributes:
        class:
           __ID:id
           __CUSTOMIZE:カスタマイズデータ
        instance:
            _customize:取り出したデータで初期化したリスト

    """
    __ID = 'id'
    __CUSTOMIZE = 'customize'

    def __init__(self, data:Dict[str, Dict]) -> None:
        """クラスのインスタンスを初期化するメソッドです。コンストラクタ

        引数として受け取ったデータから新たにSubFlowRule型のリストを作成します。

        Args:
            data (Dict[str, Dict]): subFlowの情報が格納されたデータ

        """
        self._id = data[self.__ID]
        self._customize:List[SubFlowRule] = []

        for subflow_type_name, subflow_rule_data in data[self.__CUSTOMIZE].items():
            self._customize.append(SubFlowRule(subflow_type_name, subflow_rule_data))

class SubFlowRule:
    """DGカスタマイズJSON定義書のインスタンス作成に関するメソッドを記載したクラスです。

    このクラスではデータを解析し、インスタンスを作成する処理を行います。

    Attributes:
        class:
            __TASK_IDS:タスクのid群
            __VERIFICATION_IDS:検証用のid群
        instance:
            _subflow_type_name:サブフローの型名

    """
    __TASK_IDS = 'task_ids'
    __VERIFICATION_IDS = 'verification_ids'

    def __init__(self, subflow_type_name:str, data:Dict[str, Any]) -> None:
        """クラスのインスタンスを初期化するメソッドです。コンストラクタ

        引数として受け取ったデータを自身のインスタンスに保存します。

        Args:
            subflow_type_name (str): サブフローの型名
            data (Dict[str, Any]): subFlowの情報が格納されたデータ

        """
        self._subflow_type_name = subflow_type_name
        self._task_ids = data[self.__TASK_IDS]
        self._verification_ids = data[self.__VERIFICATION_IDS]

def get_dg_customize_config():
    """DGカスタマイズJSON定義書のインスタンスを取得するメソッドです。

    ジェイソンファイルを読み出し、AlphaProperty型のリストを作成し、戻り値として返します。

    Returns:
        list[AlphaProperty]:DGカスタマイズJSON定義書のインスタンス

    """
    jf = JsonFile(str(data_governance_customize_file))
    dg_customize_data = jf.read()
    dg_customize:List[AlphaProperty] = []
    for alpha_property_data in dg_customize_data['dg_customize']:
        dg_customize.append(AlphaProperty(alpha_property_data))
    return dg_customize
