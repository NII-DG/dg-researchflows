from .api import get_projects
from .main import get_project_id, sync, get_project_metadata

from urllib import parse

BASE_URL = 'https://api.rdm.nii.ac.jp/v2/'
parse_url = parse.urlparse(BASE_URL)
SCHEME = parse_url.scheme
DOMAIN = parse_url.netloc



