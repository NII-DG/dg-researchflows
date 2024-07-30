"""APIリクエストを行う関数が記載されたモジュールです。"""
from urllib import parse
import requests
import time
import os

def get_server_info(scheme, domain):
    """指定したAPIエンドポイントから情報を取得するための関数です。

    Args:
        scheme (Any):スキーマ
        domain (Any):ドメイン

    Returns:
        Response:指定されたAPIエンドポイントからのHTTPレスポンス

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

def get_token_for_auth(scheme, domain, user_name, password):
    """指定したユーザー名とパスワードから認証トークンを取得するメソッドです。

    Args:
        scheme (Any):スキーマ
        domain (Any):ドメイン
        user_name (Any):ユーザー名
        password (Any):パスワード

    Returns:
        Response:認証トークンを含むHTTPレスポンス

    """
    sub_url = os.path.join('api/v1/users', user_name, 'tokens')
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    auth = (user_name, password)
    return requests.get(url=api_url, auth=auth)

def create_token_for_auth(scheme, domain, user_name, password):
    """指定したユーザー名とパスワードから認証トークンを作成するメソッドです。

    Args:
        scheme (Any):スキーマ
        domain (Any):ドメイン
        user_name (Any):ユーザー名
        password (Any):パスワード

    Returns:
        Response:作成した認証トークンを含むAPIリクエストのレスポンス

    """
    sub_url = os.path.join('api/v1/users', user_name, 'tokens')
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    auth = (user_name, password)
    data={"name": "system-generated"}
    return requests.post(url=api_url, auth=auth, data=data)

def get_user_info(scheme, domain, token):
    """指定したユーザーの情報を取得するためのメソッドです。

    Args:
        scheme (Any):スキーマ
        domain (Any):ドメイン
        token (Any):トークン

    Returns:
        Response:指定されたトークンを持つユーザの情報

    """
    sub_url = "api/v1/user"
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    params = {'token' : token}
    return requests.get(url=api_url, params=params)

def delete_access_token(scheme, domain, token):
    """指定したアクセストークンを削除するメソッドです。

    Args:
        scheme (Any):スキーマ
        domain (Any):ドメイン
        token (Any):アクセストークン

    Returns:
        Response:APIリクエストのレスポンス

    """
    sub_url = "api/v1/user/token/delete"
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    params = {'token' : token}
    return requests.delete(url=api_url, params=params)

def upload_key(scheme:str, domain:str, token:str, pubkey:str):
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

def search_repo(scheme, domain, repo_id, user_id, token):
    """指定したリポジトリの検索を行うメソッドです。

    Args:
        scheme (Any):スキーマ
        domain (Any):ドメイン
        repo_id (Any):リポジトリID
        user_id (Any):ユーザーID
        token (Any):トークン

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

def patch_container(scheme, domain, token, server_name, user_id):
    """指定したコンテナの更新を行うメソッドです。

    Args:
        scheme (Any):スキーマ
        domain (Any):ドメイン
        token (Any):トークン
        server_name (Any):サーバー名
        user_id (Any):ユーザーID

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

def search_public_repo(scheme, domain, repo_id,):
    """指定した公開リポジトリの検索を行うメソッドです。

    Args:
        scheme (Any):スキーマ
        domain (Any):ドメイン
        repo_id (Any):リポジトリID

    Returns:
        Response:APIリクエストのレスポンス

    """
    sub_url = "/api/v1/repos/search"
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    params = {
        'id' : repo_id,
    }
    return requests.get(url=api_url, params=params)