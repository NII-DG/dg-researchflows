"""Gakunin RDMのAPIへの通信"""
from http import HTTPStatus
from urllib import parse

import requests
from requests.exceptions import RequestException

from ...error import UnauthorizedError, ProjectNotExist

class Api():

    def build_api_url(base_url: str, endpoint=''):
        """API用のURLを作成する

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
        """OAuthのAPI用のURLを作成する

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


    def get_token_profile(base_url: str, token: str):
        """https://accounts.rdm.nii.ac.jp/oauth2/profile

        Args:
            base_url (str): Root URL (e.g. https://rdm.nii.ac.jp)
            token (str): パーソナルアクセストークン

        Raises:
            UnauthorizedError: 認証が通らない
            requests.exceptions.RequestException: その他の通信エラー
        """
        endpoint = '/oauth2/profile'
        api_url = build_oauth_url(base_url, endpoint)
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


    def get_user_info(base_url: str, token: str):
        """tokenで指定したユーザーの情報を取得する

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
        api_url = build_api_url(base_url, endpoint)
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


    def get_projects(scheme, domain, token):
        """https://api.rdm.nii.ac.jp/v2/nodes/

        Raises:
            UnauthorizedError: 認証が通らない
            requests.exceptions.RequestException: その他の通信エラー
        """
        sub_url = 'v2/nodes/'
        api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
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


    def get_project_registrations(base_url, token, project_id):
        """プロジェクトメタデータを取得する

        https://api.rdm.nii.ac.jp/v2/nodes/{project_id}/registrations

        Raises:
            UnauthorizedError: 認証が通らない
            ProjectNotExist: 指定されたプロジェクトIDが存在しない
            requests.exceptions.RequestException: その他の通信エラー
        """
        endpoint = f'/nodes/{project_id}/registrations/'
        api_url = build_api_url(base_url, endpoint)
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


    def get_project_collaborators(base_url: str, token: str, project_id: str):
        """プロジェクトメンバーの情報を取得する

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
        api_url = build_api_url(base_url, endpoint)
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
