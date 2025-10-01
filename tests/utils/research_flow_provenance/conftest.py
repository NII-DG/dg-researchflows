"""fixtureを記述するモジュールです。"""
from pathlib import Path
import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch
import shutil
import tempfile
import types

from rdflib import Graph, Literal, Namespace, URIRef

from data_governance.library.utils.research_flow_provenance.prov import ProvenanceManager
from data_governance.library.utils.config import path_config

@pytest.fixture
def test_jsonld_files():

    data_dir = "tests/test_data/provenance"
    return {
        "vocab": os.path.join(data_dir, "vocab.jsonld"),
        "entity": os.path.join(data_dir, "entity.jsonld"),
        "activity": os.path.join(data_dir, "activity.jsonld"),
        "agent": os.path.join(data_dir, "agent.jsonld")
    }

@pytest.fixture
def tmp_readme_path(tmp_path):
    # path_config.DATA の値に応じてディレクトリを作る
    data_folder = getattr(path_config, "DATA", "data")  # デフォルトは "data"

    readme_dir = tmp_path / data_folder / "writing" / "ronnbunn"
    readme_dir.mkdir(parents=True, exist_ok=True)

    readme_path = readme_dir / "README.md"
    source_path = Path("tests/test_data/provenance/README.md")

    # README.md の中身をコピー
    readme_path.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")

    return readme_path

@pytest.fixture
def dummy_file_info():
    """ダミーのファイル情報を返すモック"""
    file_info = MagicMock()
    file_info.file_name = "testfileC.csv"
    file_info.file_path = "osfstorage/data/writing/ronnbunn/argument_data/Test Folder/testfileC.csv"
    file_info.link = "https://rcos.rdm.nii.ac.jp/kcbue/files/osfstorage/68ae9cff000000000000c999"
    file_info.related_files = [
        {
            "type": "コピー元",
            "label": "osfstorage/data/experiment/jikkenn1/Test Folder/testfileC.csv",
            "location": "https://rcos.rdm.nii.ac.jp/kcbue/files/osfstorage/68ae9cff000000000000c991"
        }
    ]
    return file_info

@pytest.fixture
def test_instance(dummy_file_info, tmp_path):
    """
    OutputProvenanceのインスタンスを返すfixture。
    検索と情報設定部分をモック。
    """
    from data_governance.library.utils.research_flow_provenance.output import OutputProvenance

    mock_searcher = MagicMock()
    mock_searcher.get_all_entity_info.return_value = "dummy_entity"

    instance = OutputProvenance(mock_searcher)

    instance.set_file_info = MagicMock(return_value=("writing/ronnbunn", dummy_file_info))

    # 存在するテンプレートファイルを用意
    template_file = tmp_path / "base_readme.md"
    template_file.write_text("# 来歴情報確認用README\n\n## サブフロー：", encoding="utf-8")

    instance.TEMPLATE_README = str(template_file)

    return instance

@pytest.fixture
def patch_path_config(monkeypatch, tmp_path):
    monkeypatch.setattr(path_config, "DATA", "")
    monkeypatch.setenv("HOME", str(tmp_path))
    return tmp_path

prov = Namespace("http://www.w3.org/ns/prov#")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")

@pytest.fixture
def mock_searcher():
    mock = MagicMock()

    # モックされた searcher.get_entity_info が返す graph を作成
    mock_graph = Graph()
    test_entity_uri = URIRef("http://example.org/entity1")

    # rdfs:label は必須
    mock_graph.add((test_entity_uri, rdfs.label, Literal("related_file.txt")))

    # prov:atLocation も追加
    mock_graph.add((test_entity_uri, prov.atLocation, Literal("/some/related/path")))

    # ここがポイント！必ず wasUsedBy のトリプルを入れる
    # 例として適当なURIを指定（deleteActivity を含まない）
    activity_uri = URIRef("http://example.org/someActivity")
    mock_graph.add((test_entity_uri, prov.wasUsedBy, activity_uri))

    mock_result = MagicMock()
    mock_result.graph = mock_graph
    mock.get_entity_info.return_value = mock_result

    return mock

@pytest.fixture
def mock_results_graph():
    graph = Graph()

    file_uri = URIRef("http://example.org/file1")
    activity_uri = URIRef("http://example.org/modifyActivity123")

    # メインファイルのラベル（ファイルパス的な扱い）
    graph.add((file_uri, rdfs.label, Literal("root/project/subflow/sample/file1.txt")))

    # 編集元情報
    graph.add((file_uri, prov.wasGeneratedBy, activity_uri))
    graph.add((file_uri, prov.wasUsedBy, activity_uri))
    graph.add((file_uri, prov.wasRevisionOf, URIRef("http://example.org/entity1")))
    graph.add((file_uri, prov.hadRevision, URIRef("http://example.org/entity1")))

    return graph

@pytest.fixture
def manager():
    with patch("data_governance.library.utils.research_flow_provenance.prov.RDFStore") as mock_rdfstore_class, \
        patch("data_governance.library.utils.research_flow_provenance.prov.ProvenanceSearcher") as mock_searcher_class, \
        patch("data_governance.library.utils.research_flow_provenance.prov.OutputProvenance") as mock_output_class, \
        patch("data_governance.library.utils.research_flow_provenance.prov.ProvenanceEditor") as mock_editor_class, \
        patch("data_governance.library.utils.research_flow_provenance.prov.External") as mock_external_class, \
        patch.object(ProvenanceManager, "_get_execution_user"):  # ← ここで __init__ 内の呼び出しを止める

        # インスタンスを返すためのモック設定
        mock_rdfstore = MagicMock()
        mock_searcher = MagicMock()
        mock_output = MagicMock()
        mock_editor = MagicMock()
        mock_external = MagicMock()

        mock_rdfstore_class.return_value = mock_rdfstore
        mock_searcher_class.return_value = mock_searcher
        mock_output_class.return_value = mock_output
        mock_editor_class.return_value = mock_editor
        mock_external_class.return_value = mock_external

        mgr = ProvenanceManager(token="test_token", grdm_url="http://test.url", project_id="project123")
        # 属性を明示的に設定（__init__ による呼び出しが止まっているので）
        mgr.searcher = mock_searcher
        mgr.editor = mock_editor
        mgr.external = mock_external
        mgr.AGENT_BASE = "urn:agent:"

        return mgr, mock_searcher, mock_editor, mock_external

@pytest.fixture
def async_manager():
    with patch("data_governance.library.utils.research_flow_provenance.prov.RDFStore"), \
        patch("data_governance.library.utils.research_flow_provenance.prov.ProvenanceSearcher"), \
        patch("data_governance.library.utils.research_flow_provenance.prov.OutputProvenance"), \
        patch("data_governance.library.utils.research_flow_provenance.prov.ProvenanceEditor"), \
        patch("data_governance.library.utils.research_flow_provenance.prov.External") as mock_external_class, \
        patch.object(ProvenanceManager, "_get_execution_user"):

        mock_external = mock_external_class.return_value
        mock_external.list_ = AsyncMock(return_value=[{"id": "file1"}, {"id": "file2"}])

        mgr = ProvenanceManager(token="test_token", grdm_url="http://test.url", project_id="project123")
        mgr.external = mock_external

        return mgr, mock_external

# @pytest.fixture
# def prov_manager():
#     with patch("data_governance.library.utils.research_flow_provenance.prov.RDFStore"), \
#         patch("data_governance.library.utils.research_flow_provenance.prov.ProvenanceSearcher"), \
#         patch("data_governance.library.utils.research_flow_provenance.prov.OutputProvenance"), \
#         patch("data_governance.library.utils.research_flow_provenance.prov.ProvenanceEditor"), \
#         patch("data_governance.library.utils.research_flow_provenance.prov.External"):

#         mgr = ProvenanceManager("token", "url", "project")

#         # 共通のモック設定
#         mgr.grdm_file_info = {
#             "/path/src1.py": "link://src1",
#             "/path/src2.py": "link://src2",
#             "/path/dst_file.out": "link://dst"
#         }
#         mgr.convert_grdm_path = lambda x: x
#         mgr.convert_grdm_link = lambda x: x
#         mgr.searcher.get_file_entity = MagicMock(return_value=None)
#         mgr.editor.create_entity = MagicMock(side_effect=["entity1", "entity2", "entity_dst"])
#         mgr.editor.create_activity = MagicMock()
#         mgr.editor.create_agent = MagicMock()
#         mgr.rdf_store.reload = MagicMock()
#         mgr.output.write = MagicMock()
#         mgr.excution_user = "user_uri"

#         yield mgr

    
