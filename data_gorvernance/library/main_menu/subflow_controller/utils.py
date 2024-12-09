import json
import os
import shutil
from datetime import datetime
import zipfile
from typing import Union

import panel as pn

from library.utils.config import path_config, message as msg_config, connect as con_config
from library.utils.nb_file import NbFile
from library.utils.widgets import Button, MessageBox
from library.utils import dg_web
from library.utils.storage_provider import grdm
from library.utils.vault import Vault
from library.utils import file
from library.utils.setting.status import SubflowTask ,SubflowStatusFile
from library.utils.string import StringManager
from library.utils.error import UnusableVault, RepoPermissionError, UnauthorizedError, ProjectNotExist


def input_widget() -> Union[pn.widgets.PasswordInput, pn.widgets.TextInput]:
    """パーソナルアクセストークンとプロジェクトIDの入力欄を生成する関数です。

    Returns:
        PasswordInput, TextInput: 入力欄を返す。
    """
    token_input = pn.widgets.PasswordInput(name=msg_config.get('main_menu', 'access_token_input'), visible=False)
    project_id_input = pn.widgets.TextInput(name=msg_config.get('main_menu', 'project_id_input'), visible=False)
    return token_input, project_id_input

def create_float_panel() -> Union[pn.layout.FloatPanel, Button, Button]:
    """FloatPanelの設定をする関数です。

    Returns:
        pn.layout.FloatPanel, Button, Button: FloatPanelを表示するオブジェクトを返す。
    """
    apply_button = Button(width=50)
    cancel_button = Button(width=50)
    apply_button.set_looks_init(msg_config.get('main_menu', 'apply'))
    cancel_button.set_looks_init(msg_config.get('main_menu', 'cancel'))
    float_panel = pn.layout.FloatPanel(
        pn.Row(msg_config.get('main_menu', 'defalut_govsheet_apply')),
        pn.Row(
            pn.Spacer(width=25),
            apply_button,
            pn.Spacer(width=100),
            cancel_button
        ),
        width=350,
        height=130,
        config={'header': False},
        visible=False
    )
    return float_panel, apply_button, cancel_button

def get_project_id() -> str:
    """プロジェクトIDを取得する関数です。

    Returns:
        str: プロジェクトIDを返す。
    """
    grdm_connect = grdm.Grdm()
    return grdm_connect.get_project_id()

def get_token() -> str:
    """パーソナルアクセストークンを取得する関数です。

    Raises:
        UnusableVault: vaultが利用できない

    Returns:
        str: パーソナルアクセストークンを返す。
    """
    vault_key = 'grdm_token'
    try:
        vault = Vault()
        token = vault.get_value(vault_key)
    except Exception as e:
        raise UnusableVault from e
    vault.set_value(vault_key, token)
    return token

def get_govsheet_rf(abs_root: str) -> dict:
    """RFガバナンスシートを取得する関数です。

    Args:
        abs_root (str): リサーチフローのルートディレクトリ

    Returns:
        dict: RFガバナンスシートの内容(存在しない場合は{})を返す。
    """
    govsheet_rf = {}
    file_path = get_govsheet_rf_path(abs_root)
    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            govsheet_rf = json.load(f)
    else:
        govsheet_rf = {}
    return govsheet_rf

def get_govsheet(token: str, base_url: str, project_id: str, remote_path: str) -> dict:
    """ガバナンスシートを取得する関数です。

    Args:
        token (str): パーソナルアクセストークン
        base_url (str): GRDMのURL
        project_id (str): プロジェクトID
        remote_path (str): ファイルパス

    Returns:
        dict: ガバナンスシートの内容(存在しない場合は{})を返す。
    """
    govsheet = {}
    try:
        grdm_connect = grdm.Grdm()
        govsheet = grdm_connect.download_json_file(
            token, base_url, project_id, remote_path
        )
    except FileNotFoundError:
        govsheet = {}
    return govsheet

def get_notebook_list(path: str) -> list:
    """ディレクトリ配下のノートブックファイルを取得する関数です。

    Args:
        path (str): ディレクトリパス

    Returns:
        list 取得したタスクノートブックリストを返す。
    """
    file_list = []
    for dirpath, dirname, filenames in os.walk(path):
        for filename in filenames:
            if filename.startswith('.ipynb'):
                file_path = os.path.join(dirpath, dirname)
                file_list.append(file_path)
    return file_list

def mapping_file(abs_root: str) -> dict:
    """jsonファイルを読み込みマッピングを行う処理を呼ぶ関数です。

    Args:
        abs_root (str): リサーチフローのルートディレクトリ

    Returns:
        dict: マッピングされたIDとフラグの辞書を返す。
    """
    active_dict = {}
    task_mapping_path = os.path.join(
        abs_root, path_config.DG_RESEARCHFLOW_FOLDER, 'task_mapping.json'
    )
    govsheet_rf_path = get_govsheet_rf_path(abs_root)
    with open(task_mapping_path, 'r') as task:
        task_mapping = json.load(task)
    with open(govsheet_rf_path, 'r') as govsheet:
        govsheet_rf = json.load(govsheet)
    active_dict = task_map(task_mapping, govsheet_rf)
    return active_dict

def task_map(mapping: dict, govsheet: dict) -> dict:
    """マッピングを行う関数です。

    Args:
        mapping (dict): マッピングファイルの内容
        govsheet (dict): ガバナンスシートの内容

    Returns:
        dict: マッピングされたIDとフラグの辞書を返す。
    """
    new_dict = {}
    for key in mapping:
        if isinstance(mapping[key], list):
            for map_dict in mapping[key]:
                if map_dict["value"] == govsheet[key]:
                    for hide_id in map_dict["hide"]:
                        if not hide_id in new_dict:
                            new_dict[hide_id] = False
                    for display_id in map_dict["display"]:
                        new_dict[display_id] = True
        else:
            value_dict = task_map(mapping[key], govsheet[key])
            for map_key, map_value in value_dict.items():
                if map_key in new_dict:
                    if map_value == new_dict[map_key]:
                        new_dict.update(value_dict)
                    else:
                        new_dict[map_key] = True
                else:
                    new_dict.update(value_dict)
    return new_dict

def _copy_file_by_name(target_file: str, search_directory: str, destination_directory: str) -> None:
    """ 指定した名前のファイルを検索ディレクトリから目的のディレクトリにコピーする関数です。

    Args:
        target_file(str) : コピー元のファイルを設定します。
        search_directory(str) : ファイルを検索するディレクトリを設定します。
        destination_directory(str) : コピー先のディレクトリを設定します。

    """
    for root, dirs, files in os.walk(search_directory):
        for filename in files:
            if not filename.startswith(target_file):
                continue
            # if filename.startswith(target_file) のとき
            source_dir = root
            relative_path = file.relative_path(root, search_directory)
            destination_dir = os.path.join(destination_directory, relative_path)
            # タスクノートブックのコピー
            source_file = os.path.join(source_dir, filename)
            destination_file = os.path.join(destination_dir, filename)
            if not os.path.isfile(destination_file):
                file.copy_file(source_file, destination_file)
            # imagesのシンボリックリンク
            source_images = os.path.join(
                path_config.get_abs_root_form_working_dg_file_path(root),
                path_config.DG_IMAGES_FOLDER
            )
            destination_images = os.path.join(destination_dir, path_config.IMAGES)
            if not os.path.isdir(destination_images):
                os.symlink(source_images, destination_images, target_is_directory=True)

def update_status_file(abs_root: str, status_json_path: str, working_path: str):
    """status.jsonを更新する関数です。

    Args:
        abs_root (str): リサーチフローのルートディレクトリ
        status_json_path (str): status.jsonまでのパス
        working_path (str): workingフォルダのパス
    """
    task_dir = os.path.join(abs_root, path_config.DG_TASK_BASE_DATA_FOLDER)
    update_date = mapping_file(abs_root)
    sf = SubflowStatusFile(status_json_path)
    sf_status = sf.read()
    update_flg(update_date, sf_status._tasks)
    sf.write(sf_status)
    after_sf = SubflowStatusFile(status_json_path)
    update_sf_status = after_sf.read()
    dependent_id_list = get_dependent_id_list(update_sf_status._tasks)
    update_dependent_task(dependent_id_list, update_sf_status._tasks)
    after_sf.write(update_sf_status)
    active_name(task_dir, working_path, update_sf_status._tasks)

def update_flg(data: dict, tasks: SubflowTask):
    """タスクの表示フラグを更新する関数です。

    Args:
        data (dict): タスクIDと表示フラグ
        tasks (SubflowTask): サブフローのタスクの設定値
    """
    for task_id, active_flg in data.items():
        for task in tasks:
            if task_id == task.id:
                task.active = active_flg

def get_dependent_id_list(tasks: SubflowTask) -> list:
    """依存タスクが設定されているタスクのタスクIDを取得する関数です。

    Args:
        tasks (SubflowTask): サブフローのタスクの設定値

    Returns:
        list: タスクIDのリストを返す。
    """
    dependent_id_list = []
    for task in tasks:
        if len(task.dependent_task_ids) > 0:
            for dependent_id in task.dependent_task_ids:
                dependent_id_list.append(dependent_id)
    return dependent_id_list

def update_dependent_task(dependent_list: list, tasks: SubflowTask):
    """依存タスクのactiveフラグをTrueにする関数です。

    Args:
        dependent_list (list): タスクIDのリスト
        tasks (SubflowTask): サブフローのタスクの設定値
    """
    for task in tasks:
        for dependent_id in dependent_list:
            if task.id == dependent_id:
                task.active = True

def active_name(search_dir: str, working_path: str, tasks: SubflowTask):
    """表示フラグがTrueのタスクノートブックを用意する関数です。

    Args:
        search_dir (str): ノートブックが格納されているディレクトリパス
        working_path (str): workingフォルダのパス
        tasks (SubflowTask): サブフローのタスクの設定値
    """
    notebook_name_list = []
    for task in tasks:
        if task.active == True:
            _copy_file_by_name(task.name, search_dir, working_path)

def grdm_access_check(base_url: str, token: str, project_id: str) -> bool:
    """アクセス権限のチェックを行う関数です。

    Args:
        base_url (str): リサーチフローのルートディレクトリ
        token (str): パーソナルアクセストークン
        project_id (str): プロジェクトID

    Returns:
        bool: 問題が無ければTrue、問題があればFalseを返す
    """
    grdm_connect = grdm.Grdm()
    if not grdm_connect.check_permission(base_url, token, project_id):
        return False
    else:
        return True

def backup_zipfile(abs_root: str, research_flow_dict: dict, current_time: str):
    """サブフローのファイル群をzip化する関数です。

    Args:
        abs_root (str): リサーチフローのルートディレクトリ
        research_flow_dict (dict): 存在するフェーズをkeyとし対応するサブフローIDとサブフロー名をvalueとした辞書
        current_time (str): 現在時刻
    """
    image_folder = os.path.join(
        abs_root, path_config.DG_IMAGES_FOLDER
    )
    for phase_name, subflow_data in research_flow_dict.items():
        for sub_flow_id, sub_flow_name in subflow_data.items():
            zip_file_path = get_zipfile_path(abs_root, phase_name, sub_flow_id, current_time)
            working_path = get_working_path(abs_root, phase_name, sub_flow_id)
            menu_notebook_path, status_json_path = get_options_path(abs_root, phase_name, sub_flow_id)
            os.makedirs(os.path.dirname(zip_file_path), exist_ok=True)
            notebook_list = get_notebook_list(working_path)
            with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in os.listdir(image_folder):
                    file_path = os.path.join(image_folder, file)
                    if os.path.isfile(file_path):
                        zip_path = os.path.join(path_config.IMAGES, file)
                        zipf.write(file_path, zip_path)
                zipf.write(menu_notebook_path, arcname=os.path.basename(menu_notebook_path))
                zipf.write(status_json_path, arcname=os.path.basename(status_json_path))
                for notebook in notebook_list:
                    zipf.write(notebook, arcname=os.path.basename(notebook))

def get_govsheet_rf_path(abs_root: str) -> str:
    """RFガバナンスシートのパスを取得する関数です。

    Args:
        abs_root (str): リサーチフローのルートディレクトリ

    Returns:
        str: RFガバナンスシートのパスを返す。
    """
    return os.path.join(
        abs_root,
        path_config.DG_RESEARCHFLOW_FOLDER,
        'gov-sheet-rf.json'
    )

def get_zipfile_path(abs_root: str, phase_name: str, sub_flow_id: str, current_time: str) -> str:
    """サブフローファイル群のバックアップ先のパスを取得する関数です。

    Args:
        abs_root (str): リサーチフローのルートディレクトリ
        phase_name (str): フェーズ名
        sub_flow_data (list): サブフローステータスリスト
        current_time (str): 現在時刻

    Returns:
        str: サブフローファイル群のバックアップ先のパスを返す。
    """
    return os.path.join(
        abs_root,
        path_config.DG_SUBFLOW_LOG_FOLDER,
        phase_name,
        sub_flow_id,
        f'{current_time}.zip'
    )

def get_working_path(abs_root: str, phase_name: str, subflow_id: str) -> str:
    """workingファイルのパスを取得する関数です。

    Args:
        abs_root (str): リサーチフローのルートディレクトリ
        phase_name (str): フェーズ名
        subflow_data (list): サブフローステータスリスト

    Returns:
        str: workingファイルのパスを返す。
    """
    return os.path.join(
        abs_root,
        path_config.DG_WORKING_RESEARCHFLOW_FOLDER,
        phase_name,
        subflow_id,
        path_config.TASK
    )

def get_options_path(abs_root: str, phase_name: str, subflow_id: str) -> str:
    """サブフローの設定ファイルのパスを取得する関数です。

    Args:
        abs_root (str): リサーチフローのルートディレクトリ
        phase_name (str): フェーズ名
        subflow_data (list): サブフローステータスリスト

    Returns:
        str: サブフローの設定ファイルのパスを取得する関数です。
    """
    menu_notebook_path = os.path.join(
        abs_root,
        path_config.DATA_GOVERNANCE,
        path_config.get_sub_flow_menu_path(phase_name, subflow_id)
    )
    status_json_path = os.path.join(
        abs_root,
        path_config.get_sub_flow_status_file_path(phase_name, subflow_id)
    )
    return menu_notebook_path, status_json_path

def get_schema() -> dict:
    """スキーマを取得する関数です。

    Returns:
        dict: ガバナンスシートのスキーマを返す。
    """
    schema = {}
    dg_web_url = con_config.get('DG_WEB', 'BASE_URL')
    dgwebapi = dg_web.Api()
    schema = dgwebapi.get_govsheet_schema(dg_web_url)
    return schema

def get_default_govsheet(schema: dict) -> dict:
    """デフォルトのガバナンスシートを作成する関数です。

    Args:
        schema (dict): ガバナンスシートのスキーマ

    Returns:
        dict: デフォルトのガバナンスシートを返す。
    """
    default_govsheet = {}
    for key, value in schema['properties'].items():
        schema_value = get_schema_value(value)
        default_govsheet[key] = schema_value
    return default_govsheet

def get_schema_value(value: dict) -> dict:
    """各valueのdefaultの値を設定する関数です。

    Args:
        value (dict): スキーマのkeyに対する定義部分

    Returns:
        dict: 各keyにdefaultの値を設定した辞書を返す。
    """
    value_dict = {}
    for key, value in value['properties'].items():
        if value.get('type') == 'array':
            if value['default'] is None:
                value_dict[key] = []
            else:
                value_dict[key] = value['default']
        elif value.get('type') == 'boolean':
            value_dict[key] = value['default']
        elif value.get('type') == 'string':
            value_dict[key] = value['default']
    return value_dict

def check_input(input_value: str) -> str:
    """入力の形式をチェックする関数です。

    Args:
        input_value (str): 入力内容

    Returns:
        str: 正しければそのまま入力内容を、間違っていれば空文字を返す。
    """
    input_value = StringManager.strip(input_value)
    if StringManager.is_empty(input_value):
        input_value = ''
    if not StringManager.is_half(input_value):
        input_value = ''
    return input_value

def file_backup_and_copy(abs_root: str, govsheet_rf: dict, govsheet: dict, research_flow_dict: dict, current_time: dict, file_path: str, govsheet_rf_path: str):
    """サブフロー群のバックアップをし、ガバナンスシートをRFガバナンスシートにコピーする関数です。

    Args:
        abs_root (str): リサーチフローのルートディレクトリ
        govsheet_rf (dict): RFガバナンスシート
        govsheet (dict): ガバナンスシート
        research_flow_dict (dict): 存在するフェーズをkeyとし対応するサブフローIDとサブフロー名をvalueとした辞書
        current_time (dict): 現在時刻
        file_path (str): ガバナンスシートのパス
        govsheet_rf_path (str): RFガバナンスシートのパス
    """
    if research_flow_dict:
        if govsheet_rf:
            backup_govsheet_rf_file(abs_root, govsheet_rf_path, current_time)
        backup_zipfile(abs_root, research_flow_dict, current_time)
    file.JsonFile(govsheet_rf_path).write(govsheet)

def remove_and_copy_file_notebook(abs_root: str, research_flow_dict: dict, box: pn.WidgetBox, message: MessageBox):
    """baseフォルダからファイルをコピーしstatus.jsonファイルを更新する関数です。

    Args:
        abs_root (str): リサーチフローのルートディレクトリ
        research_flow_dict (dict): 存在するフェーズをkeyとし対応するサブフローIDとサブフロー名をvalueとした辞書
        box (pn.WidgetBox): ウィジェットボックス
        message (MessageBox): メッセージボックス
    """
    if research_flow_dict:
        for phase_name, sub_flow_data in research_flow_dict.items():
            for sub_flow_id, sub_flow_name in sub_flow_data.items():
                menu_notebook_path, status_json_path = get_options_path(abs_root, phase_name, sub_flow_id)
                working_path = get_working_path(abs_root, phase_name, sub_flow_id)
                remove_file(working_path)
                file.File(str(menu_notebook_path)).remove()
                file.File(str(status_json_path)).remove()
                prepare_new_subflow_data(abs_root, phase_name, sub_flow_id, sub_flow_name, True)
                update_status_file(abs_root, status_json_path, working_path)
    else:
        msg = msg_config.get('main_menu', 'success_govsheet')
        message.update_success(msg)
        box.append(message)

def prepare_new_subflow_data(abs_root: str, phase_name: str, new_sub_flow_id: str, sub_flow_name: str, flg: bool):
    """新しいサブフローのデータを用意するメソッドです。

    Args:
        phase_name (str): フェーズ名
        new_sub_flow_id (str): 新しいサブフローのID
        sub_flow_name (str): サブフロー名
        flg (bool): フォルダ作成時にエラーにさせるかのフラグ。エラーにさせるならfalse、させないならtrue
    """

    # 新規サブフローデータの用意
    # data_gorvernance\researchflowを取得
    dg_researchflow_path = os.path.join(abs_root, path_config.DG_RESEARCHFLOW_FOLDER)
    # data_gorvernance\base\subflowを取得する
    dg_base_subflow_path = os.path.join(abs_root, path_config.DG_SUB_FLOW_BASE_DATA_FOLDER)

    # コピー先フォルダパス
    dect_dir_path = os.path.join(dg_researchflow_path, phase_name, new_sub_flow_id)

    # コピー先フォルダの作成
    os.makedirs(dect_dir_path, exist_ok=flg)  # 新規作成の時、既に存在している場合はエラーになる

    # 対象コピーファイルorディレクトリリスト
    copy_files = path_config.get_prepare_file_name_list_for_subflow()

    try:
        for copy_file_name in copy_files:
            # コピー元ファイルパス
            src_path = os.path.join(dg_base_subflow_path, phase_name, copy_file_name)
            dect_path = os.path.join(dg_researchflow_path, phase_name, new_sub_flow_id, copy_file_name)
            # コピーする。
            if os.path.isfile(src_path):
                shutil.copyfile(src_path, dect_path)
            if os.path.isdir(src_path):
                file.copy_dir(src_path, dect_path, overwrite=True)
            # menu.ipynbファイルの場合は、menu.ipynbのヘッダーにサブフロー名を埋め込む
            if copy_file_name == path_config.MENU_NOTEBOOK:
                nb_file = NbFile(dect_path)
                nb_file.embed_subflow_name_on_header(sub_flow_name)
    except Exception:
        # 失敗した場合は、コピー先フォルダごと削除する（ロールバック）
        shutil.rmtree(dect_dir_path)
        raise

def backup_govsheet_rf_file(abs_root :str, govsheet_rf_path: str, current_time: str):
    """RFガバナンスシートのバックアップを取る関数です。

    Args:
        abs_root (str): リサーチフローのルートディレクトリ
        govsheet_rf_path (str): RFガバナンスシートのパス
        current_time (str): 現在時刻
    """
    backup_file_path = os.path.join(
        abs_root,
        path_config.DATA_GOVERNANCE,
        path_config.LOG,
        'gov-sheet-rf',
        f'{current_time}.json'
    )
    file.copy_file(govsheet_rf_path, backup_file_path)

def remove_file(drc_path: str):
    """フォルダ内のファイルを全て削除するメソッドです。

    Args:
        drc_path (str): 対象のディレクトリのパス
    """
    if not os.path.isdir(drc_path):
        pass
    for root, dirs, files in os.walk(drc_path):
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)

def create_data_dir(abs_root, phase_name: str, data_dir_name: str) -> str:
    """データディレクトリを作成するメソッドです。

    Args:
        phase_name (str): フェーズ名
        data_dir_name (str): データディレクトリ名

    Raises:
        Exception: 既にファイルが存在しているエラー

    Returns:
        str: データディレクトリを作成するパスの値を返す。
    """
    path = path_config.get_task_data_dir(abs_root, phase_name, data_dir_name)
    if os.path.exists(path):
        raise Exception(f'{path} is already exist.')
    os.makedirs(path)
    return path
