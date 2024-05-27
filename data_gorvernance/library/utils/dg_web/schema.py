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
