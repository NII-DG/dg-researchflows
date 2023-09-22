import os
from pathlib import Path
from typing import Any, Dict, List

from ..utils.config import path_config
from .file import JsonFile

script_dir_path = os.path.dirname(__file__)
p = Path(script_dir_path)
# DGカスタマイズJSON定義書絶対パス(data_gorvernance\library\data\data_governance_customize.json)
data_governance_customize_file = p.joinpath('..', 'data/data_governance_customize.json').resolve()

class AlphaProperty:
    __ID = 'id'
    __CUSTOMIZE = 'customize'

    def __init__(self, data:Dict[str, Dict]) -> None:
        self._id = data[self.__ID]
        self._customize:List[SubFlowRule] = []

        for subflow_type_name, subflow_rule_data in data[self.__CUSTOMIZE].items():
            self._customize.append(SubFlowRule(subflow_type_name, subflow_rule_data))

class SubFlowRule:
    __TASK_IDS = 'task_ids'
    __VERIFICATION_IDS = 'verification_ids'

    def __init__(self, subflow_type_name:str, data:Dict[str, Any]) -> None:
        self._subflow_type_name = subflow_type_name
        self._task_ids = data[self.__TASK_IDS]
        self._verification_ids = data[self.__VERIFICATION_IDS]

def get_dg_customize_config():
    """DGカスタマイズJSON定義書のインスタンスを取得する

    Returns:
        [list[AlphaProperty]]: [DGカスタマイズJSON定義書のインスタンス]
    """
    jf = JsonFile(str(data_governance_customize_file))
    dg_customize_data = jf.read()
    dg_customize:List[AlphaProperty] = []
    for alpha_property_data in dg_customize_data['dg_customize']:
        dg_customize.append(AlphaProperty(alpha_property_data))
    return dg_customize
