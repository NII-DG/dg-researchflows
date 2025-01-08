"""このモジュールはユニットテストフレームワークを用いてテストを行うモジュールです。

data_governance.library.utils.config.messageモジュールのメソッドのテストを行います。

"""
from unittest import TestCase

from data_governance.library.utils.config import message

class TestMessageConfig(TestCase):
    """data_governance.library.utils.config.messageモジュールのテストを行うクラスです。"""
    # test exec : python -m unittest tests.utils.config.test_message

    def test_get(self):
        """getメソッドをテストするメソッドです。

        このメソッドではgetメソッドでメッセージを取得し、期待通りの値が返ってくるか確認します。

        """
        research_preparation = message.get('research_flow_phase_display_name', 'plan')
        self.assertEqual('研究準備', research_preparation)
