"""
リサーチフローで利用するパスを一括管理する
"""
import os
from typing import List


# Folder
DATA_GOVERNANCE = 'data_gorvernance'
DATA = 'data'
## data_gorvernance直下
BASE = 'base'
LOG = 'log'
RESEARCHFLOW = 'researchflow'
WORKING = 'working' ## 同期非対称フォルダ
## base直下
SUB_FLOW = 'subflow'
TASK = 'task'
## researchflow直下
PLAN = 'plan'


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
# ログフォルダ
DG_LOG_FOLDER = os.path.join(DATA_GOVERNANCE, LOG, RESEARCHFLOW)
# 非同期フォルダパス
DG_WORKING_FOLDER = os.path.join(DATA_GOVERNANCE, WORKING)
DG_WORKING_RESEARCHFLOW_FOLDER = os.path.join(DG_WORKING_FOLDER, RESEARCHFLOW)

def get_task_data_dir(abs_root, phase:str, data_dir_name:str):
    """<root>/data/<phase>/<data_dir_name>"""
    return os.path.join(abs_root, DATA, phase, data_dir_name)


# File
## subflow
MENU_NOTEBOOK = 'menu.ipynb'
STATUS_JSON = 'status.json'
PROPERTY_JSON = 'property.json'
PLAN_JSON = 'plan.json'
FLOW_DIAG = 'flow.diag'
## config file
TOKEN = 'token.json'
USER_INFO = 'user_info.json'
DOT_GITIGNORE = '.gitignore'


# File Path
## main menu
MAIN_MENU_PATH = os.path.join(DG_RESEARCHFLOW_FOLDER, 'main.ipynb')
SETUP_COMPLETED_TEXT_PATH = os.path.join(DG_WORKING_FOLDER, 'setup_completed.txt')
## config file
TOKEN_JSON_PAHT = os.path.join(DG_WORKING_FOLDER, TOKEN)
USER_INFO_PATH = os.path.join(DG_WORKING_FOLDER, USER_INFO)
## data_gorvernance/researchflow/plan/status.json
PLAN_TASK_STATUS_FILE_PATH = os.path.join(DG_RESEARCHFLOW_FOLDER, PLAN, STATUS_JSON)
PLAN_FILE_PATH = os.path.join(DG_RESEARCHFLOW_FOLDER, PLAN, PLAN_JSON)

def get_research_flow_status_file_path(abs_root)->str:
    return os.path.join(abs_root, DG_RESEARCHFLOW_FOLDER, 'research_flow_status.json')

def get_base_subflow_pahse_status_file_path(pahse:str)->str:
    # data_gorvernance\base\subflow\<フェーズ>\status.jsonを更新する。
    return os.path.join(DG_SUB_FLOW_BASE_DATA_FOLDER, pahse, STATUS_JSON)

def get_sub_flow_menu_path(phase:str, subflow_id:str='')->str:
    """各サブフロー種別（フェーズ）のサブフローメニューNotebookへのパスを取得する

    Args:
        phase (str): サブフロー種別（フェーズ）

        subflow_id (str, optional): サブフローID. Defaults to ''.

    Returns:
        str : サブフローメニューNotebookへのパス

        phase, subflow_idに意味ある値が与えられた場合、researchflow/{:phase}/{:subflow_id}/menu.ipynbを返却する

        phaseのみに意味ある値が与えられた場合、researchflow/{:phase}/menu.ipynbを返却する
    """
    if len(subflow_id) > 0:
        return os.path.join(RESEARCHFLOW, phase, subflow_id, MENU_NOTEBOOK)
    else:
        return os.path.join(RESEARCHFLOW, phase, MENU_NOTEBOOK)

def get_sub_flow_status_file_path(phase:str, subflow_id:str='')->str:

    if len(subflow_id)>0:
        return os.path.join(DG_RESEARCHFLOW_FOLDER, phase, subflow_id, STATUS_JSON)
    else:
        return os.path.join(DG_RESEARCHFLOW_FOLDER, phase, STATUS_JSON)


# other method
def get_prepare_file_name_list_for_subflow()->List[str]:
    return [MENU_NOTEBOOK, STATUS_JSON, PROPERTY_JSON]
