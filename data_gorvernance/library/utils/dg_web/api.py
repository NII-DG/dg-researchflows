from http import HTTPStatus
from urllib import parse

import requests
from requests.exceptions import RequestException

from ..error import UnauthorizedError, NotFoundContentsError


def get_govsheet_schema(scheme, domain):
    """/schemas/govSheet"""
    sub_url = '/schemas/govSheet'
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    response = requests.get(url=api_url)
    response.raise_for_status()
    return response.json()


def get_metadata_schema(scheme, domain):
    """/schemas/metadata"""
    sub_url = '/schemas/metadata'
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    response = requests.get(url=api_url)
    response.raise_for_status()
    return response.json()


def check_governedrun_token(scheme, domain, token:str)->bool:
    """/checkToken

    Governed Runのトークンの有効性を確認する

    Raises:
        requests.exceptions.RequestException: 通信エラー
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


def validate(scheme, domain, grdm_token, project_id, govrun_token=None, govsheet=None, metadata=None):
    """/validations/submit

    検証する

    Raises:
        UnauthorizedError: 認証が通らない
        requests.exceptions.RequestException: その他の通信エラー
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


def get_validations(scheme, domain, grdm_token: str, project_id: str):
    """/validations

    Raises:
        UnauthorizedError: 認証が通らない
        NotFoundContentsError: 検証結果が存在しない
        requests.exceptions.RequestException: その他の通信エラー

    Returns:
        全ての検証結果
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


def get_validations_validationId(scheme, domain, grdm_token: str, project_id: str, validation_id: str):
    """/validations/{validation_id}

    Raises:
        UnauthorizedError: 認証が通らない
        NotFoundContentsError: 検証結果が存在しない
        requests.exceptions.RequestException: その他の通信エラー

    Returns:
        指定したidの検証結果
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