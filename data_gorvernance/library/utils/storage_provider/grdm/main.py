import os
from urllib import parse
import json

from .client import upload, download
from .api import get_projects, get_project_registrations, get_project_collaborators
from .metadata import format_metadata
from ...error import MetadataNotExist, RemoteFileNotExist


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


def get_projects_list(scheme, domain, token):
    """プロジェクトの一覧を取得する

    Raises:
        UnauthorizedError: 認証エラー
        requests.exceptions.RequestException: 通信エラー
    """
    response = get_projects(scheme, domain, token)
    data = response['data']
    return {d['id']: d['attributes']['title'] for d in data}


def sync(token, base_url, project_id, abs_source, abs_root="/home/jovyan"):
    """upload to Gakunin RDM

    abs_source must be an absolute path.
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
        token=token, base_url=base_url, project_id=project_id,
        source=abs_source, destination=destination,
        recursive=recursive, force=True
    )


def download_text_file(token, base_url, project_id, remote_path, encoding='utf-8'):
    """テキストファイルの中身を取得する"""
    content = download(
        token=token, project_id=project_id,
        base_url=base_url, remote_path=remote_path
    )
    if content is None:
        raise RemoteFileNotExist(f'The specified file (path: {remote_path}) does not exist.')
    return content.decode(encoding)


def download_json_file(token, base_url, project_id, remote_path):
    """jsonファイルの中身を取得する"""
    content = download_text_file(token, base_url, project_id, remote_path)
    return json.loads(content)


def get_project_metadata(scheme, domain, token, project_id):
    """プロジェクトメタデータを取得する"""
    metadata = get_project_registrations(scheme, domain, token, project_id)
    if len(metadata['data']) < 1:
        raise MetadataNotExist

    return format_metadata(metadata)


def get_collaborator_list(scheme, domain, token, project_id):
    """共同管理者の取得

    Returns:
        dict: ユーザー名がkey、権限種別がvalue
    """
    response = get_project_collaborators(scheme, domain, token, project_id)
    data = response['data']
    return {
        d['embeds']['users']['data']['attributes']['full_name']: d['attributes']['permission']
        for d in data
    }


def get_collaborator_url(scheme, domain, project_id):
    """プロジェクトのメンバー一覧のURLを返す"""
    sub_url = f'{project_id}/contributors/'
    return parse.urlunparse((scheme, domain, sub_url, "", "", ""))