"""GRDMのAPIへの通信"""
from urllib import parse
import requests
from requests.exceptions import RequestException
from http import HTTPStatus

from ...error import UnauthorizedError, NotFoundURLError


def get_projects(scheme, domain, token):
    """https://api.rdm.nii.ac.jp/v2/nodes/"""
    sub_url = 'v2/nodes/'
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    headers = {
        'Authorization': 'Bearer {}'.format(token)
    }
    response = requests.get(url=api_url, headers=headers)
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        raise UnauthorizedError
    response.raise_for_status()
    return response.json()


def get_project_registrations(scheme, domain, token, project_id):
    """https://api.rdm.nii.ac.jp/v2/nodes/{project_id}/registrations"""
    sub_url = f'v2/nodes/{project_id}/registrations/'
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
        if response.status_code == HTTPStatus.NOT_FOUND:
            # プロジェクトIDが不正確
            raise NotFoundURLError(str(e)) from e
    return response.json()


def get_project_collaborators(scheme, domain, token, project_id):
    """https://api.rdm.nii.ac.jp/v2/nodes/{project_id}/contributors/"""
    sub_url = f'v2/nodes/{project_id}/contributors/'
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
        if response.status_code == HTTPStatus.NOT_FOUND:
            # プロジェクトIDが不正確
            raise NotFoundURLError(str(e)) from e
    response.raise_for_status()
    return response.json()

