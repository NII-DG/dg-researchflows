"""リサーチフローで利用するパスを一括管理するモジュールです。"""
import os
from typing import List


# Folder
DATA_GOVERNANCE = 'data_gorvernance'
DATA = 'data'
OCS_TEMPLATES = 'ocs-templates'
## data_gorvernance直下
BASE = 'base'
LOG = 'log'
IMAGES = 'images'
RESEARCHFLOW = 'researchflow'
WORKING = 'working' ## 同期非対称フォルダ
## base直下
SUB_FLOW = 'subflow'
TASK = 'task'
## researchflow直下
PLAN = 'plan'


# Folder Path
def get_abs_root_form_working_dg_file_path(working_dg_file_path:str)->str:
    """ 与えられたパスから絶対パスを取得する関数です。

    Args:
        working_dg_file_path (str): 作業中のデータガバナンスファイルのパス

    Returns:
        str: working_dg_file_pathからDATA_GOVERNANCEまでのパスを返す。
    """
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
# 画像フォルダ
DG_IMAGES_FOLDER = os.path.join(DATA_GOVERNANCE, IMAGES)
# 非同期フォルダパス
DG_WORKING_FOLDER = os.path.join(DATA_GOVERNANCE, WORKING)
DG_WORKING_RESEARCHFLOW_FOLDER = os.path.join(DG_WORKING_FOLDER, RESEARCHFLOW)

def get_task_data_dir(abs_root, phase:str, data_dir_name:str):
    """ タスクデータディレクトリのパスを取得する関数です。

    <root>/data/<phase>/<data_dir_name>の形式で取得します。

    Args:
        abs_root (): 絶対パスを設定します。
        phase (str): サブフロー種別（フェーズ）を設定します。
        data_dir_name (str): データディレクトリ名を設定します。

    Returns:
        _type_: タスクデータディレクトリのパスを返す。
    """
    return os.path.join(abs_root, DATA, phase, data_dir_name)


# File
MAIN_NOTEBOOK = 'main.ipynb'
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
MAIN_MENU_PATH = os.path.join(DG_RESEARCHFLOW_FOLDER, MAIN_NOTEBOOK)
SETUP_COMPLETED_TEXT_PATH = os.path.join(DG_WORKING_FOLDER, 'setup_completed.txt')
## config file
TOKEN_JSON_PAHT = os.path.join(DG_WORKING_FOLDER, TOKEN)
USER_INFO_PATH = os.path.join(DG_WORKING_FOLDER, USER_INFO)
## data_gorvernance/researchflow/plan/status.json
PLAN_TASK_STATUS_FILE_PATH = os.path.join(DG_RESEARCHFLOW_FOLDER, PLAN, STATUS_JSON)
PLAN_FILE_PATH = os.path.join(DG_RESEARCHFLOW_FOLDER, PLAN, PLAN_JSON)

def get_research_flow_status_file_path(abs_root)->str:
    """ リサーチフローのステータスファイルのパスを取得する関数です。

    Args:
        abs_root (Any): 絶対パスを設定します。

    Returns:
        str: リサーチフローのステータスファイルのパスを返す。
    """
    return os.path.join(abs_root, DG_RESEARCHFLOW_FOLDER, 'research_flow_status.json')

def get_base_subflow_pahse_status_file_path(pahse:str)->str:
    """ baseディレクトリの指定されたサブフロー種別（フェーズ）のステータスファイルへのパスを取得する関数です。

    Args:
        pahse (str): サブフロー種別（フェーズ）を設定します。

    Returns:
        str: サブフロー種別（フェーズ）のステータスファイルへのパスを返す。
    """
    # data_gorvernance\base\subflow\<フェーズ>\status.jsonを更新する。
    return os.path.join(DG_SUB_FLOW_BASE_DATA_FOLDER, pahse, STATUS_JSON)

def get_sub_flow_menu_path(phase:str, subflow_id:str='')->str:
    """各サブフロー種別（フェーズ）のサブフローメニューNotebookへのパスを取得する関数です。

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
    """ researchflowディレクトリの指定されたサブフロー種別（フェーズ）のステータスファイルへのパスを取得する関数です。

    Args:
        phase (str): サブフロー種別（フェーズ）を設定します。
        subflow_id (str, optional): サブフローIDを設定します。 Defaults to ''.

    Returns:
        str: サブフローのステータスファイルへのパスを返す。
    """

    if len(subflow_id)>0:
        return os.path.join(DG_RESEARCHFLOW_FOLDER, phase, subflow_id, STATUS_JSON)
    else:
        return os.path.join(DG_RESEARCHFLOW_FOLDER, phase, STATUS_JSON)

def get_ocs_template_dir( subflow_id:str='' ):
    """ ocs-templatesディレクトリのパスを取得する関数です。

    Args:
        subflow_id (str, optional): サブフローIDを設定します。 Defaults to ''.

    Returns:
        _type_: ocs-templatesディレクトリのパスを返す。
    """

    # working/researchflow/plan/task/plan/ocs-templates
    if len(subflow_id) > 0:
        return os.path.join( '../../../../../../../', DG_WORKING_RESEARCHFLOW_FOLDER, PLAN, TASK, PLAN, OCS_TEMPLATES)
    else:
        return os.path.join( '../../../../../../', DG_WORKING_RESEARCHFLOW_FOLDER, PLAN, TASK, PLAN, OCS_TEMPLATES)

# other method
def get_prepare_file_name_list_for_subflow()->List[str]:
    """ 新規サブフローデータ作成時にコピーするファイルのリストを取得する関数です。

    Returns:
        List[str]: 新規サブフローデータ作成時にコピーするファイルのリスト
    """
    return [MENU_NOTEBOOK, STATUS_JSON, PROPERTY_JSON]
