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