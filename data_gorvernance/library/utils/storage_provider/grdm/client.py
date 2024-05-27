import os

from osfclient.cli import OSF, split_storage
from osfclient.utils import norm_remote_path, split_storage, is_path_matched
from osfclient.exceptions import UnauthorizedException


class UpdateArgs:

    def __init__(self, project_id, source, destination, recursive=False, force=False) -> None:
        """アップロード時のパラメータ

        Args:
            project_id (_type_): プロジェクトID
            source (_type_): 保存元パス
            destination (_type_): 保存先パス
            recursive (bool, optional): 指定したsourceがフォルダかどうか. Defaults to False.
            force (bool, optional): ファイルが存在した場合に上書きするかどうか. Defaults to False.
        """
        self.project = project_id
        self.source = source
        self.destination = destination
        self.recursive = recursive
        self.force = force
        self.update = False


def upload(token, base_url, args):
    if args.source is None or args.destination is None:
        raise KeyError("too few arguments: source or destination")

    osf = OSF(token=token, base_url=base_url)
    if not osf.has_auth:
        raise KeyError('To upload a file you need to provide a username and'
                    ' password or token.')

    project = osf.project(args.project)
    storage, remote_path = split_storage(args.destination)

    store = project.storage(storage)
    if args.recursive:
        if not os.path.isdir(args.source):
            raise RuntimeError("Expected source ({}) to be a directory when "
                                "using recursive mode.".format(args.source))

        # local name of the directory that is being uploaded
        _, dir_name = os.path.split(args.source)

        for root, _, files in os.walk(args.source):
            subdir_path = os.path.relpath(root, args.source)
            for fname in files:
                local_path = os.path.join(root, fname)
                with open(local_path, 'rb') as fp:
                    # build the remote path + fname
                    name = os.path.join(remote_path, dir_name, subdir_path,
                                        fname)
                    store.create_file(name, fp, force=args.force,
                                        update=args.update)

    else:
        with open(args.source, 'rb') as fp:
            store.create_file(remote_path, fp, force=args.force,
                                update=args.update)

class DownloadArgs:

        def __init__(self, project_id, base_url, remote_path, base_path=None) -> None:
            """ダウンロード時のパラメータ

            Args:
                project_id (_type_): _description_
                base_url (_type_): _description_
                remote_path (_type_): _description_
            """
            self.project = project_id
            self.base_url = base_url
            self.remote = remote_path
            self.base_path = base_path

def download(token, args):
    """ファイルの内容を取得する。ファイルに保存はしない

    Args:
        token (str): OSFのパーソナルアクセストークン
        args (DownloadArgs): パラメータ

    Returns:
        str: 指定したファイルの内容
    """

    storage, remote_path = split_storage(args.remote)

    osf = OSF(token=token, base_url=args.base_url)
    project = osf.project(args.project)
    if args.base_path is not None:
        base_path = args.base_path
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
