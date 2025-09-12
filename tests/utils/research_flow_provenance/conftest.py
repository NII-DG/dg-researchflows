"""fixtureを記述するモジュールです。"""
from pathlib import Path
import pytest
import os
from unittest.mock import MagicMock
import shutil
import tempfile
import types

from rdflib import Graph, Literal, Namespace, URIRef

from data_governance.library.utils.research_flow_provenance.output import OutputProvenance
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
    readme_dir = tmp_path / "writing" / "ronnbunn"
    readme_dir.mkdir(parents=True)

    readme_path = readme_dir / "README.md"
    source_path = Path("tests/test_data/provenance/README.md")

    # ファイルの中身をコピー（重要）
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
def test_instance(dummy_file_info):
    """
    OutputProvenanceのインスタンスを返すfixture。
    検索と情報設定部分をモック。
    """
    from data_governance.library.utils.research_flow_provenance.output import OutputProvenance

    mock_searcher = MagicMock()
    mock_searcher.get_all_entity_info.return_value = "dummy_entity"

    instance = OutputProvenance(mock_searcher)

    # set_file_info をモックしてサブフロー名とinfoを返す
    instance.set_file_info = MagicMock(return_value=("writing/ronnbunn", dummy_file_info))

    # テンプレートは使われないので、何をセットしてもよい（念のためセット）
    instance.TEMPLATE_README = "not_used"

    return instance

@pytest.fixture
def patch_path_config(monkeypatch, tmp_path):
    # tmp_path: /tmp/pytest-...
    monkeypatch.setattr(path_config, "DATA", "")  # base_path = /tmp/pytest-...
    monkeypatch.setenv("HOME", str(tmp_path))     # /home/fakeuser → /tmp/pytest-...

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
