"""
リサーチフローで利用するパスを一括管理する
"""
import os
from typing import List

# Folder
### 1階層目
DATA_GOVERNANCE = 'data_gorvernance'
### 2階層目
BASE = 'base'
SUB_FLOW = 'subflow'
TASK = 'task'
RESEARCHFLOW = 'researchflow'
PLAN = 'plan'
WORKING = 'working' ## 同期非対称フォルダ

# Folder Path
def get_abs_root_form_working_dg_file_path(working_dg_file_path:str)->str:
    abs_root = working_dg_file_path[0:working_dg_file_path.rfind(DATA_GOVERNANCE)-1]
    return abs_root

# サブフローベースデータのフォルダパス
DG_SUB_FLOW_BASE_DATA_FOLDER = os.path.join(DATA_GOVERNANCE, BASE, SUB_FLOW)
# タスクベースデータのフォルダパス
DG_TASK_BASE_DATA_FOLDER = os.path.join(DATA_GOVERNANCE, BASE, TASK)
# リサーチフローのフォルダパス
DG_RESEARCHFLOW_FOLDER = os.path.join(DATA_GOVERNANCE, RESEARCHFLOW)
# 非同期フォルダパス
DG_WORKING_FOLDER = os.path.join(DATA_GOVERNANCE, WORKING)


# File
## base
FLOW_DIAG = 'flow.diag'
## researchflow
MENU_NOTEBOOK = 'menu.ipynb'
STATUS_JSON = 'status.json'
PROPERTY_JSON = 'property.json'
PLAN_JSON = 'plan.json'

# File Path
SETUP_COMPLETED_TEXT_PATH = os.path.join(DG_WORKING_FOLDER, 'setup_completed.txt')
PLAN_TASK_STATUS_FILE_PATH = os.path.join(DG_RESEARCHFLOW_FOLDER, PLAN, STATUS_JSON)
PLAN_FILE_PATH = os.path.join(DG_RESEARCHFLOW_FOLDER, PLAN, PLAN_JSON)

def get_research_flow_status_file_path(abs_root)->str:
    return os.path.join(abs_root, DG_RESEARCHFLOW_FOLDER, 'research_flow_status.json')


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
