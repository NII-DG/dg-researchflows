""" トークン取得のモジュールです。

各種トークンやプロジェクトIDを取得する関数が記載されています。

"""
import getpass
from typing import Callable

from . import dg_web
from .config import message as msg_config
from .error import UnusableVault, UnauthorizedError, ProjectNotExist, RepoPermissionError
from .storage_provider import grdm
from .string import StringManager
from .vault import Vault


def get_project_id() -> str:
    """ プロジェクトIDを取得する関数です。

    Returns:
        str: プロジェクトIDを返す。

    """
    grdm_connect = grdm.Grdm()
    project_id = grdm_connect.get_project_id()
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


def get_token(key: str, func: Callable[[str], bool], message: str) -> str:
    """ vaultもしくはinputからトークンを取得する関数です。

    Args:
        key (str): トークンをvaultで保存するときのキーを設定します。
        func (Callable[[str], bool]): トークンの有効性を確認する関数を設定します。
        message(str): inputを求める際の表示メッセージを設定します。

    Returns:
        str: トークンを返す。

    Raises:
        UnusableVault: vaultの利用に不具合があったときのエラー

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


def get_grdm_token(base_url: str, vault_key: str) -> str:
    """ GRDMのパーソナルアクセストークンを取得する関数です。

    Args:
        base_url(str):GRDMのURL
        vault_key(str):grdmのパーソナルアクセストークンキー

    Returns:
        str: パーソナルアクセストークンを返す。

    Raises:
        UnusableVault: vaultが利用できない
        requests.exceptions.RequestException: 通信不良

    """
    def check_auth(token: str) -> bool:
        """ トークンの有効性を検証する関数です。

        Args:
            token (str): パーソナルアクセストークンを設定します。

        Returns:
            bool: トークンの有効性を返す。

        """
        grdm_connect = grdm.Grdm()
        return grdm_connect.check_authorization(base_url, token)

    return get_token(vault_key, check_auth, msg_config.get('form', 'pls_input_grdm_token'))


def get_goveredrun_token(base_url: str) -> str:
    """ Governed Runのトークンを取得する関数です。

    Args:
        base_url(str):WdG-webのURL

    Returns:
        str: Governed Runのトークンを返す。

    Raises:
        UnusableVault: vaultが利用できない
        requests.exceptions.RequestException: 通信不良

    """
    def check_auth(token: str) -> bool:
        """ Governed Runのトークンの有効性を確認する関数です。

        Args:
            token (str): Governed Runのトークンを設定します。

        Returns:
            bool: Governed Runのトークンの有効性を返す。
        """
        dgweb_api = dg_web.Api()
        return dgweb_api.check_governedrun_token(base_url, token)

    return get_token('govrun_token', check_auth, msg_config.get('form', 'pls_input_govrun_token'))


def get_grdm_connection_parameters(base_url: str) -> tuple[str, str]:
    """ GRDMのトークンとプロジェクトIDを取得する関数です。

    Args:
        base_url(str):GRDMのURL

    Returns:
        str: GRDMのトークンを返す。
        str: プロジェクトIDを返す。

    Raises:
        RepoPermissionError: プロジェクトの権限が足りない
        ProjectNotExist: プロジェクトIDが存在しない
        UnusableVault: vaultが利用できない
        requests.exceptions.RequestException: 通信不良

    """

    project_id = get_project_id()
    vault_key = 'grdm_token'

    while True:
        try:
            token = get_grdm_token(base_url, vault_key)
            grdm_connect = grdm.Grdm()
            if not grdm_connect.check_permission(base_url, token, project_id):
                raise RepoPermissionError
            break
        except UnauthorizedError:
            vault = Vault()
            vault.set_value(vault_key, '')
            continue
        except ProjectNotExist as e:
            msg = msg_config.get('form', 'project_id_not_exist').format(project_id)
            raise ProjectNotExist(msg) from e

    return token, project_id
