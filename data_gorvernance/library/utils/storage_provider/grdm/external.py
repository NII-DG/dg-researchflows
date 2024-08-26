""" Gakunin RDMのAPIへの通信、ファイルまたはフォルダをアップロード、メタデータの整形、取得、返却を行うモジュールです。

ファイルの内容を取得し、ファイルまたはフォルダをアップロードします。
ファイルまたはフォルダをアップロードするメソッドやファイルの内容を取得するメソッドがあります。
"""
from http import HTTPStatus
from urllib import parse

import requests
from requests.exceptions import RequestException

from ...error import UnauthorizedError, ProjectNotExist
import os
from osfclient.cli import OSF, split_storage
from osfclient.utils import norm_remote_path, split_storage, is_path_matched
from osfclient.exceptions import UnauthorizedException
from typing import Union
import json

class External:
    """ GRDMのAPI通信への通信、動作確認、データの取得などを行うクラスです。"""

    def __init__(self, base_url:str) -> None:
        """ External コンストラクタのメソッドです。

        Args:
            base_url (str):WebサーバーのURL
        """
        self.base_url = base_url

    def build_api_url(base_url: str, endpoint=''):
        """ API用のURLを作成する

        Args:
            base_url (str): Root URL (e.g. https://rdm.nii.ac.jp)
            endpoint (str, optional): endpoint for api. Defaults to ''.

        Returns:
            str: base path

        Examples:
            >>> build_api_base_url('https://rdm.nii.ac.jp')
            'https://api.rdm.nii.ac.jp/v2/'
            >>> build_api_base_url('https://rdm.nii.ac.jp', '/users/me/')
            'https://api.rdm.nii.ac.jp/v2/users/me/'
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


    def build_oauth_url(base_url: str, endpoint=''):
        """ OAuthのAPI用のURLを作成する

        Args:
            base_url (str): Root URL (e.g. https://rdm.nii.ac.jp)
            endpoint (str, optional): endpoint for api. Defaults to ''.

        Returns:
            str: base path
        """
        parsed = parse.urlparse(base_url)
        netloc = f'accounts.{parsed.netloc}'
        endpoint = endpoint.rstrip('/')
        return parse.urlunparse((parsed.scheme, netloc, endpoint, '', '', ''))

    def get_token_profile(self, token: str):
        """ https://accounts.rdm.nii.ac.jp/oauth2/profile

        Args:
            base_url (str): Root URL (e.g. https://rdm.nii.ac.jp)
            token (str): パーソナルアクセストークン

        Raises:
            UnauthorizedError: 認証が通らない
            requests.exceptions.RequestException: その他の通信エラー
        """
        endpoint = '/oauth2/profile'
        api_url = External.build_oauth_url(self.base_url, endpoint)
        headers = {
            'Authorization': 'Bearer {}'.format(token)
        }
        response = requests.get(url=api_url, headers=headers)
        try:
            response.raise_for_status()
        except RequestException as e:
            if response.status_code == HTTPStatus.UNAUTHORIZED:
                raise UnauthorizedError(str(e)) from e
            raise
        return response.json()

    def get_user_info(self, token: str):
        """ tokenで指定したユーザーの情報を取得する

        https://api.rdm.nii.ac.jp/v2/users/me/

        Args:
            base_url (str): Root URL (e.g. https://rdm.nii.ac.jp)
            token (str): パーソナルアクセストークン

        Raises:
            UnauthorizedError: 認証が通らない
            requests.exceptions.RequestException: その他の通信エラー

        Returns:
            ユーザー情報
        """
        endpoint = '/users/me/'
        api_url = External.build_api_url(self.base_url, endpoint)
        headers = {
            'Authorization': 'Bearer {}'.format(token)
        }
        response = requests.get(url=api_url, headers=headers)
        try:
            response.raise_for_status()
        except RequestException as e:
            if response.status_code == HTTPStatus.UNAUTHORIZED:
                raise UnauthorizedError(str(e)) from e
            raise
        return response.json()

    def get_projects(self, base_url, token):
        """ https://api.rdm.nii.ac.jp/v2/nodes/

        Raises:
            UnauthorizedError: 認証が通らない
            requests.exceptions.RequestException: その他の通信エラー
        """
        sub_url = 'v2/nodes/'
        api_url = base_url + sub_url
        headers = {
            'Authorization': 'Bearer {}'.format(token)
        }
        response = requests.get(url=api_url, headers=headers)
        try:
            response.raise_for_status()
        except RequestException as e:
            if response.status_code == HTTPStatus.UNAUTHORIZED:
                raise UnauthorizedError(str(e)) from e
            raise
        return response.json()

    def get_project_registrations(self, token, project_id):
        """ プロジェクトメタデータを取得する

        https://api.rdm.nii.ac.jp/v2/nodes/{project_id}/registrations

        Raises:
            UnauthorizedError: 認証が通らない
            ProjectNotExist: 指定されたプロジェクトIDが存在しない
            requests.exceptions.RequestException: その他の通信エラー
        """
        endpoint = f'/nodes/{project_id}/registrations/'
        api_url = External.build_api_url(self.base_url, endpoint)
        headers = {
            'Authorization': 'Bearer {}'.format(token)
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

    def get_project_collaborators(self, token: str, project_id: str):
        """ プロジェクトメンバーの情報を取得する

        https://api.rdm.nii.ac.jp/v2/nodes/{project_id}/contributors/

        Args:
            base_url (str): Root URL (e.g. https://rdm.nii.ac.jp)
            token (str): パーソナルアクセストークン
            project_id (str): プロジェクトID

        Raises:
            UnauthorizedError: 認証が通らない
            ProjectNotExist: 指定されたプロジェクトIDが存在しない
            requests.exceptions.RequestException: その他の通信エラー
        """
        endpoint = f'/nodes/{project_id}/contributors/'
        api_url = External.build_api_url(self.base_url, endpoint)
        headers = {
            'Authorization': 'Bearer {}'.format(token)
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

    def upload(self, token:str, base_url:str, project_id:str, source:str, destination:str, recursive:bool=False, force:bool=False):
        """ ファイルまたはフォルダをアップロードするメソッドです。

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


    def download(self, token:str, project_id:str, base_url:str, remote_path:str, base_path=None) -> Union[bytes, None]:
        """ ファイルの内容を取得するメソッドです。

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