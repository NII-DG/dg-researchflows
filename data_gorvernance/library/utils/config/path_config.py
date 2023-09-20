"""
リサーチフローで利用するパスを一括管理する
"""

import os
from typing import List
# Folder
## 同期対象外フォルダ
DOT_DATA_GOVERNANCE = '.data_gorvernance'
## 同期対象フォルダ
DATA_GOVERNANCE = 'data_gorvernance'
BASE = 'base'
SUB_FLOW = 'subflow'
TASK = 'task'
RESEARCHFLOW = 'researchflow'
PLAN = 'plan'


# Folder Path

def get_abs_root_form_working_dg_file_path(working_dg_file_path:str)->str:
    abs_root = working_dg_file_path[0:working_dg_file_path.rfind(DATA_GOVERNANCE)-1]
    return abs_root

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
PLAN_JSON = 'plan.json'

FLOW_DIAG = 'flow.diag'

# File Path
SETUP_COMPLETED_TEXT_PATH = os.path.join(DOT_DATA_GOVERNANCE, 'setup_completed.txt')
PLAN_TASK_STATUS_FILE_PATH = os.path.join(get_dg_researchflow_folder(False), PLAN, STATUS_JSON)
PLAN_FILE_PATH = os.path.join(get_dg_researchflow_folder(False), PLAN, PLAN_JSON)

def get_research_flow_status_file_path(abs_root)->str:
    return os.path.join(abs_root, get_dg_researchflow_folder(), 'research_flow_status.json')

def get_abs_root_form_working_dg_file_path(working_dg_file_path:str)->str:
    if DOT_DATA_GOVERNANCE in working_dg_file_path:
        return working_dg_file_path[0:working_dg_file_path.rfind(DOT_DATA_GOVERNANCE)-1]
    else:
        return working_dg_file_path[0:working_dg_file_path.rfind(DATA_GOVERNANCE)-1]

# other method
def get_prepare_file_name_list_for_subflow()->List[str]:
    return [MENU_NOTEBOOK, STATUS_JSON, PROPERTY_JSON]


def get_subflow_type_and_id(working_file_path: str):
    parts = os.path.normpath(working_file_path).split(os.sep)
    target_directory = RESEARCHFLOW
    subflow_id = None
    subflow_type = None
    if target_directory in parts:

        try:
            index = parts.index(target_directory)
        except Exception:
            raise

        if index < len(parts) - 1:
            subflow_type = parts[index + 1]
        if index + 2 < len(parts) - 1:
            subflow_id = parts[index + 2]

    return subflow_type, subflow_id
