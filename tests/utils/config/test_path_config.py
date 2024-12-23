"""このモジュールはユニットテストフレームワークを用いてテストを行うモジュールです。

data_governance.library.utils.config.path_configモジュールのテストを行います。

"""
from unittest import TestCase

from data_governance.library.utils.config import path_config

class TestPathConfig(TestCase):
    """data_governance.library.utils.config.path_configモジュールのテストを行うクラスです。"""
    # test exec : python -m unittest tests.utils.config.test_path_config

    def test_get_prepare_file_name_list_for_subflow(self):
        """get_prepare_file_name_list_for_subflowメソッドをテストするメソッドです。"""
        file_names = path_config.get_prepare_file_name_list_for_subflow()
        self.assertEqual('menu.ipynb', file_names[0])
        self.assertEqual('status.json', file_names[1])
        self.assertEqual('property.json', file_names[2])
