"""GRDMのAPIへの通信"""
from urllib import parse
import requests
from http import HTTPStatus

from ...error import UnauthorizedError


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
    data = response.json()['data']
    return {d['id']: d['attributes']['title'] for d in data}


def get_project_registrations(scheme, domain, token, project_id):
    """https://api.rdm.nii.ac.jp/v2/nodes/{project_id}/registrations"""
    sub_url = f'v2/nodes/{project_id}/registrations'
    api_url = parse.urlunparse((scheme, domain, sub_url, "", "", ""))
    headers = {
    'Authorization': 'Bearer {}'.format(token)
    }
    response = requests.get(url=api_url, headers=headers)
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        raise UnauthorizedError
    response.raise_for_status()
    return response.json()

