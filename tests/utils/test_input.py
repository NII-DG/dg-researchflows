"""input.pyのテストモジュールです。"""
# tox exec -- pytest tests/utils/test_input.py -s -vv
import pytest
from unittest.mock import patch

from data_governance.library.utils.error import UnusableVault, UnauthorizedError, ProjectNotExist, RepoPermissionError
from data_governance.library.utils.input import get_project_id, get_token, get_grdm_token, get_goveredrun_token, get_grdm_connection_parameters


class VaultMock:
    def __init__(self):
        self._store = {}
    def get_value(self, key):
        return self._store.get(key)
    def set_value(self, key, value):
        self._store[key] = value
    def delete_value(self, key):
        self._store.pop(key, None)
    def clear(self):
        self._store.clear()


@pytest.fixture(autouse=True)
def mock_vault():
    vault = VaultMock()
    with patch('data_governance.library.utils.input.Vault', new=lambda: vault):
        yield vault


# def get_project_id() -> str:
# tox exec -- pytest tests/utils/test_input.py::test_get_project_id -s -vv
def test_get_project_id(mock_vault, mocker):
    MockGrdm = mocker.patch('data_governance.library.utils.input.grdm.Grdm')
    mock_grdm = MockGrdm.return_value
    # プロジェクトIDがget_project_idから取得できる場合
    with patch.object(mock_grdm, 'get_project_id', return_value='test_project_id'):
        assert get_project_id() == 'test_project_id'
        assert mock_vault.get_value('grdm_projectid') == None
    # プロジェクトIDをVaultから取得する場合
    with patch.object(mock_grdm, 'get_project_id', return_value=None):
        mock_vault.set_value('grdm_projectid', 'vault_project_id')
        assert get_project_id() == 'vault_project_id'
        assert mock_vault.get_value('grdm_projectid') == 'vault_project_id'
    # プロジェクトIDをinputから取得する場合
    mock_vault.delete_value('grdm_projectid')
    with patch.object(mock_grdm, 'get_project_id', return_value=None):
        # 1回目: 空文字、2回目: 半角でない文字、3回目: 正しい半角文字
        inputs = ['', '全角', 'testid']
        def fake_input(prompt):
            return inputs.pop(0)
        with patch('data_governance.library.utils.input.input', side_effect=fake_input) as mock_input:
            result = get_project_id()
            assert result == 'testid'
            assert mock_vault.get_value('grdm_projectid') is None
            assert mock_input.call_count == 3
    # vaultからプロジェクトIDを取得する際、エラーが発生する場合
    with patch.object(mock_grdm, 'get_project_id', return_value=None), \
        patch.object(mock_vault, 'get_value', side_effect=Exception("Vault error")):
        with pytest.raises(UnusableVault):
            get_project_id()


# def get_token(vault_key: str, check_auth: Callable[[str], bool], msg: str) -> str:
# tox exec -- pytest tests/utils/test_input.py::test_get_token -s -vv
def test_get_token(mock_vault, mocker):
    # 'valid_token'の場合Trueを返すcheck_auth関数
    def check_auth(token):
        return token == 'valid_token'

    # Vaultから取得したトークンが有効な場合
    with patch.object(mock_vault, 'get_value', return_value='valid_token'):
        assert get_token('vault_key', check_auth, 'msg') == 'valid_token'
    # Vaultから取得したトークンが無効の場合
    mock_vault.set_value('vault_key', 'invalid_token')
    getpass_mock = mocker.patch('getpass.getpass', return_value='valid_token')
    assert get_token('vault_key', check_auth, 'msg') == 'valid_token'
    getpass_mock.assert_called_once_with('msg')
    assert mock_vault.get_value('vault_key') == 'valid_token'
    # トークンをinputから取得する場合
    mock_vault.set_value('vault_key', "")
    # 1回目: 空文字、2回目: 半角でない文字、3回目: 無効なトークン、4回目: 有効なトークン
    inputs = ['', '全角', 'invalid_token','valid_token']
    def fake_getpass(prompt):
        return inputs.pop(0)
    with patch('getpass.getpass', side_effect=fake_getpass) as mock_getpass:
        result = get_token('vault_key', check_auth, 'msg')
        assert result == 'valid_token'
        assert mock_vault.get_value('vault_key') == 'valid_token'
        assert mock_getpass.call_count == 4
    # vaultからプロジェクトIDを取得する際、エラーが発生する場合
    with patch.object(mock_vault, 'get_value', side_effect=Exception("Vault error")):
        with pytest.raises(UnusableVault):
            get_token('vault_key', check_auth, 'msg')


# def get_grdm_token(base_url: str, vault_key: str) -> str:
# tox exec -- pytest tests/utils/test_input.py::test_get_grdm_token -s -vv
def test_get_grdm_token(mock_vault):
    # Vaultから有効なトークンが取得できる場合
    with patch.object(mock_vault, 'get_value', return_value='valid_token'), \
        patch('data_governance.library.utils.input.grdm.Grdm') as MockGrdm:
        mock_grdm = MockGrdm.return_value
        mock_grdm.check_authorization.return_value = True
        result = get_grdm_token('https://example.com', 'vault_key')
        assert result == 'valid_token'
        mock_grdm.check_authorization.assert_called_once_with('https://example.com', 'valid_token')

    # Vaultから取得したトークンが無効で、ユーザー入力で有効なトークンが得られる場合
    with patch.object(mock_vault, 'get_value', return_value='invalid_token'), \
        patch('data_governance.library.utils.input.grdm.Grdm') as MockGrdm, \
        patch('getpass.getpass', return_value='valid_token') as mock_getpass:
        mock_grdm = MockGrdm.return_value
        mock_grdm.check_authorization.side_effect = [False, False, True]
        result = get_grdm_token('https://example.com', 'vault_key')
        assert result == 'valid_token'
        assert mock_grdm.check_authorization.call_count == 3
        assert mock_getpass.call_count == 2


# def get_goveredrun_token(base_url: str) -> str:
# tox exec -- pytest tests/utils/test_input.py::test_get_goveredrun_token -s -vv
def test_get_goveredrun_token(mock_vault):
    # Vaultから有効なトークンが取得できる場合
    with patch.object(mock_vault, 'get_value', return_value='valid_token'), \
        patch('data_governance.library.utils.input.dg_web.Api') as MockApi:
        instance = MockApi.return_value
        instance.check_governedrun_token.return_value = True
        result = get_goveredrun_token('https://example.com')
        assert result == 'valid_token'
        instance.check_governedrun_token.assert_called_once_with('https://example.com', 'valid_token')

    # Vaultから取得したトークンが無効で、ユーザー入力で有効なトークンが得られる場合
    with patch.object(mock_vault, 'get_value', return_value='invalid_token'), \
        patch('data_governance.library.utils.input.dg_web.Api') as MockApi, \
        patch('getpass.getpass', return_value='valid_token') as mock_getpass:
        instance = MockApi.return_value
        instance.check_governedrun_token.side_effect = [False, False, True]
        result = get_goveredrun_token('https://example.com')
        assert result == 'valid_token'
        assert instance.check_governedrun_token.call_count == 3
        assert mock_getpass.call_count == 2


# def get_grdm_connection_parameters(base_url: str) -> tuple[str, str]:
# tox exec -- pytest tests/utils/test_input.py::test_get_grdm_connection_parameters -s -vv
def test_get_grdm_connection_parameters(mock_vault, mocker):
    base_url = 'https://example.com'
    mocker.patch('data_governance.library.utils.input.get_project_id', return_value='pid')
    mocker.patch('data_governance.library.utils.input.get_grdm_token', return_value='token')
    MockGrdm = mocker.patch('data_governance.library.utils.input.grdm.Grdm')
    mock_grdm = MockGrdm.return_value

    # 正常系: 権限あり、プロジェクトID取得可能
    with patch.object(mock_grdm, 'check_permission', return_value=True):
        result = get_grdm_connection_parameters(base_url)
        assert result == ('token', 'pid')
        assert mock_vault.get_value('grdm_projectid') == 'pid'

    # 権限不足: check_permissionがFalse
    with patch.object(mock_grdm, 'check_permission', return_value=False):
        with pytest.raises(RepoPermissionError):
            get_grdm_connection_parameters(base_url)
        assert mock_vault.get_value('grdm_projectid') == ''

    # UnauthorizedError: get_grdm_tokenでUnauthorizedError発生
    with patch('data_governance.library.utils.input.get_grdm_token', side_effect=[UnauthorizedError, 'token']) as mock_get_grdm_token, \
        patch.object(mock_grdm, 'check_permission', return_value=True):
        result = get_grdm_connection_parameters(base_url)
        assert result == ('token', 'pid')
        assert mock_get_grdm_token.call_count == 2
        assert mock_vault.get_value('grdm_projectid') == 'pid'

    # ProjectNotExist: check_permissionでProjectNotExist発生
    with patch.object(mock_grdm, 'check_permission', side_effect=ProjectNotExist('not exist')):
        with pytest.raises(ProjectNotExist):
            get_grdm_connection_parameters(base_url)
        assert mock_vault.get_value('grdm_projectid') == ''
