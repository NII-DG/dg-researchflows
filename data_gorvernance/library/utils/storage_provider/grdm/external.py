""" Gakunin RDMのAPIへの通信、ファイルまたはフォルダをアップロード、メタデータの整形、取得、返却を行うモジュールです。

ファイルの内容を取得し、ファイルまたはフォルダをアップロードします。
ファイルまたはフォルダをアップロードするメソッドやファイルの内容を取得するメソッドがあります。
"""
from http import HTTPStatus
import os
from typing import Optional
from urllib import parse

from osfclient.cli import OSF, split_storage
from osfclient.utils import norm_remote_path, split_storage, _is_path_matched
from osfclient.exceptions import UnauthorizedException
import requests
from requests.exceptions import RequestException

from library.utils.error import UnauthorizedError, ProjectNotExist


class External:
    """ GRDMのAPI通信への通信、動作確認、データの取得などを行うクラスです。"""

    def build_api_url(self, base_url: str, endpoint: str = '') -> str:
        """ API用のURLを作成する

        Args:
            base_url (str): GRDMのURL (e.g. https://rdm.nii.ac.jp)
            endpoint (str): APIのエンドポイント(デフォルト値は'')

        Returns:
            str: base path

        Examples:
            >>> build_api_base_url('https://rdm.nii.ac.jp')
            'https://rdm.nii.ac.jp/v2/'
            >>> build_api_base_url('https://rdm.nii.ac.jp', '/users/me/')
            'https://rdm.nii.ac.jp/v2/users/me/'
        """
        parsed = parse.urlparse(base_url)
        netloc = f'api.{parsed.netloc}'
        base_path = 'v2/'
        if not endpoint:
            endpoint = base_path
        else:
            endpoint = endpoint.lstrip('/')
            endpoint = base_path + endpoint
        if not endpoint.endswith('/'):
                endpoint = endpoint + '/'
        return parse.urlunparse((parsed.scheme, netloc, endpoint, '', '', ''))

    def build_oauth_url(self, base_url: str,  endpoint: str = '') -> str:
        """ OAuthのAPI用のURLを作成する

        Args:
            base_url (str): GRDMのURL (e.g.  https://rdm.nii.ac.jp)
            endpoint (str): APIのエンドポイント(デフォルト値は'')

        Returns:
            str: base path
        """
        parsed = parse.urlparse(base_url)
        netloc = f'accounts.{parsed.netloc}'
        endpoint = endpoint.rstrip('/')
        return parse.urlunparse((parsed.scheme, netloc, endpoint, '', '', ''))

    def get_token_profile(self, base_url: str, token: str) -> dict:
        """ https://accounts.rdm.nii.ac.jp/oauth2/profile

        Args:
            base_url (str): GRDMのURL (e.g.  https://rdm.nii.ac.jp)
            token (str): パーソナルアクセストークン

        Returns:
            dict: プロファイル

        Raises:
            UnauthorizedError: 認証が通らない
            requests.exceptions.RequestException: その他の通信エラー
        """
        endpoint = '/oauth2/profile'
        api_url = self.build_oauth_url(base_url, endpoint)
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(url=api_url, headers=headers)
        try:
            response.raise_for_status()
        except RequestException as e:
            if response.status_code == HTTPStatus.UNAUTHORIZED:
                raise UnauthorizedError(str(e)) from e
            raise
        return response.json()

    def get_user_info(self, base_url: str, token: str) -> dict:
        """ tokenで指定したユーザーの情報を取得する

        https://rdm.nii.ac.jp/v2/users/me/

        Args:
            base_url (str): GRDMのURL (e.g.  https://rdm.nii.ac.jp)
            token (str): パーソナルアクセストークン

        Raises:
            UnauthorizedError: 認証が通らない
            requests.exceptions.RequestException: その他の通信エラー

        Returns:
            dict: ユーザー情報
        """
        endpoint = '/users/me/'
        api_url = self.build_api_url(base_url, endpoint)
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(url=api_url, headers=headers)
        try:
            response.raise_for_status()
        except RequestException as e:
            if response.status_code == HTTPStatus.UNAUTHORIZED:
                raise UnauthorizedError(str(e)) from e
            raise
        return response.json()

    def get_projects(self, base_url: str, token: str) -> dict:
        """ https://rdm.nii.ac.jp/v2/nodes/

        Args:
            base_url (str): GRDMのURL (e.g. https://rdm.nii.ac.jp)
            token (str): パーソナルアクセストークン

        Returns:
            dict: プロジェクトのデータ

        Raises:
            UnauthorizedError: 認証が通らない
            requests.exceptions.RequestException: その他の通信エラー
        """
        sub_url = 'v2/nodes/'
        api_url = self.build_api_url(base_url, sub_url)
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(url=api_url, headers=headers)
        try:
            response.raise_for_status()
        except RequestException as e:
            if response.status_code == HTTPStatus.UNAUTHORIZED:
                raise UnauthorizedError(str(e)) from e
            raise
        return response.json()

    def get_project_registrations(self, base_url: str, token: str, project_id: str) -> dict:
        """ プロジェクトメタデータを取得する

        https://rdm.nii.ac.jp/v2/nodes/{project_id}/registrations

        Args:
            base_url (str): GRDMのURL (e.g. https://rdm.nii.ac.jp)
            token (str): パーソナルアクセストークン
            project_id (str): プロジェクトID

        Returns:
            dict: プロジェクトメタデータ

        Raises:
            UnauthorizedError: 認証が通らない
            ProjectNotExist: 指定されたプロジェクトIDが存在しない
            requests.exceptions.RequestException: その他の通信エラー
        """
        endpoint = f'/nodes/{project_id}/registrations/'
        api_url = self.build_api_url(base_url, endpoint)
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(url=api_url, headers=headers)
        try:
            response.raise_for_status()
        except RequestException as e:
            if response.status_code == HTTPStatus.UNAUTHORIZED:
                raise UnauthorizedError(str(e)) from e
            if response.status_code == HTTPStatus.NOT_FOUND:
                # 存在しないプロジェクトID
                raise ProjectNotExist(str(e)) from e
            if response.status_code == HTTPStatus.GONE:
                # プロジェクトが消された
                raise ProjectNotExist(str(e)) from e
            raise
        return response.json()

    def get_project_collaborators(self, base_url: str, token: str, project_id: str) -> dict:
        """ プロジェクトメンバーの情報を取得する

        https://rdm.nii.ac.jp/v2/nodes/{project_id}/contributors/

        Args:
            base_url (str): GRDMのURL (e.g.  https://rdm.nii.ac.jp)
            token (str): パーソナルアクセストークン
            project_id (str): プロジェクトID

        Returns:
            dict: プロジェクトメンバーの情報

        Raises:
            UnauthorizedError: 認証が通らない
            ProjectNotExist: 指定されたプロジェクトIDが存在しない
            requests.exceptions.RequestException: その他の通信エラー
        """
        endpoint = f'/nodes/{project_id}/contributors/'
        api_url = self.build_api_url(base_url, endpoint)
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(url=api_url, headers=headers)
        try:
            response.raise_for_status()
        except RequestException as e:
            if response.status_code == HTTPStatus.UNAUTHORIZED:
                raise UnauthorizedError(str(e)) from e
            if response.status_code == HTTPStatus.NOT_FOUND:
                # 存在しないプロジェクトID
                raise ProjectNotExist(str(e)) from e
            if response.status_code == HTTPStatus.GONE:
                # プロジェクトが消された
                raise ProjectNotExist(str(e)) from e
            raise
        return response.json()

    def upload(
        self, token: str, base_url: str, project_id: str, source: str,
        destination: str, recursive: bool = False, force: bool = False
    ) -> None:
        """ ファイルまたはフォルダをアップロードするメソッドです。

        Args:
            token (str): GRDMのパーソナルアクセストークン
            base_url (str): GRDMのURL (e.g.  https://rdm.nii.ac.jp)
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
        api_url_grdm = self.build_api_url(base_url,'')

        osf = OSF(token=token, base_url=api_url_grdm)
        if not osf.has_auth:
            raise KeyError('To upload a file you need to provide a username and password or token.')

        try:
            project = osf.project(project_id)
            storage, remote_path = split_storage(destination)

            store = project.storage(storage)
            if recursive:
                if not os.path.isdir(source):
                    raise RuntimeError(f"Expected source ({source}) to be a directory when using recursive mode.")

                # local name of the directory that is being uploaded
                _, dir_name = os.path.split(source)

                for root, _, files in os.walk(source):
                    subdir_path = os.path.relpath(root, source)
                    for fname in files:
                        local_path = os.path.join(root, fname)
                        with open(local_path, 'rb') as fp:
                            # build the remote path + fname
                            name = os.path.join(remote_path, dir_name, subdir_path, fname)
                            store.create_file(name, fp, force=force, update=update)

            else:
                with open(source, 'rb') as fp:
                    store.create_file(remote_path, fp, force=force, update=update)
        except UnauthorizedException as e:
            raise UnauthorizedError(str(e)) from e

    def download(
        self, token: str, base_url: str, project_id: str,
        remote_path: str, base_path: Optional[str] = None
    ) -> Optional[bytes]:
        """ ファイルの内容を取得するメソッドです。

        Args:
            token (str): GRDMのパーソナルアクセストークン
            base_url (str): GRDMのURL (e.g.  https://rdm.nii.ac.jp)
            project_id (str): プロジェクトID
            remote_path (str): ファイルパス
            base_path (str): ファイルを探すディレクトリのパス

        Returns:
            bytes: 指定したファイルの内容

        Raises:
            UnauthorizedError: 認証が通らない
            requests.exceptions.RequestException: その他の通信エラー
        """

        api_url_grdm = self.build_api_url(base_url,'')
        storage, remote_path = split_storage(remote_path)

        osf = OSF(token=token, base_url=api_url_grdm)
        if base_path is not None:
            if base_path.startswith('/'):
                base_path = base_path[1:]
            base_file_path = base_path[base_path.index('/'):]
            if not base_file_path.endswith('/'):
                base_file_path = base_file_path + '/'

                def path_filter(f): return _is_path_matched(base_file_path, f)
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