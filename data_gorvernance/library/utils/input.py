import getpass
from typing import Callable

from . import dg_web
from .config import message as msg_config
from .storage_provider import grdm
from .string import StringManager
from .vault import Vault
from .error import UnusableVault, UnauthorizedError, NotFoundURLError, PermissionError


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


def get_token(key:str, func:Callable[[str], bool], message:str) -> str:
    """vaultもしくはinputからトークンを取得する

    Args:
        key (str): トークンをvaultで保存するときのキー
        func (Callable[[str], bool]): トークンの有効性を確認するメソッド
        message(str): inputを求める際の表示メッセージ

    Raises:
        UnusableVault: vaultの利用に不具合があったときのエラー

    Returns:
        str: トークン
    """
    try:
        vault = Vault()
        token = vault.get_value(key)
    except Exception as e:
        raise UnusableVault from e

    # 有効性確認
    if token and func(token):
        return token

    while True:
        token = getpass.getpass(message)

        # 形式確認
        token = StringManager.strip(token)
        if StringManager.is_empty(token):
            continue
        if not StringManager.is_half(token):
            continue

        # 有効性確認
        if not func(token):
            continue

        break

    vault.set_value(key, token)
    return token


def get_grdm_token(vault_key):
    """GRDMのパーソナルアクセストークンを取得する

    Raises:
        UnusableVault: vaultが利用できない
        requests.exceptions.RequestException: 通信不良

    Returns:
        str: パーソナルアクセストークン
    """
    def check_auth(token):
        return grdm.check_authorization(grdm.BASE_URL, token)

    return get_token(vault_key, check_auth, msg_config.get('form', 'pls_input_grdm_token'))


def get_goveredrun_token():
    """Governed Runのトークンを取得する

    Raises:
        UnusableVault: vaultが利用できない
        requests.exceptions.RequestException: 通信不良

    Returns:
        str: Governed Runのトークン
    """
    def check_auth(token):
        return dg_web.check_governedrun_token(dg_web.SCHEME, dg_web.DOMAIN, token)

    return get_token('govrun_token', check_auth, msg_config.get('form', 'pls_input_govrun_token'))


def get_grdm_connection_parameters():
    """GRDMのトークンとプロジェクトIDを取得する

    Raises:
        NotFoundURLError: プロジェクトIDが存在しない
        UnusableVault: vaultが利用できない
        requests.exceptions.RequestException: 通信不良
    """

    project_id = get_project_id()
    vault_key = 'grdm_token'

    while True:
        try:
            token = get_grdm_token(vault_key)
            if not grdm.check_permission(grdm.BASE_URL, token, project_id):
                msg = msg_config.get('form', 'insufficient_permission')
                raise PermissionError(msg)
            break
        except UnauthorizedError:
            vault = Vault()
            vault.set_value(vault_key, '')
            continue
        except NotFoundURLError as e:
            msg = msg_config.get('form', 'project_id_not_exist').format(project_id)
            raise NotFoundURLError(msg) from e

    return token, project_id