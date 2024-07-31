"""ファイルまたはフォルダをアップロード
    
このモジュールはファイルの内容を取得し、ファイルまたはフォルダをアップロードします。
ファイルまたはフォルダをアップロードするメソッドやファイルの内容を取得するメソッドがあります。
"""
# rdmclientを利用する
from http import HTTPStatus
import os

from osfclient.cli import OSF, split_storage
from osfclient.utils import norm_remote_path, split_storage, is_path_matched
from osfclient.exceptions import UnauthorizedException
from requests.exceptions import RequestException

from ...error import UnauthorizedError


def upload(token, base_url, project_id, source, destination, recursive=False, force=False):
    """ファイルまたはフォルダをアップロードするメソッドです。

    Args:
        token (str): GRDMのパーソナルアクセストークン
        base_url (str): API URL (e.g. https://api.osf.io/v2/)
        project_id (str): プロジェクトID
        source (str): 保存元パス
        destination (str): 保存先パス
        recursive (bool, optional): 指定したsourceがフォルダかどうか. Defaults to False.
        force (bool, optional): ファイルが存在した場合に上書きするかどうか. Defaults to False.

    Raises:
        KeyError:必要な引数が与えられなかった
        RuntimeError:タイムアウト、ネットワークのエラー
        UnauthorizedError: 認証が通らない
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

    try:
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
    except UnauthorizedException as e:
        raise UnauthorizedError(str(e)) from e



def download(token, project_id, base_url, remote_path, base_path=None):
    """ファイルの内容を取得するメソッドです。

    Args:
        token (str): GRDMのパーソナルアクセストークン
        project_id (str): プロジェクトID
        base_url (str): API URL (e.g. https://api.osf.io/v2/)
        remote_path (str): ファイルパス
        base_path (optional): ファイルを探すディレクトリのパス

    Returns:
        str: 指定したファイルの内容

    Raises:
        UnauthorizedError: 認証が通らない
        requests.exceptions.RequestException: その他の通信エラー
    """

    storage, remote_path = split_storage(remote_path)

    osf = OSF(token=token, base_url=base_url)
    if base_path is not None:
        if base_path.startswith('/'):
            base_path = base_path[1:]
        base_file_path = base_path[base_path.index('/'):]
        if not base_file_path.endswith('/'):
            base_file_path = base_file_path + '/'
        path_filter = lambda f: is_path_matched(base_file_path, f)
    else:
        path_filter = None

    try:
        project = osf.project(project_id)
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
    except UnauthorizedException as e:
        raise UnauthorizedError(str(e)) from e
    except RequestException as e:
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            raise UnauthorizedError(str(e)) from e
        raise