import os
from urllib.parse import urlparse

from .models import UpdateArgs, upload


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


def sync(token, base_url, project_id, abs_source, abs_root="/home/jovyan", recursive=True):
    """upload to GRDM

    source must be an absolute path.
    """
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