import os
from urllib.parse import urlparse
import json

from .models import UpdateArgs, upload
from .api import get_project_registrations
from ...error import MetadataNotExist


def get_project_id():
    # url: https://rdm.nii.ac.jp/vz48p/osfstorage
    url = os.environ.get("BINDER_REPO_URL", "")
    if not url:
        return None
    split_path = urlparse(url).path.split("/")
    if "osfstorage" in split_path:
        return split_path[1]
    else:
        return None


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
        # first_value = [first_value_item, ...]
        first_value_item = {'title': data['attributes']['title']}
        registration = data['attributes']['registration_responses']
        for key, value in registration.items():
            if key != 'grdm-files':
                first_value_item[key] = value

        files = json.loads(registration['grdm-files'])
        # {'dmp': {'grdm-files': second_value}}
        second_value = []
        for file in files:
            # second_value = [second_value_item, ...]
            second_value_item = {}
            second_value_item['path'] = file['path']
            # {'dmp': {'grdm-files': {'metadata': third_value}}}
            third_value = {}
            for key, value in file['metadata'].items():
                third_value[key] = value['value']
            second_value_item['metadata'] = third_value
            second_value.append(second_value_item)

        first_value_item['grdm-files'] = second_value
        first_value.append(first_value_item)
    return {'dmp': first_value}
