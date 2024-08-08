"""データの取得、アップロード、権限やアクセス許可のチェックをするモジュールです。

このモジュールはデータの取得やアップロード、権限やアクセス許可のチェックを行います。
プロジェクトID、プロジェクトの一覧、テキストファイルの中身やjsonファイルの中身、メタデータを取得したり、
GRDMにアップロードしたり、"URLの権限やアクセス許可のチェックを行います。
ファイルまたはフォルダをアップロードするメソッドやファイルの内容を取得するメソッドがあります。
プロジェクトメタデータを整形したり、メタデータのテンプレートを取得したり、メタデータをフォーマットして返却するメソッドがあります。
"""
import json
import os
from urllib import parse
from http import HTTPStatus

from .client import upload, download
from .api import Api
from .metadata import format_metadata
from ...error import NotFoundContentsError, UnauthorizedError
from osfclient.cli import OSF, split_storage
from osfclient.utils import norm_remote_path, split_storage, is_path_matched
from osfclient.exceptions import UnauthorizedException
from requests.exceptions import RequestException
import requests


NEED_TOKEN_SCOPE = ["osf.full_write"]
ALLOWED_PERMISSION = ["admin", "write"]


class GrdmMain():

    def get_project_id() -> (str | None):
        """プロジェクトIDを取得するメソッドです。

        Returns:
            str:プロジェクトIDを返す。値が取得できなかった場合はNone。
        """
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
        """パーソナルアクセストークンの権限をチェックするメソッドです。

        Args:
            base_url (str): Root URL (e.g. https://rdm.nii.ac.jp)
            token (str): パーソナルアクセストークン

        Returns:
            bool: 権限に問題が無ければTrue、問題があればFalseを返す。
        """
        try:
            profile = Api.get_token_profile(base_url=base_url, token=token)
            scope = profile['scope']
            if all(element in scope for element in NEED_TOKEN_SCOPE):
                return True
        except UnauthorizedError:
            return False
        return False


    def check_permission(base_url: str, token: str, project_id: str) -> bool:
        """リポジトリへのアクセス権限のチェックを行うメソッドです。

        Args:
            base_url (str): Root URL (e.g. https://rdm.nii.ac.jp)
            token (str): パーソナルアクセストークン
            project_id (str): プロジェクトID

        Raises:
            UnauthorizedError: 認証が通らない
            ProjectNotExist: 指定されたプロジェクトIDが存在しない
            requests.exceptions.RequestException: その他の通信エラー

        Returns:
            bool:パーミッションに問題なければTrue、問題があればFalseの値を返す。
        """
        response = Api.get_user_info(base_url, token)
        user_id = response['data']['id']
        response = Api.get_project_collaborators(base_url, token, project_id)
        data = response['data']
        for user in data:
            if user['embeds']['users']['data']['id'] == user_id:
                if user['attributes']['permission'] in ALLOWED_PERMISSION:
                    return True
        return False


    #def get_projects_list(scheme: str, domain: str, token: str) -> dict:
    def get_projects_list(scheme_domain: str, token: str) -> dict:
        """プロジェクトの一覧を取得するメソッドです。

        Args:
            scheme(str): プロトコル名(http, https, ssh)
            domain(str):ドメイン名
            token(str):パーソナルアクセストークン

        Raises:
            UnauthorizedError: 認証が通らない
            requests.exceptions.RequestException: 通信エラー

        Returns:
            dict:プロジェクトの一覧のデータの値を返す。
        """
        response = Api.get_projects(scheme_domain, token)
        data = response['data']
        return {d['id']: d['attributes']['title'] for d in data}


    def sync(token: str, api_url: str, project_id: str, abs_source: str, abs_root:str="/home/jovyan"):
        """GRDMにアップロードするメソッドです。

        abs_source は絶対パスでなければならない。

        Args:
            token (str): GRDMのパーソナルアクセストークン
            api_url (str): API URL (e.g. https://api.osf.io/v2/)
            project_id (str): プロジェクトID
            abs_source (str): 同期したいファイルまたはディレクトリ
            abs_root (str): リサーチフローのルートディレクトリ. Defaults to "/home/jovyan".

        Raises:
            UnauthorizedError: 認証が通らない
            RuntimeError: RDMClientから上がってくるエラー全般
            FileNotFoundError: 指定したファイルが存在しないエラー
            ValueError:絶対パスではないエラー
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


    def download_text_file(token: str, api_url: str, project_id: str, remote_path: str, encoding='utf-8'):
        """テキストファイルの中身を取得するメソッドです。

        Args:
            token (str): GRDMのパーソナルアクセストークン
            api_url (str): API URL (e.g. https://api.osf.io/v2/)
            project_id (str): プロジェクトID
            remote_path (str): ファイルパス
            encoding (str): バイトを解析するエンコーディング

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


    def download_json_file(token: str, api_url: str, project_id: str, remote_path: str):
        """jsonファイルの中身を取得するメソッドです。

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
        content = GrdmMain.download_text_file(token, api_url, project_id, remote_path)
        return json.loads(content)


    def get_project_metadata(base_url: str, token: str, project_id: str):
        """プロジェクトメタデータを取得するメソッドです。

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
        metadata = Api.get_project_registrations(base_url, token, project_id)
        if len(metadata['data']) < 1:
            raise NotFoundContentsError(f"Metadata doesn't exist for the project with the specified ID {project_id}.")
        return format_metadata(metadata)


    def get_collaborator_list(base_url: str, token: str, project_id: str) -> dict:
        """共同管理者の取得するメソッドです。

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
        response = Api.get_project_collaborators(base_url, token, project_id)
        data = response['data']
        return {
            d['embeds']['users']['data']['attributes']['full_name']: d['attributes']['permission']
            for d in data
        }


    def build_collaborator_url(base_url: str, project_id: str) -> str:
        """プロジェクトのメンバー一覧のURLを返すメソッドです。

        Args:
            base_url (str):Root URL (e.g. https://rdm.nii.ac.jp)
            project_id (str): プロジェクトID

        Returns:
            str: 指定されたproject idのプロジェクトメンバー一覧画面のURL
        """
        parsed = parse.urlparse(base_url)
        endpoint = f'{project_id}/contributors/'
        return parse.urlunparse((parsed.scheme, parsed.netloc, endpoint, '', '', ''))

    def upload(token:str, base_url:str, project_id:str, source:str, destination:str, recursive:bool=False, force:bool=False):
        """ファイルまたはフォルダをアップロードするメソッドです。

        Args:
            token (str): GRDMのパーソナルアクセストークン
            base_url (str): API URL (e.g. https://api.osf.io/v2/)
            project_id (str): プロジェクトID
            source (str): 保存元パス
            destination (str): 保存先パス
            recursive (bool): 指定したsourceがフォルダかどうか. Defaults to False.
            force (bool): ファイルが存在した場合に上書きするかどうか. Defaults to False.

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



    def download(token:str, project_id:str, base_url:str, remote_path:str, base_path=None) -> (bytes | None):
        """ファイルの内容を取得するメソッドです。

        Args:
            token (str): GRDMのパーソナルアクセストークン
            project_id (str): プロジェクトID
            base_url (str): API URL (e.g. https://api.osf.io/v2/)
            remote_path (str): ファイルパス
            base_path (str): ファイルを探すディレクトリのパス

        Returns:
            bytes: 指定したファイルの内容

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

    def format_metadata(metadata:dict) -> dict[str, list]:
        """Gakunin RDMから取得したプロジェクトメタデータを整形するメソッドです。
            Args:
                metadata(dict):メタデータの値
            Returns:
                list:Dmpの値を返す。
        """

        datas = metadata['data']
        # {'dmp': first_value}
        first_value = []
        for data in datas:
            url = data["relationships"]["registration_schema"]["links"]["related"]["href"]
            schema = GrdmMain.get_schema(url)

            # first_value = [second_layer, ...]
            second_layer = {'title': data['attributes']['title']}
            registration = data['attributes']['registration_responses']
            for key, value in registration.items():
                if key != 'grdm-files':
                    second_layer[key] = GrdmMain.format_display_name(schema, "page1", key, value)

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

            second_layer['grdm-files'] = GrdmMain.format_display_name(schema, "page2", 'grdm-files', file_values)
            first_value.append(second_layer)

        return {'dmp': first_value}


    def get_schema(url:str) -> json:
        """メタデータのプロトコル名を取得するメソッドです。

        リクエストされたURLに接続し、その接続に問題がないかを確認してプロトコル名を取得する。

        Args:
            url(str):メタデータのURL

        Returns:
            Response.json:メタデータのプロトコル名の値を返す。
        """
        response = requests.get(url=url)
        response.raise_for_status()
        return response.json()


    def format_display_name(schema: dict, page_id: str, qid: str, value=None) -> dict:
        """メタデータをフォーマットして返却するメソッドです。

        Args:
            schema (dict): メタデータのプロトコル名
            page_id (str): プロジェクトメタデータ("page1")、ファイルメタデータ("page2")
            qid (str): メタデータのqid
            value (str): メタデータに設定された値. Defaults to None.

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