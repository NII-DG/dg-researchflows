"""outputクラスのテストを行うモジュールです。"""

from pathlib import Path
import re
import pytest
from unittest import mock

from rdflib import Graph, Literal, Namespace, URIRef
from data_governance.library.utils.config import path_config
from data_governance.library.utils.research_flow_provenance.output import FileInfo, OutputProvenance

class TestFileInfo:
    """FileInfoクラスのテストクラスです。"""
    def test_fileinfo_initialization(self):
        """初期化テストケースです。"""
        related_files = [
            {"type": "コピー元", "label": "fileA.csv", "location": "path/to/fileA.csv"},
            {"type": "参照元", "label": "fileB.csv", "location": "削除済み"}
        ]

        fi = FileInfo(
            file_name="test.csv",
            file_path="path/to/test.csv",
            link="http://example.com/test.csv",
            related_files=related_files
        )

        assert fi.file_name == "test.csv"
        assert fi.file_path == "path/to/test.csv"
        assert fi.link == "http://example.com/test.csv"
        assert isinstance(fi.related_files, list)
        assert len(fi.related_files) == 2
        assert fi.related_files[0]["type"] == "コピー元"
        assert fi.related_files[1]["location"] == "削除済み"


class TestOutputProvenance:
    """OutputProvenanceクラスのテストクラスです。"""
    def test_write_appends_new_section(self, tmp_readme_path, test_instance, patch_path_config):
        """README.mdファイルが既に存在する場合のテストケースです。"""
        test_instance.write(["dummy_file.csv"])

        result_text = tmp_readme_path.read_text(encoding="utf-8")

        assert "testfileC.csv" in result_text
        assert "https://rcos.rdm.nii.ac.jp/kcbue/files/osfstorage/68ae9cff000000000000c999" in result_text
        assert "コピー元：[osfstorage/data/experiment/jikkenn1/Test Folder/testfileC.csv]" in result_text
        assert "testfileA.csv" in result_text
        assert "testfileB.csv" in result_text

    def test_write_creates_readme_from_template(self, tmp_path, test_instance, monkeypatch):
        """README.mdが既に存在しない場合のテストケースです。"""
        readme_dir = tmp_path / "writing" / "ronnbunn"
        readme_dir.mkdir(parents=True)
        readme_path = readme_dir / "README.md"

        # テンプレートの絶対パスをセット
        template_path = (Path(__file__).parent.parent.parent  / "test_data" / "provenance" / "base_readme.md").resolve()
        test_instance.TEMPLATE_README = str(template_path)

        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.setattr(path_config, "DATA", "")

        test_instance.write(["dummy_file.csv"])

        content = readme_path.read_text(encoding="utf-8")
        assert "来歴情報確認用README" in content
        assert "testfileC.csv" in content

    def test_write_with_existing_same_file_section(self, tmp_readme_path, test_instance, monkeypatch):
        """README.mdに既に同名のセクションが存在する場合のテストケースです。"""
        # 既存のREADMEにdummy_file.csvのセクションを追加
        readme_text = tmp_readme_path.read_text(encoding="utf-8")
        existing_section = (
            "## [dummy_file.csv（osfstorage/data/writing/ronnbunn/argument_data/Test Folder/dummy_file.csv)]"
            "(https://rcos.rdm.nii.ac.jp/kcbue/files/osfstorage/68ae9cff000000000000c999)"
        )
        readme_text += "\n\n" + existing_section
        tmp_readme_path.write_text(readme_text, encoding="utf-8")

        # テンプレートファイルのパスセット
        template_path = (Path(__file__).parent.parent.parent.parent / "test_data" / "provenance" / "base_readme.md").resolve()
        test_instance.TEMPLATE_README = str(template_path)

        # monkeypatchセット
        monkeypatch.setattr(path_config, "DATA", "")
        monkeypatch.setenv("HOME", str(tmp_readme_path.parent.parent.parent))

        # ファイル更新
        test_instance.write(["dummy_file.csv"])

        updated_text = tmp_readme_path.read_text(encoding="utf-8")

        assert updated_text.count("osfstorage/data/writing/ronnbunn/argument_data/Test Folder/dummy_file.csv") == 1

    def test_set_file_info_returns_expected_data(self, mock_searcher, mock_results_graph):
        """正常系のテストケースです。"""
        # Arrange
        instance = OutputProvenance(searcher=mock_searcher)
        mock_results = mock.MagicMock()
        mock_results.graph = mock_results_graph
        file_path = "/some/path/file1.txt"

        # Act
        subflow_name, file_info = instance.set_file_info(mock_results, file_path)

        # Assert
        assert subflow_name == "subflow/sample"
        assert isinstance(file_info, FileInfo)
        assert file_info.file_name == "file1.txt"
        assert file_info.file_path == "root/project/subflow/sample/file1.txt"
        assert file_info.link == file_path
        assert len(file_info.related_files) >= 1
        assert "type" in file_info.related_files[0]
        assert "label" in file_info.related_files[0]
        assert "location" in file_info.related_files[0]

    def test_set_file_info_with_delete_activity(self, mock_searcher):
        """削除済みのエンティティが存在するケース。"""
        prov = Namespace("http://www.w3.org/ns/prov#")
        rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")

        entity_uri = URIRef("http://example.org/entity_with_delete")
        activity_uri = URIRef("http://example.org/deleteActivity123")

        # entity_graph (get_entity_infoで返すもの)
        entity_graph = Graph()
        entity_graph.add((entity_uri, rdfs.label, Literal("file_deleted.txt")))
        entity_graph.add((entity_uri, prov.wasUsedBy, activity_uri))

        mock_result = mock.MagicMock()
        mock_result.graph = entity_graph
        mock_searcher.get_entity_info.return_value = mock_result

        # results.graph (set_file_infoに渡す)
        results_graph = Graph()
        subject = URIRef("http://example.org/subject")

        # ここでwasGeneratedByとwasDerivedFrom両方セット
        results_graph.add((subject, rdfs.label, Literal("root/project/subflow/sample/file1.txt")))
        results_graph.add((subject, prov.wasGeneratedBy, activity_uri))
        results_graph.add((subject, prov.wasDerivedFrom, entity_uri))


        results = mock.MagicMock()
        results.graph = results_graph

        instance = OutputProvenance(searcher=mock_searcher)
        subflow_name, file_info = instance.set_file_info(results, "some_file.txt")

        print(f"{file_info}を出力")
        assert any(f.get("location") == "削除済み" for f in file_info.related_files if f)

    def test_set_file_info_multiple_entries(self, mock_searcher):
        """複数のエンティティが存在するテストケース。"""
        prov = Namespace("http://www.w3.org/ns/prov#")
        rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")

        # メインgraph（results.graph）を構築
        graph = Graph()
        subject1 = URIRef("http://example.org/subject1")
        subject2 = URIRef("http://example.org/subject2")
        activity1 = URIRef("http://example.org/copyActivity123")
        activity2 = URIRef("http://example.org/modifyActivity456")
        entity1 = URIRef("http://example.org/entity1")
        entity2 = URIRef("http://example.org/entity2")

        graph.add((subject1, rdfs.label, Literal("root/project/subflow/sample/file1.txt")))
        graph.add((subject1, prov.wasGeneratedBy, activity1))
        graph.add((subject1, prov.wasDerivedFrom, entity1))

        graph.add((subject2, prov.wasGeneratedBy, activity2))
        graph.add((subject2, prov.wasRevisionOf, entity2))

        # メインファイルのラベルだけ subject1 に追加
        graph.add((subject2, rdfs.label, Literal("file2.txt")))

        # mock_searcher.get_entity_info に返させるモックグラフを構築
        def mock_get_entity_info(uri):
            entity_graph = Graph()
            entity_graph.add((uri, rdfs.label, Literal(f"label_for_{uri.split('/')[-1]}")))
            entity_graph.add((uri, prov.wasUsedBy, URIRef("http://example.org/usedByActivity123")))
            mock_entity_result = mock.MagicMock()
            mock_entity_result.graph = entity_graph
            return mock_entity_result

        mock_searcher.get_entity_info.side_effect = mock_get_entity_info

        # OutputProvenance の実行
        results = mock.MagicMock()
        results.graph = graph
        instance = OutputProvenance(searcher=mock_searcher)

        subflow_name, file_info = instance.set_file_info(results, "some_file.txt")

        # アサーション（検証）
        assert file_info.file_name == "file1.txt"
        assert file_info.file_path == "root/project/subflow/sample/file1.txt"
        assert file_info.link == "some_file.txt"
        assert len(file_info.related_files) >= 2  # 少なくとも2件の関連ファイルがあること

        related_types = [f.get("type") for f in file_info.related_files if f]
        assert "コピー元" in related_types
        assert "編集元" in related_types

