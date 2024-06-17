from urllib import parse
import requests
from http import HTTPStatus


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
    response = requests.post(url=api_url, json=data)
    response.raise_for_status()
    return response.json()