

from .config import path_config, message as msg_config
from .storage_provider.grdm import get_project_id



def get_token():
    # Vaultからトークンを取得する
    token = ""
    if token:
        return token
    while True:
        token = input(msg_config.get('form', 'pls_input_token'))
        if token:
            break
    return token

def get_project_id():
    project_id = get_project_id()
    if project_id:
        return project_id
    while True:
        project_id = input(msg_config.get('form', 'pls_input_token'))
        if project_id:
            break
    return project_id
