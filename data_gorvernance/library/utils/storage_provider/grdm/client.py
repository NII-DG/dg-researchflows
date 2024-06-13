# rdmclientを利用する
import os

from osfclient.cli import OSF, split_storage
from osfclient.utils import norm_remote_path, split_storage, is_path_matched
from osfclient.models import File
from osfclient.exceptions import UnauthorizedException


def upload(token, base_url, project_id, source, destination, recursive=False, force=False):
    """ファイルまたはフォルダをアップロードする

    Args:
        token (str): GRDMのパーソナルアクセストークン
        base_url (str): API URL (e.g. https://api.osf.io/v2/)
        project_id (str): プロジェクトID
        source (str): 保存元パス
        destination (str): 保存先パス
        recursive (bool, optional): 指定したsourceがフォルダかどうか. Defaults to False.
        force (bool, optional): ファイルが存在した場合に上書きするかどうか. Defaults to False.
    """
    # Falseで固定
    # Trueにすると指定したパスを見つけ出せずにRuntimeErrorが返ってくる
    update = False

    if source is None or destination is None:
        raise KeyError("too few arguments: source or destination")

    osf = OSF(token=token, base_url=base_url)
    if not osf.has_auth:
        raise KeyError('To upload a file you need to provide a username and'
                    ' password or token.')

    project = osf.project(project_id)
    storage, remote_path = split_storage(destination)

    store = project.storage(storage)
    if recursive:
        if not os.path.isdir(source):
            raise RuntimeError("Expected source ({}) to be a directory when "
                                "using recursive mode.".format(source))

        # local name of the directory that is being uploaded
        _, dir_name = os.path.split(source)

        for root, _, files in os.walk(source):
            subdir_path = os.path.relpath(root, source)
            for fname in files:
                local_path = os.path.join(root, fname)
                with open(local_path, 'rb') as fp:
                    # build the remote path + fname
                    name = os.path.join(remote_path, dir_name, subdir_path,
                                        fname)
                    store.create_file(name, fp, force=force,
                                        update=update)

    else:
        with open(source, 'rb') as fp:
            store.create_file(remote_path, fp, force=force,
                                update=update)


def download(token, project_id, base_url, remote_path, base_path=None):
    """ファイルの内容を取得する。ファイルに保存はしない

    Args:
        token (str): GRDMのパーソナルアクセストークン
        project_id (str): プロジェクトID
        base_url (str): API URL (e.g. https://api.osf.io/v2/)
        remote_path (str): ファイルパス
        base_path (optional): ファイルを探すディレクトリのパス

    Returns:
        str: 指定したファイルの内容
    """

    storage, remote_path = split_storage(remote_path)

    osf = OSF(token=token, base_url=base_url)
    project = osf.project(project_id)
    if base_path is not None:
        if base_path.startswith('/'):
            base_path = base_path[1:]
        base_file_path = base_path[base_path.index('/'):]
        if not base_file_path.endswith('/'):
            base_file_path = base_file_path + '/'
        path_filter = lambda f: is_path_matched(base_file_path, f)
    else:
        path_filter = None

    store = project.storage(storage)
    files = store.files if path_filter is None \
            else store.matched_files(path_filter)
    for file_ in files:
        if norm_remote_path(file_.path) == remote_path:
            try:
                response = file_._get(file_._download_url, stream=True)
            except UnauthorizedException:
                response = file_._get(file_._upload_url, stream=True)
            response.raise_for_status()

            file_content = []
            for chunk in response.iter_content(chunk_size=8192):
                file_content.append(chunk)
            return b''.join(file_content)


class ClientFile(File):
    def _update_attributes(self, file):
        super()._update_attributes(file)
        self.link = self._get_attribute(file, 'links', 'html')


def file_list(token, project_id, base_url, target_folder, recursive=False)->list[ClientFile]:
    """指定したディレクトリにあるファイルを取得する

    Args:
        token (str): GRDMのパーソナルアクセストークン
        project_id (str): プロジェクトID
        base_url (str): API URL (e.g. https://api.osf.io/v2/)
        target_folder (str): ファイルを取得したいディレクトリ
        recursive (bool, optional): 再帰的に取得するかどうか. Defaults to False.

    Returns:
        list[ClientFile]: 指定したディレクトリにあるファイルのリスト
    """

    osf = OSF(token=token, base_url=base_url)
    if not osf.has_auth:
        raise KeyError('To upload a file you need to provide a username and'
                ' password or token.')
    project = osf.project(project_id)
    storage, remote_path = split_storage(target_folder)

    base_file_path = remote_path
    if not base_file_path.startswith('/'):
        base_file_path = '/' + base_file_path
    if not base_file_path.endswith('/'):
        base_file_path = base_file_path + '/'
    path_filter = lambda f: is_path_matched(base_file_path, f)

    store = project.storage(storage)
    files = store._iter_children(store._files_url, 'file', ClientFile,
                                 store._files_key, path_filter)
    target_files = []
    for file_ in files:
        if recursive or remote_path == os.path.dirname(norm_remote_path(file_.path)):
            target_files.append(file_)
    return target_files

