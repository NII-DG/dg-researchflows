import os
from urllib.parse import urlparse

from .models import UpdateArgs, upload
from ...config import path_config, message as msg_config


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


def all_sync_path(abs_root):
    paths = []

    # /home/jovyan/data
    paths.append(os.path.join(abs_root, path_config.DATA))

    # /home/jovyan/data_gorvernance配下のworking以外
    dg_dir = os.path.join(abs_root, path_config.DATA_GOVERNANCE)
    contents = os.listdir(dg_dir)
    contents.remove(path_config.WORKING)
    paths.extend([
        os.path.join(dg_dir, con)
        for con in contents
    ])

    return paths


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