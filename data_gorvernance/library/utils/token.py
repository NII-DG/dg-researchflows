
from IPython.display import clear_output

from .config import path_config, message as msg_config
from .storage_provider import grdm
from .checker import StringManager


def get_token():
    # Vaultからトークンを取得する
    token = ""
    if token:
        return token
    while True:
        token = input(msg_config.get('form', 'pls_input_token'))
        token = StringManager.strip(token)
        if StringManager.is_empty(token):
            continue
        if not StringManager.is_half(token):
            continue
        break
    return token

def get_project_id():
    project_id = grdm.get_project_id()
    if project_id:
        return project_id
    while True:
        project_id = input(msg_config.get('form', 'pls_input_project_id'))
        project_id = StringManager.strip(project_id)
        if StringManager.is_empty(project_id):
            continue
        if not StringManager.is_half(project_id):
            continue
        break
    return project_id
