import pytest
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.fixture
def mock_osf():
    with patch("data_governance.library.utils.storage_provider.grdm.external.OSF") as mock_osf_cls:
        mock_osf_instance = AsyncMock()
        mock_osf_instance.has_auth = True
        mock_osf_cls.return_value = mock_osf_instance
        yield mock_osf_cls, mock_osf_instance

@pytest.fixture
def mock_helpers():
    with patch("data_governance.library.utils.storage_provider.grdm.external.filter_by_path_pattern") as mock_filter, \
        patch("data_governance.library.utils.storage_provider.grdm.external.is_folder") as mock_is_folder, \
        patch("dateutil.parser.parse") as mock_parser, \
        patch("tzlocal.get_localzone") as mock_get_localzone:
        yield {
            "filter_by_path_pattern": mock_filter,
            "is_folder": mock_is_folder,
            "parse": mock_parser,
            "get_localzone": mock_get_localzone
        }