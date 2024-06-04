import getpass

from IPython.display import clear_output

from .config import message as msg_config
from .storage_provider import grdm
from .string import StringManager
from .vault import Vault
from .storage_provider import grdm
from .error import UnauthorizedError, UnusableVault


def get_grdm_token():
    """トークンを取得する

    Raises:
        UnusableVault: vaultが利用できない
        requests.exceptions.RequestException: 通信不良

    Returns:
        str: トークン
    """

    TOKEN_KEY = 'grdm_token'

    # Vaultからトークンを取得する
    try:
        vault = Vault()
        token = vault.get_value(TOKEN_KEY)
    except Exception as e:
        raise UnusableVault from e

    if token:
        # 接続確認
        try:
            grdm.get_projects(grdm.SCHEME, grdm.API_DOMAIN, token)
        except UnauthorizedError:
            pass
        else:
            return token

    while True:
        token = getpass.getpass(msg_config.get('form', 'pls_input_token'))

        # 形式確認
        token = StringManager.strip(token)
        if StringManager.is_empty(token):
            continue
        if not StringManager.is_half(token):
            continue

        # 接続確認
        try:
            grdm.get_projects(grdm.SCHEME, grdm.API_DOMAIN, token)
        except UnauthorizedError:
            continue

        break

    vault.set_value(TOKEN_KEY, token)
    return token


def get_project_id():
    """プロジェクトIDを取得する"""
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
