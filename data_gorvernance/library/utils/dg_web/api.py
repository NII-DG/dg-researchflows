from urllib import parse
import requests
from requests.exceptions import RequestException
from http import HTTPStatus

from ..error import UnauthorizedError, NotFoundURLError


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


def check_goveredrun_token(scheme, domain, token:str)->bool:
    """/checkToken

    Govered Runのトークンの有効性を確認する
    """
    sub_url = '/checkToken'
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    data = {
        "grdmToken": None,
        "govRunToken": token
    }
    response = requests.post(url=api_url, data=data)
    if response.status_code == HTTPStatus.OK:
        return True
    elif response.status_code == HTTPStatus.UNAUTHORIZED:
        return False
    response.raise_for_status()
    # Noneが返却される可能性を防ぐため。仕様的にはここまで到達しない
    return False


def validate(scheme, domain, grdm_token, project_id, govrun_token=None, govsheet=None, metadata=None):
    """/validations/submit

    検証する
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
    response = requests.post(url=api_url, data=data)
    response.raise_for_status()
    return response.json()


def get_validations(scheme, domain, grdmToken: str, projectId: str):
    """/validations"""
    sub_url = '/validations'
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    data = {
        "grdmToken": grdmToken,
        "grdmProjectId": projectId,
    }
    response = requests.post(url=api_url, json=data)
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        raise UnauthorizedError
    response.raise_for_status()
    return response.json()


def get_validations_validationId(scheme, domain, grdmToken: str, projectId: str, validationId: str):
    """/validations/{validationId}"""
    sub_url = f'/validations/{validationId}'
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    data = {
        "grdmToken": grdmToken,
        "grdmProjectId": projectId,
    }
    params = {
        "validationId": validationId
    }
    response = requests.post(url=api_url, json=data, params=params)
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        raise UnauthorizedError
    response.raise_for_status()
    return response.json()
