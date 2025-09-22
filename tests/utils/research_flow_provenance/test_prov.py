"""prov.pyのテストモジュールです。"""
import hashlib
from pathlib import Path
import tempfile
import os
from unittest.mock import ANY, MagicMock, patch
from urllib.parse import urljoin

import pytest
from data_governance.library.utils.research_flow_provenance.prov import calculate_sha256, ProvenanceManager

def test_calculate_sha256():
    # テスト用の内容
    content = b"Hello, World!"

    # 期待されるハッシュ値を計算
    expected_hash = hashlib.sha256(content).hexdigest()

    # 一時ファイルを作成して書き込み
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(content)
        tmp_file_path = tmp_file.name

    try:
        # 関数の出力をテスト
        result = calculate_sha256(tmp_file_path)
        assert result == expected_hash
    finally:
        # テスト後に一時ファイルを削除
        os.remove(tmp_file_path)

class TestProvenanceManager:
    """ProvenanceManagerクラスのテストクラスです。"""

    @patch("data_governance.library.utils.research_flow_provenance.prov.RDFStore")
    @patch("data_governance.library.utils.research_flow_provenance.prov.ProvenanceSearcher")
    @patch("data_governance.library.utils.research_flow_provenance.prov.OutputProvenance")
    @patch("data_governance.library.utils.research_flow_provenance.prov.ProvenanceEditor")
    @patch("data_governance.library.utils.research_flow_provenance.prov.External")
    def test_provenance_manager_init(self, mock_external, mock_editor, mock_output, mock_searcher, mock_rdfstore):
        """コンストラクタの正常実行テストケースです。"""
        # モックの設定
        mock_rdfstore_instance = MagicMock()
        mock_rdfstore.return_value = mock_rdfstore_instance

        mock_searcher_instance = MagicMock()
        mock_searcher.return_value = mock_searcher_instance

        mock_output_instance = MagicMock()
        mock_output.return_value = mock_output_instance

        mock_editor_instance = MagicMock()
        mock_editor.return_value = mock_editor_instance

        mock_external_instance = MagicMock()
        mock_external.return_value = mock_external_instance

        # _get_execution_user をモック化（private method）
        with patch.object(ProvenanceManager, "_get_execution_user", return_value="mock_user") as mock_get_user:
            manager = ProvenanceManager(token="dummy_token", grdm_url="http://example.com", project_id="project123")

            # 属性が正しく設定されたかを検証
            assert manager.token == "dummy_token"
            assert manager.grdm_url == "http://example.com"
            assert manager.project_id == "project123"

            # モックが使用されているか確認
            mock_rdfstore.assert_called_once()
            mock_rdfstore_instance.load_graph.assert_called_once()

            mock_searcher.assert_called_once_with(mock_rdfstore_instance)
            mock_output.assert_called_once_with(mock_searcher_instance)
            mock_editor.assert_called_once()
            mock_external.assert_called_once()

            mock_get_user.assert_called_once()
            assert manager.excution_user == "mock_user"

            # dispatch_map に必要なキーが存在するか
            expected_keys = {
                "File Copy", "File Modify", "File Compile", "File Export",
                "File Upload", "File Delete", "Collection Edit", "Provenance Edit"
            }
            assert expected_keys.issubset(manager.dispatch_map.keys())

    def test_get_execution_user_existing(self, manager):
        """実行ユーザーが既に存在していた場合のテストケースです。"""
        mgr, mock_searcher, mock_editor, mock_external = manager

        # モック返却値
        mock_external.get_user_info.return_value = {
            'data': {
                'id': 'user123',
                'attributes': {'full_name': 'John Doe'}
            }
        }
        mock_searcher.get_excution_user.return_value = "existing:agent:uri"

        result = mgr._get_execution_user()

        assert result == "existing:agent:uri"
        mock_external.get_user_info.assert_called_once_with("http://test.url", "test_token")
        mock_searcher.get_excution_user.assert_called_once_with("urn:agent:user123")
        mock_editor.create_agent.assert_not_called()

    def test_get_execution_user_creates_new(self, manager):
        """実行ユーザーが存在しない場合のテストケースです。"""
        mgr, mock_searcher, mock_editor, mock_external = manager

        # モック返却値（ユーザー情報）
        mock_external.get_user_info.return_value = {
            'data': {
                'id': 'user123',
                'attributes': {'full_name': 'John Doe'}
            }
        }

        # 検索結果なし → create_agent を呼ぶケース
        mock_searcher.get_excution_user.return_value = None
        mock_editor.create_agent.return_value = "created:agent:uri"

        result = mgr._get_execution_user()

        assert result == "created:agent:uri"
        mock_external.get_user_info.assert_called_once_with("http://test.url", "test_token")
        mock_searcher.get_excution_user.assert_called_once_with("urn:agent:user123")
        mock_editor.create_agent.assert_called_once_with(
            "urn:agent:user123",
            ["prov:Agent", "prov:Person"],
            "John Doe"
        )

    @pytest.mark.asyncio
    async def test_handle_runs_correct_handler(self, async_manager):
        mgr, mock_external = async_manager

        # ハンドラ関数をモック（activity_type を引数として受け取る）
        mock_handler = MagicMock(return_value="handler_result")

        # dispatch_map を差し替え
        mgr.dispatch_map = {
            "File Upload": mock_handler
        }

        result = await mgr.handle("File Upload", "arg1", key="value1")

        # list_() が呼ばれたか？
        mock_external.list_.assert_awaited_once_with(
            "test_token", "http://test.url", "project123", "osfstorage/data/"
        )

        # handler が正しく呼ばれたか？
        mock_handler.assert_called_once_with("File Upload", "arg1", key="value1")

        # 戻り値の確認
        assert result == "handler_result"

        # grdm_file_info がセットされたか
        assert mgr.grdm_file_info == [{"id": "file1"}, {"id": "file2"}]

    @pytest.fixture(autouse=True)
    def setup_mgr(self, mocker):
        with patch("data_governance.library.utils.research_flow_provenance.prov.RDFStore"), \
            patch("data_governance.library.utils.research_flow_provenance.prov.ProvenanceSearcher"), \
            patch("data_governance.library.utils.research_flow_provenance.prov.OutputProvenance"), \
            patch("data_governance.library.utils.research_flow_provenance.prov.ProvenanceEditor"), \
            patch("data_governance.library.utils.research_flow_provenance.prov.External"):
            self.mgr = ProvenanceManager("token", "url", "project")

        self.mgr.grdm_file_info = {
            "/path/src_file.txt": "link://src_file",
            "/path/dst_file.txt": "link://dst_file"
        }
        self.mgr.convert_grdm_path = lambda x: x
        self.mgr.convert_grdm_link = lambda x: x
        self.mgr.searcher.get_file_entity = MagicMock(return_value=None)
        self.mgr.editor.create_entity = MagicMock(return_value="entity_uri")
        self.mgr.editor.create_activity = MagicMock()
        self.mgr.rdf_store.reload = MagicMock()
        self.mgr.output.write = MagicMock()
        self.mgr.excution_user = "user_uri"

        mocker.patch("data_governance.library.utils.research_flow_provenance.prov.calculate_sha256", side_effect=lambda x: "fakehash_" + x)

    def test_handle_file_copy_success(self):
        """正常系のテストケースです。"""
        copied_files = {"/path/dst_file.txt": "/path/src_file.txt"}
        self.mgr._handle_file_copy("File Copy", copied_files)

        # コピー元の呼び出し
        self.mgr.searcher.get_file_entity.assert_called_with("link://src_file")
        self.mgr.editor.create_entity.assert_any_call("/path/src_file.txt", "link://src_file", "fakehash_/path/src_file.txt")

        # コピー先の呼び出し（activity_id部分は部分一致で）
        calls = self.mgr.editor.create_entity.call_args_list
        assert any(
            c[0][0] == "/path/dst_file.txt" and
            c[0][1] == "link://dst_file" and
            c[0][2] == "fakehash_/path/dst_file.txt" and
            c[0][3].startswith(self.mgr.FILE_COPY_BASE) and
            c[0][4] == "entity_uri" and
            c[0][5] == "user_uri"
            for c in calls
        )

        self.mgr.editor.create_activity.assert_called_once()
        self.mgr.rdf_store.reload.assert_called_once()
        self.mgr.output.write.assert_called_once_with(["link://src_file", "link://dst_file"])

    def test_handle_file_copy_src_not_found(self):
        """コピー元ファイルが存在しない場合のテストケースです。"""
        copied_files = {"/path/dst_file.txt": "/path/unknown_src.txt"}  # 存在しないファイル
        with pytest.raises(FileNotFoundError):
            self.mgr._handle_file_copy("File Copy", copied_files)

    def test_handle_file_copy_dst_not_found(self):
        """コピー先ファイルが存在しない場合のテストケースです。"""
        copied_files = {"/path/unknown_dst.txt": "/path/src_file.txt"}  # コピー先が存在しない
        with pytest.raises(FileNotFoundError):
            self.mgr._handle_file_copy("File Copy", copied_files)

    def test_handle_file_modify_success(self):
        """正常系のテストケースです。"""
        self.mgr._handle_file_modify("File Modify", "/path/src_file.txt", "/path/dst_file.txt")

        self.mgr.searcher.get_file_entity.assert_called_once_with("link://src_file")

        self.mgr.editor.create_entity.assert_any_call(
            "/path/src_file.txt", "link://src_file", "fakehash_/path/src_file.txt"
        )

        self.mgr.editor.create_entity.assert_any_call(
            "/path/dst_file.txt", "link://dst_file", "fakehash_/path/dst_file.txt",
            ANY,  # activity_id
            "src_entity_uri",
            "user_uri"
        )

        self.mgr.editor.create_activity.assert_called_once()
        self.mgr.rdf_store.reload.assert_called_once()
        self.mgr.output.write.assert_called_once_with(["link://src_file", "link://dst_file"])

    def test_handle_file_modify_src_not_found(self):
        """編集元ファイルが存在しない場合のテストケースです。"""
        # src_fileが存在しないケース
        self.mgr.grdm_file_info.pop("/path/src_file.txt")

        with pytest.raises(FileNotFoundError) as e:
            self.mgr._handle_file_modify("File Modify", "/path/src_file.txt", "/path/dst_file.txt")

        assert "がGRDMに存在しない" in str(e.value)

    def test_handle_file_modify_dst_not_found(self):
        """編集先ファイルが存在しない場合のテストケースです。"""
        # dst_fileが存在しないケース
        self.mgr.grdm_file_info.pop("/path/dst_file.txt")

        with pytest.raises(FileNotFoundError) as e:
            self.mgr._handle_file_modify("File Modify", "/path/src_file.txt", "/path/dst_file.txt")

        assert "がGRDMに存在しない" in str(e.value)

    def test_handle_file_compile_success(self, prov_manager, mocker):
        """正常系のテストケースです。"""
        mocker.patch("data_governance.library.utils.research_flow_provenance.prov.calculate_sha256", side_effect=lambda x: f"hash_{x}")

        agent_info = [{"agent_name": "gcc", "agent_type": "Software"}]
        prov_manager._handle_file_compile("File Compile", "/path/dst_file.out", ["/path/src1.py", "/path/src2.py"], agent_info)

        prov_manager.searcher.get_file_entity.assert_any_call("link://src1")
        prov_manager.searcher.get_file_entity.assert_any_call("link://src2")

        prov_manager.editor.create_entity.assert_any_call("/path/src1.py", "link://src1", "hash_/path/src1.py")
        prov_manager.editor.create_entity.assert_any_call("/path/src2.py", "link://src2", "hash_/path/src2.py")

        prov_manager.editor.create_entity.assert_any_call(
            "/path/dst_file.out", "link://dst", "hash_/path/dst_file.out",
            ANY,  # activity_id
            "entity2",  # 最後のsrc_uri
            ["user_uri", "urn:agent:gcc"]
        )

        prov_manager.editor.create_activity.assert_called_once_with(
            ANY, "File Compile", ["entity1", "entity2"], ["user_uri", "urn:agent:gcc"]
        )

        prov_manager.rdf_store.reload.assert_called_once()
        prov_manager.output.write.assert_called_once_with(["link://src1", "link://src2", "link://dst"])

    def test_handle_file_compile_src_not_found(self, prov_manager):
        """コンパイル元ファイルが存在しない場合のテストケースです。"""
        prov_manager.grdm_file_info.pop("/path/src2.py")

        with pytest.raises(FileNotFoundError, match="/path/src2.pyがGRDMに存在しない"):
            prov_manager._handle_file_compile("File Compile", "/path/dst_file.out", ["/path/src1.py", "/path/src2.py"])

    def test_handle_file_compile_dst_not_found(self, prov_manager):
        """コンパイル先ファイルが存在しない場合のテストケースです。"""
        prov_manager.grdm_file_info.pop("/path/dst_file.out")

        with pytest.raises(FileNotFoundError, match="/path/dst_file.outがGRDMに存在しない"):
            prov_manager._handle_file_compile("File Compile", "/path/dst_file.out", ["/path/src1.py", "/path/src2.py"])

    def test_handle_file_export_success(self, prov_manager, mocker):
        """正常系のテストケースです。"""
        mocker.patch("data_governance.library.utils.research_flow_provenance.prov.calculate_sha256", side_effect=lambda x: f"hash_{x}")

        agent_info = [{"agent_name": "external_tool", "agent_type": "Software"}]

        prov_manager._handle_file_export(
            "File Export",
            "/path/dst_file.out",
            ["/path/src1.py", "/path/src2.py"],
            agent_info
        )

        prov_manager.searcher.get_file_entity.assert_any_call("link://src1")
        prov_manager.searcher.get_file_entity.assert_any_call("link://src2")

        prov_manager.editor.create_entity.assert_any_call("/path/src1.py", "link://src1", "hash_/path/src1.py")
        prov_manager.editor.create_entity.assert_any_call("/path/src2.py", "link://src2", "hash_/path/src2.py")

        prov_manager.editor.create_entity.assert_any_call(
            "/path/dst_file.out", "link://dst", "hash_/path/dst_file.out",
            ANY,  # activity_id
            "entity2",  # 最後に生成された src_uri
            ["user_uri", "urn:agent:external_tool"]
        )

        prov_manager.editor.create_activity.assert_called_once_with(
            ANY, "File Export", ["entity1", "entity2"], ["user_uri", "urn:agent:external_tool"]
        )

        prov_manager.rdf_store.reload.assert_called_once()
        prov_manager.output.write.assert_called_once_with(["link://src1", "link://src2", "link://dst"])

    def test_handle_file_export_src_not_found(self, prov_manager):
        """エクスポート元ファイルが存在しない場合のテストケースです。"""
        prov_manager.grdm_file_info.pop("/path/src2.py")

        with pytest.raises(FileNotFoundError, match="/path/src2.pyがGRDMに存在しない"):
            prov_manager._handle_file_export(
                "File Export",
                "/path/dst_file.out",
                ["/path/src1.py", "/path/src2.py"]
            )

    def test_handle_file_export_dst_not_found(self, prov_manager):
        """エクスポート先ファイルが存在しない場合のテストケースです。"""
        prov_manager.grdm_file_info.pop("/path/dst_file.out")

        with pytest.raises(FileNotFoundError, match="/path/dst_file.outがGRDMに存在しない"):
            prov_manager._handle_file_export(
                "File Export",
                "/path/dst_file.out",
                ["/path/src1.py", "/path/src2.py"]
            )

    def test_handle_file_upload_success(self, prov_manager, mocker):
        """正常系のテストケースです。"""
        mocker.patch("data_governance.library.utils.research_flow_provenance.prov.calculate_sha256", side_effect=lambda x: f"hash_{x}")

        upload_files = {
            "/path/dst1.txt": "link://source1",
            "/path/dst2.txt": "link://source2"
        }

        prov_manager._handle_file_upload("File Upload", upload_files)

        prov_manager.editor.create_entity.assert_any_call(
            "/path/dst1.txt", "link://dst1", "hash_/path/dst1.txt",
            ANY, "link://source1", "user_uri"
        )

        prov_manager.editor.create_entity.assert_any_call(
            "/path/dst2.txt", "link://dst2", "hash_/path/dst2.txt",
            ANY, "link://source2", "user_uri"
        )

        prov_manager.editor.create_activity.assert_called_once_with(
            ANY, "File Upload", ["link://source1", "link://source2"], "user_uri"
        )

        prov_manager.rdf_store.reload.assert_called_once()
        prov_manager.output.write.assert_called_once_with(["link://dst1", "link://dst2"])

    def test_handle_file_upload_dst_not_found(self, prov_manager):
        """アップロード先ファイルが存在しない場合のテストケースです。"""
        prov_manager.grdm_file_info.pop("/path/dst2.txt")

        upload_files = {
            "/path/dst1.txt": "link://source1",
            "/path/dst2.txt": "link://source2"  # 存在しない
        }

        with pytest.raises(FileNotFoundError, match="/path/dst2.txtがGRDMに存在しない"):
            prov_manager._handle_file_upload("File Upload", upload_files)

    def test_handle_file_delete_success(self, prov_manager):
        """正常系のテストケースです。"""
        prov_manager.searcher.get_file_entity.return_value = "entity_uri"

        prov_manager._handle_file_delete("File Delete", "/path/delete.txt")

        prov_manager.searcher.get_file_entity.assert_called_once_with("link://delete")
        prov_manager.editor.create_activity.assert_called_once_with(
            ANY, "File Delete", ["entity_uri"], "user_uri"
        )
        prov_manager.rdf_store.reload.assert_called_once()
        prov_manager.output.write.assert_called_once_with(["link://delete"])

    def test_handle_file_delete_grdm_info_not_found(self, prov_manager):
        """GRDM上にファイルが存在しない場合のテストケースです。"""
        prov_manager.grdm_file_info.pop("/path/delete.txt")

        with pytest.raises(FileNotFoundError, match="/path/delete.txtがGRDMに存在しない"):
            prov_manager._handle_file_delete("File Delete", "/path/delete.txt")

    def test_handle_file_delete_entity_not_found(self, prov_manager):
        """エンティティが存在しない場合のテストケースです。"""
        prov_manager.searcher.get_file_entity.return_value = None

        with pytest.raises(FileNotFoundError, match="/path/delete.txtのEntityが存在しない"):
            prov_manager._handle_file_delete("File Delete", "/path/delete.txt")

    def test_handle_collection_edit_success(self, prov_manager):
        """正常系テストケースです。"""
        collection_info = [
            {
                "collection_id": "col1",
                "old_member": ["link://file1", "link://file2"],
                "new_member": ["link://file3"]
            },
            {
                "collection_id": "col2",
                "old_member": ["link://fileA"],
                "new_member": ["link://fileB", "link://fileC"]
            }
        ]

        prov_manager._handle_collection_edit("Collection Edit", collection_info)

        assert prov_manager.editor.edit_collection.call_count == 2
        assert prov_manager.editor.create_activity.call_count == 2

        # 最初の呼び出し内容をざっくり確認
        prov_manager.editor.edit_collection.assert_any_call("col1", ANY, ["link://file3"])
        prov_manager.editor.create_activity.assert_any_call(
            ANY, "Collection Edit", ["col1"], "user_uri", old_provenances=["link://file1", "link://file2"]
        )

        # 出力されるファイル一覧の確認
        prov_manager.output.write.assert_called_once()
        written_files = prov_manager.output.write.call_args[0][0]
        expected_files = list(set(
            ["link://file1", "link://file2", "link://file3", "link://fileA", "link://fileB", "link://fileC"]
        ))
        assert sorted(written_files) == sorted(expected_files)

        prov_manager.rdf_store.reload.assert_called_once()

    def test_handle_provenance_edit_success(self, prov_manager):
        """正常系テストケースです。"""
        entity_id = "entity://123"
        old_prov = ["link://old1", "link://old2"]
        new_prov = ["link://new1", "link://new2"]

        prov_manager._handle_provenance_edit("Provenance Edit", entity_id, old_prov, new_prov, comment="updated")

        # edit_entity が正しく呼ばれたか
        prov_manager.editor.edit_entity.assert_called_once_with(entity_id, ANY, new_prov)

        # create_activity の呼び出し確認
        prov_manager.editor.create_activity.assert_called_once_with(
            ANY, "Provenance Edit", entity_id, "user_uri", old_prov
        )

        # RDF更新と出力確認
        prov_manager.rdf_store.reload.assert_called_once()
        prov_manager.output.write.assert_called_once()

        written_files = prov_manager.output.write.call_args[0][0]
        expected_files = list(set(old_prov + new_prov))
        assert sorted(written_files) == sorted(expected_files)

    def test_convert_grdm_path(self):
        """正常系テストケースです。"""
        class Dummy:
            def convert_grdm_path(self, grdm_path: str) -> str:
                return f"link://{grdm_path}"

        mgr = Dummy()

        assert mgr.convert_grdm_path("osfstorage/work/data.txt") == "link://osfstorage/work/data.txt"
        assert mgr.convert_grdm_path("osfstorage/data.csv") == "link://osfstorage/data.csv"

    def test_convert_grdm_link(self):
        """正常系テストケースです。"""
        class Dummy:
            def __init__(self, project_id, grdm_url):
                self.project_id = project_id
                self.grdm_url = grdm_url

            def convert_grdm_link(self, file_id):
                files = "files"
                osfstorage = "osfstorage"
                path = "/".join([self.project_id, files, osfstorage, file_id])
                return urljoin(self.grdm_url + "/", path)

    def test_check_file_exist(self):
        """正常系テストケースです。"""
        class Dummy:
            def __init__(self):
                self.searcher = MagicMock()
            def check_file_exist(self, relative_path):
                parts = Path(relative_path).parts
                data_index = parts.index('data')
                base_path = Path(*parts[:data_index])
                dir_path = Path(*parts[data_index:])

                results = self.searcher.get_all_entities(dir_path)

                error_files = {}
                for label, ids in results.items():
                    file_path = os.path.join(base_path, label)

                    if not os.path.exists(file_path):
                        error_files[label] = ids

                return error_files
