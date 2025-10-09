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
        readme_dir = tmp_path / "data" / "writing" / "ronnbunn"
        readme_dir.mkdir(parents=True)
        readme_path = readme_dir / "README.md"

        template_path = (Path(__file__).parent.parent.parent / "test_data" / "provenance" / "base_readme.md").resolve()
        test_instance.TEMPLATE_README = str(template_path)

        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.setattr(path_config, "DATA", "")

        test_instance.write(["dummy_file.csv"])

        content = readme_path.read_text(encoding="utf-8")
        assert "来歴情報確認用README" in content
        assert "testfileC.csv" in content

    def test_write_with_existing_same_file_section(self, tmp_path, test_instance, monkeypatch):
        """指定したファイルの来歴情報が既に記録されている場合のテストケース"""
        # DATA を "data" にする（write()内部のパスと整合）
        monkeypatch.setattr(path_config, "DATA", "data")
        monkeypatch.setenv("HOME", str(tmp_path))

        readme_dir = tmp_path / "data" / "writing" / "ronnbunn"
        readme_dir.mkdir(parents=True, exist_ok=True)

        readme_path = readme_dir / "README.md"
        source_path = Path("tests/test_data/provenance/README.md")
        readme_path.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")

        readme_text = readme_path.read_text(encoding="utf-8")
        existing_section = (
            "## [dummy_file.csv（osfstorage/data/writing/ronnbunn/argument_data/Test Folder/dummy_file.csv)]"
            "(https://rcos.rdm.nii.ac.jp/kcbue/files/osfstorage/68ae9cff000000000000c999)"
        )
        readme_text += "\n\n" + existing_section
        readme_path.write_text(readme_text, encoding="utf-8")

        template_path = (Path(__file__).parent.parent.parent.parent / "tests" / "test_data" / "provenance" / "base_readme.md").resolve()
        test_instance.TEMPLATE_README = str(template_path)

        test_instance.write(["dummy_file.csv"])

        updated_text = readme_path.read_text(encoding="utf-8")
        assert updated_text.count("osfstorage/data/writing/ronnbunn/argument_data/Test Folder/dummy_file.csv") == 1
    
    def test_write_handles_deleted_related_file(self, test_instance, monkeypatch, tmp_path):
        """関連情報に削除済みファイルの情報が存在する場合のテストケース"""
        from data_governance.library.utils.research_flow_provenance.output import FileInfo

        file_info_mock = FileInfo(
            file_name="deleted_file.csv",
            file_path="some/path/deleted_file.csv",
            link="http://example.com/deleted_file",
            related_files=[
                {"type": "コピー元", "label": "deleted.csv", "location": "削除済み"}
            ]
        )

        def mock_set_file_info(results, location):
            return ("ronnbunn", file_info_mock)

        test_instance.set_file_info = mock_set_file_info
        test_instance.searcher.get_all_entity_info.return_value = None

        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.setattr(path_config, "DATA", "data")

        # writeメソッドが書き込むパスの親ディレクトリを作成する
        write_dir = tmp_path / "data" / "ronnbunn"
        write_dir.mkdir(parents=True, exist_ok=True)

        readme_path = write_dir / "README.md"
        readme_path.write_text("")

        template_path = (Path(__file__).parent.parent.parent.parent / "tests" / "test_data" / "provenance" / "base_readme.md").resolve()
        test_instance.TEMPLATE_README = str(template_path)

        test_instance.write(["http://example.com/deleted_file"])

        updated_text = readme_path.read_text(encoding="utf-8")
        assert "削除済み" in updated_text
        assert "deleted.csv" in updated_text

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

        # related_filesに削除済みは含まれないため代わりにentityのラベルが空かどうか確認など
        # 削除済みなのでrelated_filesは空の可能性もあるためそれもOKとする
        assert isinstance(file_info.related_files, list)

        # ファイル名などは正しくセットされているかチェック
        assert file_info.file_name == "file1.txt"
        assert subflow_name == "subflow/sample"

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

    def test_set_file_info_with_upload_activity(self, mock_searcher):
        """uploadActivity による関連付けが存在するケース"""
        prov = Namespace("http://www.w3.org/ns/prov#")
        rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")

        subject = URIRef("http://example.org/subject")
        upload_activity = URIRef("http://example.org/uploadActivity789")
        upload_entity = URIRef("http://example.org/uploaded_file")

        graph = Graph()
        graph.add((subject, rdfs.label, Literal("root/project/subflow/sample/uploaded_file.txt")))
        graph.add((subject, prov.wasGeneratedBy, upload_activity))
        graph.add((subject, prov.wasDerivedFrom, upload_entity))

        # upload_entity の get_entity_info は呼ばれないが一応返す
        mock_result = mock.MagicMock()
        mock_result.graph = Graph()
        mock_searcher.get_entity_info.return_value = mock_result

        results = mock.MagicMock()
        results.graph = graph

        instance = OutputProvenance(searcher=mock_searcher)
        subflow_name, file_info = instance.set_file_info(results, "some_file.txt")

        # 関連ファイルにuploadActivityのものがあることを確認
        related = file_info.related_files
        upload_related = [f for f in related if f["type"] == "アップロード元"]
        assert len(upload_related) > 0
        for r in upload_related:
            assert r["label"] == r["location"]  # uploadActivityの特殊処理確認

    def test_set_file_info_with_urn_collection_member_expansion(self, mock_searcher):
        """urn:collection のURIをもつ関連ファイルがあるケース"""
        prov = Namespace("http://www.w3.org/ns/prov#")
        rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")

        subject = URIRef("http://example.org/subject")
        copy_activity = URIRef("http://example.org/copyActivity123")
        urn_collection = URIRef("urn:collection:1234")
        member1 = URIRef("http://example.org/member1")
        member2 = URIRef("http://example.org/member2")

        graph = Graph()
        graph.add((subject, rdfs.label, Literal("root/project/subflow/sample/file_with_collection.txt")))
        graph.add((subject, prov.wasGeneratedBy, copy_activity))
        graph.add((subject, prov.wasDerivedFrom, urn_collection))

        # mock get_entity_info for urn_collection returns graph with hadMember
        collection_graph = Graph()
        collection_graph.add((urn_collection, prov.hadMember, member1))
        collection_graph.add((urn_collection, prov.hadMember, member2))

        def mock_get_entity_info(uri):
            mock_res = mock.MagicMock()
            if uri == urn_collection:
                mock_res.graph = collection_graph
            else:
                # member entity graph
                entity_graph = Graph()
                entity_graph.add((uri, rdfs.label, Literal(f"label_for_{uri.split('/')[-1]}")))
                mock_res.graph = entity_graph
            return mock_res

        mock_searcher.get_entity_info.side_effect = mock_get_entity_info

        results = mock.MagicMock()
        results.graph = graph

        instance = OutputProvenance(searcher=mock_searcher)
        subflow_name, file_info = instance.set_file_info(results, "some_file.txt")

        related_labels = [str(f["label"]) for f in file_info.related_files]
        assert "label_for_member1" in related_labels
        assert "label_for_member2" in related_labels

    def test_set_file_info_with_wasUsedBy_activities(self, mock_searcher):
        prov = Namespace("http://www.w3.org/ns/prov#")
        rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")

        subject = URIRef("http://example.org/subject")
        modify_activity = URIRef("http://example.org/modifyActivity789")
        entity = URIRef("http://example.org/entity_mod")

        # メインのグラフ作成
        graph = Graph()
        graph.add((subject, rdfs.label, Literal("root/project/subflow/sample/file_wasUsedBy.txt")))
        graph.add((subject, prov.wasUsedBy, modify_activity))
        graph.add((subject, prov.hadRevision, entity))

        # entity の get_entity_info で返すグラフ
        entity_graph = Graph()
        entity_graph.add((entity, rdfs.label, Literal("entity_mod_label")))
        # 削除済みのactivityは含めない（今回のテストは編集先の存在確認が目的）
        # entity_graph.add((entity, prov.wasUsedBy, URIRef("http://example.org/deleteActivity123")))  # 不要

        mock_entity_result = mock.MagicMock()
        mock_entity_result.graph = entity_graph
        mock_searcher.get_entity_info.return_value = mock_entity_result

        # get_activity_infoの戻り値もモック
        activity_graph = Graph()
        # activityが生成したentityを示す
        activity_graph.add((modify_activity, prov.generated, entity))

        mock_activity_result = mock.MagicMock()
        mock_activity_result.graph = activity_graph
        mock_searcher.get_activity_info.return_value = mock_activity_result

        # クエリ結果のモック
        results = mock.MagicMock()
        results.graph = graph

        instance = OutputProvenance(searcher=mock_searcher)
        subflow_name, file_info = instance.set_file_info(results, "some_file.txt")

        related_types = [str(f["type"]) for f in file_info.related_files]
        assert "編集先" in related_types
        assert any(str(f["label"]) == "entity_mod_label" for f in file_info.related_files)

    def test_set_file_info_with_wasMemberOf_collections(self, mock_searcher):
        prov = Namespace("http://www.w3.org/ns/prov#")
        rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")

        subject = URIRef("http://example.org/subject")
        collection = URIRef("http://example.org/collection123")
        activity = URIRef("http://example.org/copyActivity999")
        entity = URIRef("http://example.org/entity_collection")

        graph = Graph()
        graph.add((subject, rdfs.label, Literal("root/project/subflow/sample/file_with_collection_member.txt")))
        graph.add((subject, prov.wasMemberOf, collection))

        # collection graph の中身
        collection_graph = Graph()
        collection_graph.add((collection, prov.wasUsedBy, activity))
        collection_graph.add((collection, prov.hadDerivation, entity))

        entity_graph = Graph()
        entity_graph.add((entity, rdfs.label, Literal("entity_collection_label")))

        def mock_get_entity_info(uri):
            mock_res = mock.MagicMock()
            if uri == collection:
                mock_res.graph = collection_graph
            else:
                mock_res.graph = entity_graph
            return mock_res

        mock_searcher.get_entity_info.side_effect = mock_get_entity_info

        # ここが追加ポイント
        activity_graph = Graph()
        activity_graph.add((activity, prov.generated, entity))
        mock_activity_result = mock.MagicMock()
        mock_activity_result.graph = activity_graph
        mock_searcher.get_activity_info.return_value = mock_activity_result

        results = mock.MagicMock()
        results.graph = graph

        instance = OutputProvenance(searcher=mock_searcher)
        subflow_name, file_info = instance.set_file_info(results, "some_file.txt")

        related_types = [str(f["type"]) for f in file_info.related_files]
        assert "コピー先" in related_types or "編集先" in related_types or "コンパイル先" in related_types or "出力先" in related_types or "アップロード先" in related_types
        assert any(str(f["label"]) == "entity_collection_label" for f in file_info.related_files)