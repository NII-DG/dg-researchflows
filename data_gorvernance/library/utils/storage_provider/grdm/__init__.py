from .main import get_project_id, get_projects_list, sync, get_project_metadata, get_collaborator_list

from urllib import parse

BASE_URL = 'https://api.rdm.nii.ac.jp/v2/'
parse_url = parse.urlparse(BASE_URL)
SCHEME = parse_url.scheme
DOMAIN = parse_url.netloc



