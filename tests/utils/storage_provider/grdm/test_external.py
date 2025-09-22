import pytest
from unittest.mock import AsyncMock, MagicMock

from requests import patch
from data_governance.library.utils.storage_provider.grdm.external import External

class TestExternal:
    """Externalクラスのテストクラスです。"""
    @pytest.mark.asyncio
    async def test_list_success(self, mock_osf, mock_helpers):
        """正常実行のテストケースです。"""
        osf_cls, osf_instance = mock_osf
        mock_filter = mock_helpers["filter_by_path_pattern"]
        mock_is_folder = mock_helpers["is_folder"]

        # Mock storage and file objects
        mock_storage = MagicMock()
        mock_storage.name = "osfstorage"

        mock_file = MagicMock()
        mock_file.path = "/test/file.txt"
        mock_file.osf_path = "/osf/file.txt"
        mock_file.date_modified = None
        mock_file.size = 123

        mock_is_folder.return_value = False
        mock_filter.return_value.__aiter__.return_value = [mock_file]

        osf_instance.project.return_value = AsyncMock()
        osf_instance.project.return_value.storages.__aiter__.return_value = [mock_storage]

        instance = External()
        instance.build_api_url = MagicMock(return_value="https://grdm.fake/api/v1")

        result = await instance.list_(
            token="dummy_token",
            base_url="https://grdm.fake",
            project_id="abc123",
            base_path=None,
            long_format=False
        )

        expected = {"osfstorage/test/file.txt": "/osf/file.txt"}
        assert result == expected
        osf_instance.aclose.assert_awaited()

    @pytest.mark.asyncio
    async def test_list_auth_failure(self, mock_osf):
        """認証に失敗した場合のテストケースです。"""
        osf_cls, osf_instance = mock_osf
        osf_instance.has_auth = False

        instance = External()
        instance.build_api_url = MagicMock(return_value="https://grdm.fake/api/v1")

        with pytest.raises(KeyError, match="To upload a file you need to provide"):
            await instance.list_(
                token="dummy_token",
                base_url="https://grdm.fake",
                project_id="abc123"
            )

    @pytest.mark.asyncio
    async def test_list_with_base_path(self, mock_osf, mock_helpers):
        """base_path が指定されていているテストケースです。"""
        osf_cls, osf_instance = mock_osf
        mock_filter = mock_helpers["filter_by_path_pattern"]
        mock_is_folder = mock_helpers["is_folder"]

        # Mock storage and file objects
        mock_storage = MagicMock()
        mock_storage.name = "osfstorage"

        mock_file = MagicMock()
        mock_file.path = "/dir/file.txt"
        mock_file.osf_path = "/osf/dir/file.txt"
        mock_file.date_modified = None
        mock_file.size = 123

        mock_is_folder.return_value = False
        mock_filter.return_value.__aiter__.return_value = [mock_file]

        osf_instance.project.return_value = AsyncMock()
        osf_instance.project.return_value.storages.__aiter__.return_value = [mock_storage]

        instance = External()
        instance.build_api_url = MagicMock(return_value="https://grdm.fake/api/v1")

        result = await instance.list_(
            token="dummy_token",
            base_url="https://grdm.fake",
            project_id="abc123",
            base_path="osfstorage/dir",  # ← ココがポイント
            long_format=False
        )

        expected = {"osfstorage/dir/file.txt": "/osf/dir/file.txt"}
        assert result == expected

    @pytest.mark.asyncio
    async def test_list_with_long_format(self, mock_osf, mock_helpers):
        """long_format=True の場合のテストケースです。"""
        osf_cls, osf_instance = mock_osf
        mock_filter = mock_helpers["filter_by_path_pattern"]
        mock_is_folder = mock_helpers["is_folder"]
        mock_parser = mock_helpers["parse"]
        mock_get_localzone = mock_helpers["get_localzone"]

        mock_storage = MagicMock()
        mock_storage.name = "osfstorage"

        mock_file = MagicMock()
        mock_file.path = "/file.txt"
        mock_file.osf_path = "/osf/file.txt"
        mock_file.date_modified = "2023-09-01T12:00:00Z"
        mock_file.size = 999

        mock_is_folder.return_value = False
        mock_filter.return_value.__aiter__.return_value = [mock_file]

        # パーサーの返り値
        parsed_dt = MagicMock()
        parsed_dt.astimezone.return_value.strftime.return_value = "2023-09-01 21:00:00"
        mock_parser.return_value = parsed_dt

        osf_instance.project.return_value = AsyncMock()
        osf_instance.project.return_value.storages.__aiter__.return_value = [mock_storage]

        instance = External()
        instance.build_api_url = MagicMock(return_value="https://grdm.fake/api/v1")

        with patch("builtins.print") as mock_print:
            result = await instance.list_(
                token="dummy_token",
                base_url="https://grdm.fake",
                project_id="abc123",
                long_format=True
            )

            expected = {}  # long_format=True のときは return 値は変わらない
            assert result == expected

            # printが呼ばれていることを確認
            mock_print.assert_called_once()