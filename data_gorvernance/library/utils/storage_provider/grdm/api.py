"""Gakunin RDMのAPIへの通信"""
from http import HTTPStatus
from urllib import parse

import requests
from requests.exceptions import RequestException

from ...error import UnauthorizedError, NotFoundURLError


def build_api_url(base_url: str, endpoint=''):
    """_summary_

    Args:
        base_url (str): Root URL (e.g. https://rdm.nii.ac.jp)
        endpoint (str, optional): endpoint for api. Defaults to ''.

    Returns:
        str: base path

    Examples:
        >>> build_api_base_url('https://rdm.nii.ac.jp')
        'https://api.rdm.nii.ac.jp/v2/'
        >>> build_api_base_url('https://rdm.nii.ac.jp', '/users/me/')
        'https://api.rdm.nii.ac.jp/v2/users/me/'
    """
    parsed = parse.urlparse(base_url)
    netloc = f'api.{parsed.netloc}'
    base_path = 'v2/'
    if not endpoint:
        endpoint = base_path
    else:
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]
        endpoint = base_path + endpoint
    if not endpoint.endswith('/'):
            endpoint = endpoint + '/'
    return parse.urlunparse((parsed.scheme, netloc, endpoint, '', '', ''))


def build_oauth_url(base_url: str, endpoint=''):
    """_summary_

    Args:
        base_url (str): Root URL (e.g. https://rdm.nii.ac.jp)
        endpoint (str, optional): endpoint for api. Defaults to ''.

    Returns:
        str: base path
    """
    parsed = parse.urlparse(base_url)
    netloc = f'accounts.{parsed.netloc}'
    if not endpoint.endswith('/'):
            endpoint = endpoint + '/'
    return parse.urlunparse((parsed.scheme, netloc, endpoint, '', '', ''))


def get_token_profile(base_url, token):
    """https://accounts.rdm.nii.ac.jp/oauth2/profile"""
    endpoint = '/oauth2/profile'
    api_url = build_oauth_url(base_url, endpoint)
    headers = {
        'Authorization': 'Bearer {}'.format(token)
    }
    response = requests.get(url=api_url, headers=headers)
    response.raise_for_status()
    return response.json()


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
