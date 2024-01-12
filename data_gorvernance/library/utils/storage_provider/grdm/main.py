import os
from urllib import parse
import json
import requests

from .client import UpdateArgs, upload
from .api import get_projects, get_project_registrations, get_project_collaborators
from ...error import MetadataNotExist


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
    """upload to GRDM

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

    arg = UpdateArgs(
                project_id=project_id,
                source=abs_source,
                destination=destination,
                recursive=recursive,
                force=True,
            )
    upload(token, base_url, arg)


def get_project_metadata(scheme, domain, token, project_id):
    metadata = get_project_registrations(scheme, domain, token, project_id)
    if len(metadata['data']) < 1:
        raise MetadataNotExist

    return format_metadata(metadata)


def format_metadata(metadata):

    datas = metadata['data']
    # {'dmp': first_value}
    first_value = []
    for data in datas:
        url = data["relationships"]["registration_schema"]["links"]["related"]["href"]
        schema = get_schema(url)

        # first_value = [second_layer, ...]
        second_layer = {'title': data['attributes']['title']}
        registration = data['attributes']['registration_responses']
        for key, value in registration.items():
            if key != 'grdm-files':
                second_layer[key] = format_display_name(schema, "page1", key, value)

        files = json.loads(registration['grdm-files'])
        # grdm-files > value
        file_values = []
        for file in files:
            file_datas = {}
            file_datas['path'] = file['path']
            file_metadata = {}
            for key, item in file['metadata'].items():
                file_metadata[key] = item['value']
            file_datas['metadata'] = file_metadata
            file_values.append(file_datas)

        second_layer['grdm-files'] = format_display_name(schema, "page2", 'grdm-files', file_values)
        first_value.append(second_layer)

    return {'dmp': first_value}


def get_schema(url):
    response = requests.get(url=url)
    response.raise_for_status()
    return response.json()


def format_display_name(schema: dict, page_id: str, qid: str, value=None):
    """メタデータをフォーマットして返却する

    Args:
        schema (dict): メタデータのテンプレート
        page_id (str): プロジェクトメタデータ("page1")、ファイルメタデータ("page2")
        qid (str): メタデータのqid
        value (optional): メタデータに設定された値. Defaults to None.

    Returns:
        dict: フォーマットされたメタデータの値
    """
    pages = schema["data"]["attributes"]["schema"]["pages"]
    items = {}
    for page in pages:
        if page.get("id") != page_id:
            continue

        questions = page["questions"]
        for question in questions:
            if question.get("qid") != qid:
                continue

            items['label_jp'] = question.get("nav")
            if value is None:
                break
            items['value'] = value

            options = question.get("options", [])
            for option in options:
                if option.get("text") != value:
                    continue
                items['field_name_jp'] = option.get("tooltip")
                break
            break
        break

    return items


def get_collaborator_list(scheme, domain, token, project_id):
    response = get_project_collaborators(scheme, domain, token, project_id)
    data = response['data']
    return {
        d['embeds']['users']['data']['attributes']['full_name']: d['attributes']['permission']
        for d in data
    }


def get_collaborator_url(scheme, domain, project_id):
    sub_url = f'{project_id}/contributors/'
    return parse.urlunparse((scheme, domain, sub_url, "", "", ""))
