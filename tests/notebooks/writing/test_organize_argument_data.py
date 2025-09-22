"""organize_argument_data.ipynbのテスト用モジュールです。"""

import os
import pytest


class TestCopySubflowData:
    """CopySubflowDataクラスをテストするクラス"""

    def test___init__(self, mocker, notebook_class):
        """コンストラクタのテスト"""
        CopySubflowData = notebook_class("data_governance.base.task.writing.organize_argument_data", "CopySubflowData")

        mocker.patch("data_governance.base.task.writing.organize_argument_data.con_config.get", return_value="https://rcos.rdm.nii.ac.jp")
        mocker.patch("data_governance.base.task.writing.organize_argument_data.grdm.Grdm")
        mocker.patch("data_governance.base.task.writing.organize_argument_data.pn.extension")
        mock_widget_box = mocker.Mock()
        mock_widget_box.append = mocker.Mock()
        mocker.patch("data_governance.base.task.writing.organize_argument_data.pn.WidgetBox", return_value=mock_widget_box)
        mock_msg_box = mocker.Mock()
        mocker.patch("data_governance.base.task.writing.organize_argument_data.MessageBox", return_value=mock_msg_box)
        mocker.patch("data_governance.base.task.writing.organize_argument_data.display")

        # --- テスト対象の呼び出し ---
        copy_subflow_data = CopySubflowData(os.path.abspath('__file__'))

        # --- アサーション（必要最低限） ---
        assert copy_subflow_data.working_path == os.path.abspath('__file__')
        assert copy_subflow_data.grdm_url == "https://rcos.rdm.nii.ac.jp"
        assert mock_msg_box.width == 900
        assert mock_widget_box.append.call_count == 2
