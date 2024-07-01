import json
import os
from urllib import parse

from .client import upload, download
from .api import (
    get_token_profile,
    get_user_info,
    get_projects,
    get_project_registrations,
    get_project_collaborators
)
from .metadata import format_metadata
from ...error import NotFoundContentsError, UnauthorizedError


NEED_TOKEN_SCOPE = ["osf.full_write"]
ALLOWED_PERMISSION = ["admin", "write"]


def get_project_id():
    # url: https://rdm.nii.ac.jp/vz48p/osfstorage
    url = os.environ.get("BINDER_REPO_URL", "")
    if not url:
        return None
    split_path = parse.urlparse(url).path.split("/")
    if "osfstorage" in split_path:
        return split_path[1]
    else:
        return None


def check_authorization(base_url: str, token: str) -> bool:
    try:
        profile = get_token_profile(base_url=base_url, token=token)
        scope = profile['scope']
        if all(element in scope for element in NEED_TOKEN_SCOPE):
            return True
    except UnauthorizedError:
        return False
    return False


def check_permission(base_url: str, token: str, project_id: str):
    """_summary_

    Args:
        base_url (str): Root URL (e.g. https://rdm.nii.ac.jp)
        token (str): パーソナルアクセストークン
        project_id (str): プロジェクトID

    Raises:
        UnauthorizedError: 認証が通らない
        ProjectNotExist: 指定されたプロジェクトIDが存在しない
        requests.exceptions.RequestException: その他の通信エラー
    """
    response = get_user_info(base_url, token)
    user_id = response['data']['id']
    response = get_project_collaborators(base_url, token, project_id)
    data = response['data']
    for user in data:
        if user['embeds']['users']['data']['id'] == user_id:
            if user['attributes']['permission'] in ALLOWED_PERMISSION:
                return True
    return False


def get_projects_list(scheme, domain, token):
    """プロジェクトの一覧を取得する

    Raises:
        UnauthorizedError: 認証エラー
        requests.exceptions.RequestException: 通信エラー
    """
    response = get_projects(scheme, domain, token)
    data = response['data']
    return {d['id']: d['attributes']['title'] for d in data}


def sync(token, api_url, project_id, abs_source, abs_root="/home/jovyan"):
    """upload to Gakunin RDM

    abs_source must be an absolute path.

    Args:
        token (str): GRDMのパーソナルアクセストークン
        api_url (str): API URL (e.g. https://api.osf.io/v2/)
        project_id (str): プロジェクトID
        abs_source (str or list): 同期したいファイルまたはディレクトリ
        abs_root (str, optional): リモートのプロジェクトに対応させたいディレクトリの絶対パス. Defaults to "/home/jovyan".

    Raises:
        UnauthorizedError: 認証が通らない
        RuntimeError: RDMClientから上がってくるエラー全般
    """

    if os.path.isdir(abs_source):
        recursive = True
    elif os.path.isfile(abs_source):
        recursive = False
    else:
        raise FileNotFoundError(f"The file or directory '{abs_source}' does not exist.")

    if not os.path.isabs(abs_source):
        raise ValueError(f"The path '{abs_source}' is not an absolute path.")
    if recursive and not abs_source.endswith('/'):
        abs_source += '/'

    destination = os.path.relpath(abs_source, abs_root)

    upload(
        token=token, base_url=api_url, project_id=project_id,
        source=abs_source, destination=destination,
        recursive=recursive, force=True
    )


def download_text_file(token, api_url, project_id, remote_path, encoding='utf-8'):
    """テキストファイルの中身を取得する

    Args:
        token (str): GRDMのパーソナルアクセストークン
        api_url (str): API URL (e.g. https://api.osf.io/v2/)
        project_id (str): プロジェクトID
        remote_path (str): ファイルパス
        encoding (optional): The encoding with which to decode the bytes.

    Raises:
        FileNotFoundError: 指定したファイルが存在しない
        UnauthorizedError: 認証が通らない
        requests.exceptions.RequestException: その他の通信エラー
    """
    content = download(
        token=token, project_id=project_id,
        base_url=api_url, remote_path=remote_path
    )
    if content is None:
        raise FileNotFoundError(f'The specified file (path: {remote_path}) does not exist.')
    return content.decode(encoding)


def download_json_file(token, api_url, project_id, remote_path):
    """jsonファイルの中身を取得する

    Args:
        token (str): GRDMのパーソナルアクセストークン
        api_url (str): API URL (e.g. https://api.osf.io/v2/)
        project_id (str): プロジェクトID
        remote_path (str): ファイルパス

    Raises:
        FileNotFoundError: 指定したファイルが存在しない
        json.JSONDecodeError: 変換元文字列がjson形式でなかった
        UnauthorizedError: 認証が通らない
        requests.exceptions.RequestException: その他の通信エラー
    """
    content = download_text_file(token, api_url, project_id, remote_path)
    return json.loads(content)


def get_project_metadata(base_url: str, token: str, project_id: str):
    """プロジェクトメタデータを取得する

    Args:
        base_url (str):Root URL (e.g. https://rdm.nii.ac.jp)
        token (str): パーソナルアクセストークン
        project_id (str): プロジェクトID

    Raises:
        NotFoundContentsError: メタデータが存在しない
        UnauthorizedError: 認証が通らない
        ProjectNotExist: 指定されたプロジェクトIDが存在しない
        requests.exceptions.RequestException: その他の通信エラー
    """
    metadata = get_project_registrations(base_url, token, project_id)
    if len(metadata['data']) < 1:
        raise NotFoundContentsError(f"Metadata doesn't exist for the project with the specified ID {project_id}.")
    return format_metadata(metadata)


def get_collaborator_list(base_url: str, token: str, project_id: str) -> dict:
    """共同管理者の取得

    Args:
        base_url (str):Root URL (e.g. https://rdm.nii.ac.jp)
        token (str): パーソナルアクセストークン
        project_id (str): プロジェクトID

    Returns:
        dict: ユーザー名がkey、権限種別がvalue

    Raises:
        UnauthorizedError: 認証が通らない
        ProjectNotExist: 指定されたプロジェクトIDが存在しない
        requests.exceptions.RequestException: その他の通信エラー
    """
    response = get_project_collaborators(base_url, token, project_id)
    data = response['data']
    return {
        d['embeds']['users']['data']['attributes']['full_name']: d['attributes']['permission']
        for d in data
    }


def build_collaborator_url(base_url: str, project_id: str):
    """プロジェクトのメンバー一覧のURLを返す

    Args:
        base_url (str):Root URL (e.g. https://rdm.nii.ac.jp)
        project_id (str): プロジェクトID

    Returns:
        str: 指定されたproject idのプロジェクトメンバー一覧画面のURL
    """
    parsed = parse.urlparse(base_url)
    endpoint = f'{project_id}/contributors/'
    return parse.urlunparse((parsed.scheme, parsed.netloc, endpoint, '', '', ''))