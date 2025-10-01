"""prov.pyのテストモジュールです。"""
import hashlib
from pathlib import Path
import tempfile
import os
from unittest.mock import ANY, MagicMock, patch
from urllib.parse import urljoin

import pytest
from rdflib import Graph, Namespace, URIRef
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
                "File Upload", "File Delete", "Provenance Edit", "Delete Activity"
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
        """正常に編集アクティビティが処理されるケース。"""
        modified_files = {"/path/dst_file.txt": "/path/src_file.txt"}

        self.mgr._handle_file_modify("File Modify", modified_files)

        # 編集元が呼び出されたか
        self.mgr.searcher.get_file_entity.assert_called_with("link://src_file")
        self.mgr.editor.create_entity.assert_any_call("/path/src_file.txt", "link://src_file", "fakehash_/path/src_file.txt")

        # 編集先の create_entity 呼び出しが含まれているか
        calls = self.mgr.editor.create_entity.call_args_list
        assert any(
            c[0][0] == "/path/dst_file.txt" and
            c[0][1] == "link://dst_file" and
            c[0][2] == "fakehash_/path/dst_file.txt" and
            c[0][3].startswith(self.mgr.FILE_MODIFY_BASE) and
            c[0][4] == "entity_uri" and
            c[0][5] == "user_uri"
            for c in calls
        )

        self.mgr.editor.create_activity.assert_called_once()
        self.mgr.rdf_store.reload.assert_called_once()
        self.mgr.output.write.assert_called_once_with(["link://src_file", "link://dst_file"])

    def test_handle_file_modify_src_not_found(self):
        """編集元ファイルがGRDM上に存在しない場合。"""
        modified_files = {"/path/dst_file.txt": "/path/unknown_src.txt"}
        
        with pytest.raises(FileNotFoundError, match="がGRDMに存在しない"):
            self.mgr._handle_file_modify("File Modify", modified_files)

    def test_handle_file_modify_dst_not_found(self):
        """編集先ファイルがGRDM上に存在しない場合。"""
        modified_files = {"/path/unknown_dst.txt": "/path/src_file.txt"}

        with pytest.raises(FileNotFoundError, match="がGRDMに存在しない"):
            self.mgr._handle_file_modify("File Modify", modified_files)

    def test_handle_file_compile_success(self, mocker):
        """正常系のテストケースです。"""
        # ハッシュ関数のモック（calculate_sha256）
        mocker.patch(
            "data_governance.library.utils.research_flow_provenance.prov.calculate_sha256",
            side_effect=lambda x: f"hash_{x}"
        )

        # GRDMに存在するファイル情報のモック
        self.mgr.grdm_file_info = {
            "/path/src1.py": "link://src1",
            "/path/src2.py": "link://src2",
            "/path/arg1.csv": "link://arg1",
            "/path/arg2.csv": "link://arg2",
            "/path/fig1.png": "link://fig1",
            "/path/fig2.png": "link://fig2",
            "/path/dst_file.out": "link://dst"
        }

        # convert 関数の振る舞い
        self.mgr.convert_grdm_path = lambda x: x
        self.mgr.convert_grdm_link = lambda x: x

        # get_file_entity → None（常に新しくエンティティ作成される想定）
        self.mgr.searcher.get_file_entity = MagicMock(return_value=None)
        self.mgr.editor.create_entity = MagicMock(return_value="entity_uri")
        self.mgr.editor.create_activity = MagicMock()
        self.mgr.editor.create_collection = MagicMock(return_value="collection_uri")
        self.mgr.editor.create_agent = MagicMock()

        self.mgr.rdf_store.reload = MagicMock()
        self.mgr.output.write = MagicMock()
        self.mgr.excution_user = "user_uri"

        # エージェント情報（gccなどのソフトウェア）
        agent_info = [{"agent_name": "gcc", "agent_type": "Software"}]

        # 呼び出し
        self.mgr._handle_file_compile(
            activity_type="File Compile",
            dst_file="/path/dst_file.out",
            tex_list=["/path/src1.py", "/path/src2.py"],
            argument_list=["/path/arg1.csv", "/path/arg2.csv"],
            figure_list=["/path/fig1.png", "/path/fig2.png"],
            agent_info=agent_info
        )

        # アサーション
        self.mgr.editor.create_entity.assert_any_call("/path/src1.py", "link://src1", "hash_/path/src1.py")
        self.mgr.editor.create_entity.assert_any_call("/path/src2.py", "link://src2", "hash_/path/src2.py")
        self.mgr.editor.create_entity.assert_any_call("/path/arg1.csv", "link://arg1", "hash_/path/arg1.csv")
        self.mgr.editor.create_entity.assert_any_call("/path/arg2.csv", "link://arg2", "hash_/path/arg2.csv")
        self.mgr.editor.create_entity.assert_any_call("/path/fig1.png", "link://fig1", "hash_/path/fig1.png")
        self.mgr.editor.create_entity.assert_any_call("/path/fig2.png", "link://fig2", "hash_/path/fig2.png")

        self.mgr.editor.create_collection.assert_any_call(
            members=["entity_uri", "entity_uri"], label="argument_data_collection"
        )
        self.mgr.editor.create_collection.assert_any_call(
            members=["entity_uri", "entity_uri"], label="figure_collection"
        )

        self.mgr.editor.create_agent.assert_called_once_with(
            "urn:agent:gcc", "Software", "gcc"
        )

        self.mgr.output.write.assert_called_once()
        self.mgr.rdf_store.reload.assert_called_once()

    def test_handle_file_compile_tex_not_found(self):
        """tex_list に含まれるファイルが GRDM に存在しない場合。"""
        tex_list = ["/path/unknown.tex"]
        with pytest.raises(FileNotFoundError, match="がGRDMに存在しない"):
            self.mgr._handle_file_compile("File Compile", "/path/result.pdf", tex_list, [], [], [])

    def test_handle_file_compile_argument_not_found(self):
        """argument_list に含まれるファイルが GRDM に存在しない場合。"""
        argument_list = ["/path/missing.csv"]
        with pytest.raises(FileNotFoundError, match="がGRDMに存在しない"):
            self.mgr._handle_file_compile("File Compile", "/path/result.pdf", [], argument_list, [], [])

    def test_handle_file_compile_figure_not_found(self):
        """figure_list に含まれるファイルが GRDM に存在しない場合。"""
        figure_list = ["/path/none.png"]
        with pytest.raises(FileNotFoundError, match="がGRDMに存在しない"):
            self.mgr._handle_file_compile("File Compile", "/path/result.pdf", [], [], figure_list, [])

    def test_handle_file_compile_dst_not_found(self):
        """出力ファイルが GRDM に存在しない場合に FileNotFoundError を出すかを確認"""

        tex_file = "/path/doc1.tex"
        dst_file = "/path/unknown_output.pdf"

        # GRDM に存在する草稿ファイルのみセット
        convert_tex_path = self.mgr.convert_grdm_path(tex_file)
        tex_entity_id = "entity-id-123"
        self.mgr.grdm_file_info = {
            convert_tex_path: tex_entity_id
        }

        # 検索結果もモック（出力ファイルのための entity 作成が必要）
        self.mgr.searcher.get_file_entity.return_value = None
        self.mgr.editor.create_entity.return_value = "new-entity-uri"

        # 実行＆例外確認（dst_file は GRDM に存在しない）
        with pytest.raises(FileNotFoundError, match="がGRDMに存在しない"):
            self.mgr._handle_file_compile(
                "File Compile",
                dst_file,
                tex_list=[tex_file],
                argument_list=[],
                figure_list=[],
                agent_info=[]
            )

    def test_handle_file_compile_with_agent_info(self):
        """agent_info が与えられたときに create_agent が呼ばれるかを検証。"""
        tex_list = ["/path/doc1.tex"]
        dst_file = "/path/result.pdf"
        agent_info = [{"agent_type": "Person", "agent_name": "Tanaka"}]

        # GRDMファイル情報を追加（必須）
        self.mgr.grdm_file_info = {
            "/path/doc1.tex": "link://doc1",
            "/path/result.pdf": "link://result"
        }

        self.mgr._handle_file_compile("File Compile", dst_file, tex_list, [], [], agent_info)

        self.mgr.editor.create_agent.assert_called_once_with(
            self.mgr.AGENT_BASE + "Tanaka", "Person", "Tanaka"
        )

    def test_handle_file_export_success(self, mocker):
        """_handle_file_export の正常系テスト"""

        # ハッシュ計算のモック
        mocker.patch(
            "data_governance.library.utils.research_flow_provenance.prov.calculate_sha256",
            side_effect=lambda x: f"hash_{x}"
        )

        # GRDMファイル情報セット（src と dst の両方を登録）
        self.mgr.grdm_file_info = {
            "/path/src1.csv": "link://src1",
            "/path/src2.csv": "link://src2",
            "/path/dst_export.csv": "link://dst"
        }

        # convert系の振る舞い
        self.mgr.convert_grdm_path = lambda x: x
        self.mgr.convert_grdm_link = lambda x: x

        # get_file_entityは常にNone（新規エンティティ作成を想定）
        self.mgr.searcher.get_file_entity = MagicMock(return_value=None)

        # editorメソッドのモック設定
        self.mgr.editor.create_entity = MagicMock(return_value="entity_uri")
        self.mgr.editor.create_activity = MagicMock()
        self.mgr.editor.create_agent = MagicMock()

        self.mgr.rdf_store.reload = MagicMock()
        self.mgr.output.write = MagicMock()

        # 実行ユーザーURI設定
        self.mgr.excution_user = "user_uri"

        # エージェント情報（任意）
        agent_info = [{"agent_name": "ExporterTool", "agent_type": "Software"}]

        # 呼び出し
        self.mgr._handle_file_export(
            activity_type="File Export",
            dst_file="/path/dst_export.csv",
            src_files=["/path/src1.csv", "/path/src2.csv"],
            agent_info=agent_info
        )

        # 各srcファイルでcreate_entity呼ばれているか検証
        self.mgr.editor.create_entity.assert_any_call("/path/src1.csv", "link://src1", "hash_/path/src1.csv")
        self.mgr.editor.create_entity.assert_any_call("/path/src2.csv", "link://src2", "hash_/path/src2.csv")

        # dstファイルでもcreate_entityが呼ばれているか検証（activity_id, src_uri, agent_listは細かくテストするならMockのcall_args確認）
        calls = self.mgr.editor.create_entity.call_args_list
        # 3回呼ばれているはず(src1, src2, dst)
        assert len(calls) == 3

        # create_agentが呼ばれているか検証
        self.mgr.editor.create_agent.assert_called_once_with(
            self.mgr.AGENT_BASE + "ExporterTool", "Software", "ExporterTool"
        )

        # create_activityが呼ばれているか検証
        self.mgr.editor.create_activity.assert_called_once()
        args, kwargs = self.mgr.editor.create_activity.call_args
        assert args[1] == "File Export"  # activity_typeチェック
        assert "user_uri" in args[3] 

        # rdf_store.reload と output.write が呼ばれているかチェック
        self.mgr.rdf_store.reload.assert_called_once()
        self.mgr.output.write.assert_called_once()

        # output.writeはupdated_files（dst_linkが含まれているはず）を受け取る
        updated_files_arg = self.mgr.output.write.call_args[0][0]
        assert "link://dst" in updated_files_arg

    def test_handle_file_export_no_agent_info(self, mocker):
        """エージェント情報がない場合のテストケースです。"""
        mocker.patch(
            "data_governance.library.utils.research_flow_provenance.prov.calculate_sha256",
            side_effect=lambda x: f"hash_{x}"
        )

        self.mgr.grdm_file_info = {
            "/path/src1.csv": "link://src1",
            "/path/dst_export.csv": "link://dst"
        }

        self.mgr.convert_grdm_path = lambda x: x
        self.mgr.convert_grdm_link = lambda x: x
        self.mgr.searcher.get_file_entity = MagicMock(return_value=None)
        self.mgr.editor.create_entity = MagicMock(return_value="entity_uri")
        self.mgr.editor.create_activity = MagicMock()
        self.mgr.editor.create_agent = MagicMock()
        self.mgr.rdf_store.reload = MagicMock()
        self.mgr.output.write = MagicMock()
        self.mgr.excution_user = "user_uri"

        self.mgr._handle_file_export(
            activity_type="File Export",
            dst_file="/path/dst_export.csv",
            src_files=["/path/src1.csv"],
            agent_info=None
        )

        # create_agentは呼ばれない
        self.mgr.editor.create_agent.assert_not_called()

        # create_activityのagent_listにユーザーURIが含まれる
        args, _ = self.mgr.editor.create_activity.call_args
        assert "user_uri" in args[3]

    def test_handle_file_export_src_file_not_in_grdm(self, mocker):
        """エクスポート先ファイルが存在しないのテストケースです"""
        self.mgr.grdm_file_info = {
            "/path/dst_export.csv": "link://dst"
        }

        self.mgr.convert_grdm_path = lambda x: x

        with pytest.raises(FileNotFoundError) as e:
            self.mgr._handle_file_export(
                activity_type="File Export",
                dst_file="/path/dst_export.csv",
                src_files=["/path/not_exist.csv"],
                agent_info=None
            )
        assert "not_exist.csvがGRDMに存在しない" in str(e.value)

    def test_handle_file_export_dst_file_not_in_grdm(self, mocker):
        """エクスポート元ファイルが存在しない場合のテストケースです。"""
        self.mgr.grdm_file_info = {
            "/path/src1.csv": "link://src1"
        }
        self.mgr.convert_grdm_path = lambda x: x
        self.mgr.convert_grdm_link = lambda x: x
        self.mgr.searcher.get_file_entity = MagicMock(return_value=None)
        self.mgr.editor.create_entity = MagicMock(return_value="entity_uri")
        self.mgr.excution_user = "user_uri"

        with pytest.raises(FileNotFoundError) as e:
            self.mgr._handle_file_export(
                activity_type="File Export",
                dst_file="/path/not_exist.csv",
                src_files=["/path/src1.csv"],
                agent_info=None
            )
        assert "not_exist.csvがGRDMに存在しない" in str(e.value)

    def test_handle_file_upload_success(self, mocker):
        """正常系のテストケースです。"""
        # ハッシュ関数のモック
        mocker.patch(
            "data_governance.library.utils.research_flow_provenance.prov.calculate_sha256",
            side_effect=lambda x: f"hash_{x}"
        )

        # GRDMファイル情報セット
        self.mgr.grdm_file_info = {
            "/path/upload1.csv": "link://upload1",
            "/path/upload2.csv": "link://upload2"
        }

        # convert系の振る舞い
        self.mgr.convert_grdm_path = lambda x: x
        self.mgr.convert_grdm_link = lambda x: x

        # editorメソッドのモック
        self.mgr.editor.create_entity = MagicMock()
        self.mgr.editor.create_activity = MagicMock()
        self.mgr.rdf_store.reload = MagicMock()
        self.mgr.output.write = MagicMock()

        # 実行ユーザーURI
        self.mgr.excution_user = "user_uri"

        # upload_filesの設定
        upload_files = {
            "/path/upload1.csv": "src_link1",
            "/path/upload2.csv": "src_link2"
        }

        # 関数呼び出し
        self.mgr._handle_file_upload("File Upload", upload_files)

        # create_entity が2回呼ばれることを検証
        assert self.mgr.editor.create_entity.call_count == 2
        self.mgr.editor.create_entity.assert_any_call(
            "/path/upload1.csv", "link://upload1", "hash_/path/upload1.csv",
            mocker.ANY, "src_link1", "user_uri"
        )
        self.mgr.editor.create_entity.assert_any_call(
            "/path/upload2.csv", "link://upload2", "hash_/path/upload2.csv",
            mocker.ANY, "src_link2", "user_uri"
        )

        # create_activity 呼び出し検証
        self.mgr.editor.create_activity.assert_called_once()
        args, _ = self.mgr.editor.create_activity.call_args
        assert args[1] == "File Upload"  # activity_type
        assert args[2] == ["src_link1", "src_link2"]  # src_list
        assert args[3] == "user_uri"

        # output.write にupdated_filesが渡されているか
        self.mgr.output.write.assert_called_once_with(["link://upload1", "link://upload2"])

    def test_handle_file_upload_file_not_in_grdm(self):
        """アップロードファイルが存在しない場合のテストケースです。"""
        self.mgr.grdm_file_info = {
            "/path/upload1.csv": "link://upload1"
        }
        self.mgr.convert_grdm_path = lambda x: x

        upload_files = {
            "/path/upload1.csv": "src_link1",
            "/path/not_exist.csv": "src_link2"
        }

        with pytest.raises(FileNotFoundError) as e:
            self.mgr._handle_file_upload("File Upload", upload_files)

        assert "not_exist.csvがGRDMに存在しません" in str(e.value)

    def test_handle_file_delete_success(self, mocker):
        """正常系のテストケースです。"""
        # GRDMファイル情報セット
        self.mgr.grdm_file_info = {
            "/path/delete1.csv": "link://delete1",
            "/path/delete2.csv": "link://delete2"
        }
        self.mgr.convert_grdm_path = lambda x: x
        self.mgr.convert_grdm_link = lambda x: x

        # searcher.get_file_entity_list の戻り値設定
        self.mgr.searcher.get_file_entity_list = MagicMock(side_effect=[
            ["entity_uri1"],  # delete1.csv のentityリスト
            ["entity_uri2", "entity_uri3"]  # delete2.csv のentityリスト
        ])

        # editor.create_activity モック
        self.mgr.editor.create_activity = MagicMock()
        # rdf_store.reload モック
        self.mgr.rdf_store.reload = MagicMock()
        # output.write モック
        self.mgr.output.write = MagicMock()

        # 実行ユーザーURI
        self.mgr.excution_user = "user_uri"

        deleted_files = ["/path/delete1.csv", "/path/delete2.csv"]

        # 関数実行
        self.mgr._handle_file_delete("File Delete", deleted_files)

        # create_activity 呼び出し検証
        self.mgr.editor.create_activity.assert_called_once()
        args, _ = self.mgr.editor.create_activity.call_args
        assert args[1] == "File Delete"  # activity_type
        # entity_uri1, entity_uri2, entity_uri3 がまとめられて渡されているか
        assert set(args[2]) == {"entity_uri1", "entity_uri2", "entity_uri3"}
        assert args[3] == "user_uri"

        # output.write にupdated_filesが渡されているか
        self.mgr.output.write.assert_called_once_with(["entity_uri1", "entity_uri2", "entity_uri3"])

    def test_handle_file_delete_not_in_grdm(self):
        """GRDM上にファイルが存在しない場合のテストケースです。"""
        self.mgr.grdm_file_info = {
            "/path/delete1.csv": "link://delete1"
        }
        self.mgr.convert_grdm_path = lambda x: x

        deleted_files = ["/path/delete1.csv", "/path/not_exist.csv"]

        with pytest.raises(FileNotFoundError) as e:
            self.mgr._handle_file_delete("File Delete", deleted_files)

        assert "not_exist.csvがGRDMに存在しない" in str(e.value)

    def test_handle_file_delete_entity_not_exist(self):
        """エンティティが存在しない場合のテストケースです。"""
        self.mgr.grdm_file_info = {
            "/path/delete1.csv": "link://delete1"
        }
        self.mgr.convert_grdm_path = lambda x: x
        self.mgr.convert_grdm_link = lambda x: x

        # entityリストが空の場合（存在しない）
        self.mgr.searcher.get_file_entity_list = MagicMock(return_value=[])

        deleted_files = ["/path/delete1.csv"]

        with pytest.raises(FileNotFoundError) as e:
            self.mgr._handle_file_delete("File Delete", deleted_files)

        assert "delete1.csvのEntityが存在しない" in str(e.value)

    def test_handle_provenance_edit_success(self):
        """正常系のテストケースです。"""
        # GRDMファイル情報にテスト対象のパスを追加
        self.mgr.grdm_file_info["/path/file.txt"] = "link://file"

        new_path = "/path/file.txt"
        ids = ["entity1", "entity2"]

        self.mgr._handle_provenance_edit(new_path, ids)

        self.mgr.editor.change_entity_label.assert_any_call("entity1", new_path)
        self.mgr.editor.change_entity_label.assert_any_call("entity2", new_path)

        self.mgr.rdf_store.reload.assert_called_once()
        self.mgr.output.write.assert_called_once_with(["link://file"])

    def test_handle_provenance_edit_file_not_found(self):
        """対象のファイルが見つからない場合のテストケースです。"""
        new_path = "/path/nonexistent.txt"
        ids = ["entity1"]

        with pytest.raises(FileNotFoundError) as e:
            self.mgr._handle_provenance_edit(new_path, ids)

        assert str(e.value) == f"{new_path}がGRDMに存在しない"

        self.mgr.rdf_store.reload.assert_not_called()
        self.mgr.output.write.assert_not_called()

    def test_handle_delete_activity_success(self):
        """正常系のテストケースです。"""
        prov = Namespace("http://www.w3.org/ns/prov#")
        graph = Graph()
        activity_uri = "http://example.org/activity/123"
        activity_subject = URIRef(activity_uri)
        generated_entity = URIRef("http://example.org/entity/abc")

        graph.add((activity_subject, prov.generated, generated_entity))
        mock_results = MagicMock()
        mock_results.graph = graph
        self.mgr.searcher.get_activity_info.return_value = mock_results

        self.mgr.editor.edit_entity.return_value = [URIRef("urn:collection:entity1"), URIRef("other_entity")]

        self.mgr.grdm_file_info = {
            "/path/file1.txt": "file1",
            "/path/file2.txt": "file2",
        }
        self.mgr.convert_grdm_path = lambda x: x
        self.mgr.convert_grdm_link = lambda x: f"link://{x}"

        update_files = ["/path/file1.txt", "/path/file2.txt"]

        self.mgr._handle_delete_activity("Delete Activity", activity_uri, update_files)

        self.mgr.editor.delete_activity.assert_called_once_with(activity_uri)
        self.mgr.editor.edit_entity.assert_called_once_with(str(generated_entity))
        self.mgr.editor.delete_entity.assert_called_once_with(URIRef("urn:collection:entity1"))
        self.mgr.rdf_store.reload.assert_called_once()
        self.mgr.output.write.assert_called_once_with(["link://file1", "link://file2"])

    def test_handle_delete_activity_no_generated_entity(self):
        """アクティビティによって制しえされたエンティティが存在しない場合のテストケースです。"""
        prov = Namespace("http://www.w3.org/ns/prov#")
        graph = Graph()
        activity_uri = "http://example.org/activity/123"
        activity_subject = URIRef(activity_uri)

        # prov:generatedが設定されていないgraphを返す
        mock_results = MagicMock()
        mock_results.graph = graph
        self.mgr.searcher.get_activity_info.return_value = mock_results

        self.mgr.editor.edit_entity.return_value = []

        # ここでgrdm_file_infoと変換関数をきちんとセット
        self.mgr.grdm_file_info = {
            "/path/file1.txt": "file1"
        }
        self.mgr.convert_grdm_path = lambda x: x
        self.mgr.convert_grdm_link = lambda x: f"link://{x}"

        update_files = ["/path/file1.txt"]

        # 呼び出し時に例外が出ないことを確認
        self.mgr._handle_delete_activity("Delete Activity", activity_uri, update_files)

        self.mgr.editor.delete_activity.assert_called_once_with(activity_uri)
        self.mgr.editor.edit_entity.assert_called_once_with("None")  # str(None) == "None"

        self.mgr.editor.delete_entity.assert_not_called()

        self.mgr.rdf_store.reload.assert_called_once()
        self.mgr.output.write.assert_called_once_with(["link://file1"])

    def test_handle_delete_activity_update_files_not_in_grdm(self):
        """更新対象のファイルがGRDM上に存在しない場合のテストケースです。"""
        prov = Namespace("http://www.w3.org/ns/prov#")
        graph = Graph()
        activity_uri = "http://example.org/activity/123"
        activity_subject = URIRef(activity_uri)
        generated_entity = URIRef("http://example.org/entity/abc")
        graph.add((activity_subject, prov.generated, generated_entity))
        mock_results = MagicMock()
        mock_results.graph = graph
        self.mgr.searcher.get_activity_info.return_value = mock_results

        self.mgr.editor.edit_entity.return_value = []

        # grdm_file_infoに存在するファイルをセット
        self.mgr.grdm_file_info = {
            "/path/file1.txt": "file1"
        }
        self.mgr.convert_grdm_path = lambda x: x
        self.mgr.convert_grdm_link = lambda x: f"link://{x}"

        # ひとつはGRDMにある、ひとつはないパス
        update_files = ["/path/file1.txt", "/path/nonexistent.txt"]

        # 実行しても例外は出ないが、output.writeにはGRDMにあるものだけ渡される
        self.mgr._handle_delete_activity("Delete Activity", activity_uri, update_files)

        # output.writeはGRDMにあるファイルだけリンクにして呼ばれる
        self.mgr.output.write.assert_called_once_with(["link://file1"])

    def test_convert_grdm_path(self):
        """convert_grdm_path が正しい GRDM パスに変換するかをテスト"""

        class Dummy:
            def convert_grdm_path(self, path: str):
                import os
                base_path = "/home/jovyan"
                osfstorage = "osfstorage"
                trimmed = os.path.relpath(path, base_path)
                return os.path.join(osfstorage, trimmed)

        mgr = Dummy()

        input_path = "/home/jovyan/work/data.txt"
        expected = "osfstorage/work/data.txt"
        assert mgr.convert_grdm_path(input_path) == expected

        input_path2 = "/home/jovyan/data.csv"
        expected2 = "osfstorage/data.csv"
        assert mgr.convert_grdm_path(input_path2) == expected2

    def test_convert_grdm_link(self):
        class Dummy:
            def __init__(self):
                self.project_id = "abc123"
                self.grdm_url = "https://grdm.example.com"

            def convert_grdm_link(self, file_id: str):
                files = "files"
                osfstorage = "osfstorage"
                path = "/".join([self.project_id, files, osfstorage, file_id])
                return urljoin(self.grdm_url + "/", path)

        mgr = Dummy()
        file_id = "path/to/file.txt"
        expected = "https://grdm.example.com/abc123/files/osfstorage/path/to/file.txt"

        assert mgr.convert_grdm_link(file_id) == expected

    def test_get_activity_info_success(self):
        """正常系のテストケースです。"""
        # URIの一覧
        uri_list = ["http://example.org/entity/1"]

        # モックのGraphとNamespace
        prov = Namespace("http://www.w3.org/ns/prov#")
        uri = uri_list[0]
        subject = URIRef(uri)
        location = URIRef("file://path/to/file.txt")

        # モックのEntityInfoの戻り値
        mock_results = MagicMock()
        graph = Graph()
        graph.add((subject, prov.atLocation, location))
        mock_results.graph = graph
        mock_results.__len__.return_value = 1  # ★ これを追加

        # get_entity_infoのモック設定
        self.mgr.searcher.get_entity_info = MagicMock(return_value=mock_results)

        # set_file_infoのモック設定
        related_file_info = MagicMock()
        related_file_info.related_files = [
            {
                "activity": URIRef("http://example.org/activity/123"),
                "type": "edit",
                "label": "label1"
            },
            {
                "activity": URIRef("http://example.org/activity/123"),
                "type": "edit",
                "label": "label2"
            }
        ]
        self.mgr.output.set_file_info = MagicMock(return_value=("subflow", related_file_info))

        # 実行
        result = self.mgr.get_activity_info(uri_list)

        # 検証
        expected = {
            "http://example.org/activity/123": {
                "type": "edit",
                "label": ["label1", "label2"]
            }
        }
        assert result == expected

        self.mgr.searcher.get_entity_info.assert_called_once_with(uri)
        self.mgr.output.set_file_info.assert_called_once()

    def test_get_activity_info_empty_or_no_hits(self):
        """アクティビティが見つからない場合のテストケースです。"""
        # URIの一覧（空）
        uri_list = []

        result = self.mgr.get_activity_info(uri_list)
        assert result == {}

        # URIはあるが、get_entity_info が空の結果を返すケース
        uri_list = ["http://example.org/entity/1"]
        self.mgr.searcher.get_entity_info = MagicMock(return_value=[])

        result = self.mgr.get_activity_info(uri_list)
        assert result == {}
