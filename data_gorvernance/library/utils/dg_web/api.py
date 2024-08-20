"""dg-webと接続するモジュールです。

dg-webからガバナンスシートやメタデータのスキーマの取得する関数や検証を行う関数が記載されています。

"""
from http import HTTPStatus
from typing import Optional
from urllib import parse

import requests
from requests.exceptions import RequestException

from library.utils.error import UnauthorizedError, NotFoundContentsError


def get_govsheet_schema(scheme:str, domain:str) -> dict:
    """ ガバナンスシートのスキーマを取得する関数です。

    Args:
        scheme (str): スキームを設定します。
        domain (str): ドメインを設定します。

    Returns:
        dict: ガバナンスシートのスキーマを返す。

    """
    sub_url = '/schemas/govSheet'
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    response = requests.get(url=api_url)
    response.raise_for_status()
    return response.json()


def get_metadata_schema(scheme:str, domain:str) -> dict:
    """ メタデータのスキーマを取得する関数です。

    Args:
        scheme (str): スキームを設定します。
        domain (str): ドメインを設定します。

    Returns:
        dict: メタデータのスキーマを返す。

    """
    sub_url = '/schemas/metadata'
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    response = requests.get(url=api_url)
    response.raise_for_status()
    return response.json()


def check_governedrun_token(scheme:str, domain:str, token:str) -> bool:
    """ Governed Runのトークンの有効性を確認する関数です。

    Args:
        scheme (str): スキームを設定します。
        domain (str): ドメインを設定します。
        token (str): Governed Runのトークンを設定します。

    Returns:
        bool: Governed Runのトークンが有効であればTrue、有効でなければFalseを返す。

    Raises:
        RequestException: 通信エラー

    """
    sub_url = '/checkToken'
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    data = {
        "grdmToken": None,
        "govRunToken": token
    }
    response = requests.post(url=api_url, json=data)
    if response.status_code == HTTPStatus.OK:
        return True
    elif response.status_code == HTTPStatus.UNAUTHORIZED:
        return False
    response.raise_for_status()
    return False


def validate(
    scheme:str, domain:str, grdm_token:str, project_id:str,
    govrun_token:Optional[str]=None, govsheet:Optional[dict]=None,
    metadata:Optional[dict]=None
) -> dict:
    """ 検証する関数です。

    Args:
        scheme(str): スキームを設定します。
        domain(str): ドメインを設定します。
        grdm_token(str): GRDMのトークンを設定します。
        project_id(str): プロジェクトidを設定します。
        govrun_token(str|None): Governed Runのトークンを設定します。
        govsheet(dict|None): ガバナンスシートを設定します。
        metadata(dict|None): メアデータを設定します。

    Returns:
        dict: 検証結果を返す。

    Raises:
        UnauthorizedError: 認証が通らない
        RequestException: その他の通信エラー

    """
    sub_url = '/validations/submit'
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    data = {
        "grdmToken": grdm_token,
        "govRunToken": govrun_token,
        "grdmProjectId": project_id,
        "govSheet": govsheet,
        "metadata": metadata
    }
    response = requests.post(url=api_url, json=data)
    try:
        response.raise_for_status()
    except RequestException as e:
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            raise UnauthorizedError(str(e)) from e
        raise
    return response.json()


def get_validations(scheme:str, domain:str, grdm_token:str, project_id:str) -> dict:
    """ 検証結果を取得する関数です。

    Args:
        scheme (str): スキームを設定します。
        domain (str): ドメインを設定します。
        grdm_token (str): GRDMのトークンを設定します。
        project_id (str): プロジェクトidを設定します。

    Returns:
        dict: 全ての検証結果を返す。

    Raises:
        UnauthorizedError: 認証が通らない
        NotFoundContentsError: 検証結果が存在しない
        RequestException: その他の通信エラー

    """
    sub_url = '/validations'
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    data = {
        "grdmToken": grdm_token,
        "grdmProjectId": project_id,
    }
    response = requests.post(url=api_url, json=data)
    try:
        response.raise_for_status()
    except RequestException as e:
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            raise UnauthorizedError(str(e)) from e
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise NotFoundContentsError(str(e)) from e
        raise
    return response.json()


def get_validations_validationId(
    scheme:str, domain:str, grdm_token:str, project_id:str, validation_id:str
) -> dict:
    """ idを指定して検証結果を取得する関数です。

    Args:
        scheme (str): スキームを設定します。
        domain (str): ドメインを設定します。
        grdm_token (str): GRDMのトークンを設定します。
        project_id (str): プロジェクトidを設定します。
        validation_id (str): 検証のidを設定します。

    Returns:
        dict: 指定したidの検証結果を返す。

    Raises:
        UnauthorizedError: 認証が通らない
        NotFoundContentsError: 検証結果が存在しない
        RequestException: その他の通信エラー

    """
    sub_url = f'/validations/{validation_id}'
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    data = {
        "grdmToken": grdm_token,
        "grdmProjectId": project_id,
    }
    params = {
        "validationId": validation_id
    }
    response = requests.post(url=api_url, json=data, params=params)
    try:
        response.raise_for_status()
    except RequestException as e:
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            raise UnauthorizedError(str(e)) from e
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise NotFoundContentsError(str(e)) from e
        raise
    return response.json()
