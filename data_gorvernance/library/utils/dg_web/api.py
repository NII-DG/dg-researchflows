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

def get_validations(scheme, domain, grdm_token: str, project_id: str):
    """/validations"""
    sub_url = '/validations'
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    data = {
        "grdmToken": grdm_token,
        "grdmProjectId": project_id,
    }
    response = requests.post(url=api_url, json=data)
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        raise UnauthorizedError
    response.raise_for_status()
    return response.json()

def get_validations_validationId(scheme, domain, grdm_token: str, project_id: str, validation_id: str):
    """/validations/{validation_id}"""
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
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        raise UnauthorizedError
    response.raise_for_status()
    return response.json()