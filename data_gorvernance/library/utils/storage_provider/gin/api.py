"""APIリクエストを行う関数が記載されたモジュールです。"""
import os
import time
from urllib import parse

import requests
from requests import Response


def get_server_info(scheme:str, domain:str) -> Response:
    """サーバー情報を取得するための関数です。

    Args:
        scheme (str):スキーマ
        domain (str):ドメイン

    Returns:
        Response:指定したAPIエンドポイントからのHTTPレスポンス

    Raises:
        Exception:APIリクエストの送信に失敗した

    """
    sub_url = "api/v1/gin"
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    try:
        response = requests.get(url=api_url)
        return response
    except Exception as e:
        raise Exception(f'Fail Request to GIN fork url:{api_url}') from e


def get_token_for_auth(scheme:str, domain:str, user_name:str, password:str) -> Response:
    """指定したユーザー名とパスワードから認証トークンを取得するメソッドです。

    Args:
        scheme (str):スキーマ
        domain (str):ドメイン
        user_name (str):ユーザー名
        password (str):パスワード

    Returns:
        Response:認証トークンを含むHTTPレスポンス

    """
    sub_url = os.path.join('api/v1/users', user_name, 'tokens')
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    auth = (user_name, password)
    return requests.get(url=api_url, auth=auth)


def create_token_for_auth(scheme:str, domain:str, user_name:str, password:str) -> Response:
    """指定したユーザー名とパスワードから認証トークンを作成するメソッドです。

    Args:
        scheme (str):スキーマ
        domain (str):ドメイン
        user_name (str):ユーザー名
        password (str):パスワード

    Returns:
        Response:作成した認証トークンを含むAPIリクエストのレスポンス

    """
    sub_url = os.path.join('api/v1/users', user_name, 'tokens')
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    auth = (user_name, password)
    data={"name": "system-generated"}
    return requests.post(url=api_url, auth=auth, data=data)


def get_user_info(scheme:str, domain:str, token:str) -> Response:
    """指定したユーザーの情報を取得するためのメソッドです。

    Args:
        scheme (str):スキーマ
        domain (str):ドメイン
        token (str):トークン

    Returns:
        Response:指定したトークンを持つユーザの情報

    """
    sub_url = "api/v1/user"
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    params = {'token' : token}
    return requests.get(url=api_url, params=params)


def delete_access_token(scheme:str, domain:str, token:str) -> Response:
    """指定したアクセストークンを削除するメソッドです。

    Args:
        scheme (str):スキーマ
        domain (str):ドメイン
        token (str):アクセストークン

    Returns:
        Response:APIリクエストのレスポンス

    """
    sub_url = "api/v1/user/token/delete"
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    params = {'token' : token}
    return requests.delete(url=api_url, params=params)


def upload_key(scheme:str, domain:str, token:str, pubkey:str) -> Response:
    """指定した公開鍵をアップロードするメソッドです。

    Args:
        scheme (str):スキーマ
        domain (str):ドメイン
        token (str):アクセストークン
        pubkey (str):SSHの公開鍵

    Returns:
        Response:APIリクエストのレスポンス

    """
    sub_url = "api/v1/user/keys"
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    params = {'token' : token}
    data={
        "title": "system-generated-"+str(time.time()),
        "key": pubkey
    }
    return requests.post(url=api_url, params=params, data=data)


def search_repo(scheme:str, domain:str, repo_id:str, user_id:str, token:str) -> Response:
    """指定したリポジトリの検索を行うメソッドです。

    Args:
        scheme (str):スキーマ
        domain (str):ドメイン
        repo_id (str):リポジトリID
        user_id (str):ユーザーID
        token (str):トークン

    Returns:
        Response:APIリクエストのレスポンス

    """
    sub_url = "/api/v1/repos/search/user"
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    params = {
        'id' : repo_id,
        'uid' : user_id,
        'token' : token
    }
    return requests.get(url=api_url, params=params)


def patch_container(scheme:str, domain:str, token:str, server_name:str, user_id:str) -> Response:
    """指定したコンテナの更新を行うメソッドです。

    Args:
        scheme (str):スキーマ
        domain (str):ドメイン
        token (str):トークン
        server_name (str):サーバー名
        user_id (str):ユーザーID

    Returns:
        Response:APIリクエストのレスポンス

    """
    sub_url = "/api/v1/container"
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    params = {
        'token' : token,
        'server_name' : server_name,
        'user_id' : user_id
    }
    return requests.patch(url=api_url, params=params)


def search_public_repo(scheme:str, domain:str, repo_id:str,) -> Response:
    """指定した公開リポジトリの検索を行うメソッドです。

    Args:
        scheme (str):スキーマ
        domain (str):ドメイン
        repo_id (str):リポジトリID

    Returns:
        Response:APIリクエストのレスポンス

    """
    sub_url = "/api/v1/repos/search"
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    params = {
        'id' : repo_id,
    }
    return requests.get(url=api_url, params=params)
