"""このモジュールはユニットテストフレームワークを用いてテストを行うモジュールです。
data_gorvernance.library.utils.config.path_configモジュールのテストを行います。
"""
from unittest import TestCase
from data_gorvernance.library.utils.config import path_config
import os

class TestPathConfig(TestCase):
    """data_gorvernance.library.utils.config.path_configモジュールのテストを行います。

    get_prepare_file_name_list_for_subflowメソッドが正しく機能するかをテストするためのメソッドを記載しています。

    """
    # test exec : python -m unittest tests.utils.config.test_path_config

    def test_get_prepare_file_name_list_for_subflow(self):
        """get_prepare_file_name_list_for_subflowメソッドをテストするメソッドです。

        このメソッドではget_prepare_file_name_list_for_subflowを呼び出すことででファイル名のリストを取得し、期待通りの値が入っているか確認します。

        exsample:
            >>> TestPathConfig.test_get_prepare_file_name_list_for_subflow()
        
        Note:
            特にありません。

        """
        file_names = path_config.get_prepare_file_name_list_for_subflow()
        self.assertEqual('menu.ipynb', file_names[0])
        self.assertEqual('status.json', file_names[1])
        self.assertEqual('property.json', file_names[2])