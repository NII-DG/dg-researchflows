"""
リサーチフローで利用するパスを一括管理する
"""

import os
from typing import List


# root
def get_abs_root_form_working_dg_file_path(working_dg_file_path:str)->str:
    abs_root = working_dg_file_path[0:working_dg_file_path.rfind(DATA_GOVERNANCE)-1]
    return abs_root


# Folder
## 同期対象外フォルダ
DOT_DATA_GOVERNANCE = '.data_gorvernance'
## 同期対象フォルダ
DATA_GOVERNANCE = 'data_gorvernance'
BASE = 'base'
SUB_FLOW = 'subflow'
TASK = 'task'
RESEARCHFLOW = 'researchflow'


# Folder Path
def get_dg_sub_flow_base_data_folder()->str:
    """サブフローベースデータのフォルダパス"""
    return os.path.join(DATA_GOVERNANCE, BASE, SUB_FLOW)
def get_dg_task_base_data_folder()->str:
    """タスクベースデータのフォルダパス"""
    return os.path.join(DATA_GOVERNANCE, BASE, TASK)

def get_dg_researchflow_folder(is_dot:bool=False)->str:
    """リサーチフローのフォルダパス

    Args:
        is_dot (bool, optional): [真の場合、.data_gorvernance、それ以外はdata_gorvernanceが先頭につく]. Defaults to False.

    Returns:
        str: [リサーチフローのフォルダパス]
    """

    if is_dot:
        return os.path.join(DOT_DATA_GOVERNANCE, RESEARCHFLOW)
    else:
        return os.path.join(DATA_GOVERNANCE, RESEARCHFLOW)


# File
MENU_NOTEBOOK = 'menu.ipynb'
STATUS_JSON = 'status.json'
PROPERTY_JSON = 'property.json'


# File Path
SETUP_COMPLETED_TEXT_PATH = os.path.join(DOT_DATA_GOVERNANCE, 'setup_completed.txt')

def get_research_flow_status_file_path(abs_root)->str:
    return os.path.join(abs_root, get_dg_researchflow_folder(), 'research_flow_status.json')


# other method
def get_prepare_file_name_list_for_subflow()->List[str]:
    return [MENU_NOTEBOOK, STATUS_JSON, PROPERTY_JSON]
