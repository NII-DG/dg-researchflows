"""rdf.pyをテストするためのファイルです。"""

import os
import pytest
from unittest import mock

from rdflib import Graph, URIRef
from data_governance.library.utils.research_flow_provenance.rdf import RDFStore, ProvenanceSearcher

class TestRdfStore:
    """RdfStoreクラスをテストするためのクラスです。"""
    def test_constructor_success(self):
        """__init__の正常実行テストケースです。"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict(os.environ, test_env):
            with mock.patch("os.path.exists", return_value=True):
                rdf_store = RDFStore()

                base_path = os.path.join(test_env["HOME"], "data_governance/researchflow")
                env_path = os.path.join(base_path, test_env["JUPYTERHUB_SERVER_NAME"])

                assert rdf_store.vocab_file == os.path.join(env_path, rdf_store.PROV_VOCAB)
                assert rdf_store.entity_file == os.path.join(env_path, rdf_store.PROV_ENTITY)
                assert rdf_store.activity_file == os.path.join(env_path, rdf_store.PROV_ACTIVITY)
                assert rdf_store.agent_file == os.path.join(env_path, rdf_store.PROV_AGENT)

    def test_constructor_vocab_missing(self):
        """vocab.jsonld が存在しない場合に VOCAB_JSONLD からコピーされるか"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }
        with mock.patch.dict(os.environ, test_env):
            with mock.patch("os.path.exists", side_effect=lambda path: False if "vocab" in path else True):
                with mock.patch("os.makedirs") as mock_makedirs:
                    with mock.patch("shutil.copy") as mock_copy:
                        rdf_store = RDFStore()
                        vocab_src = os.path.join(test_env["HOME"], rdf_store.VOCAB_JSONLD)
                        mock_copy.assert_called_once_with(vocab_src, rdf_store.vocab_file)
                        mock_makedirs.assert_called_with(os.path.dirname(rdf_store.vocab_file), exist_ok=True)

    def test_constructor_entity_missing(self):
        """entity.jsonld が存在しない場合に TEMPLATE_JSONLD からコピーされるか"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }
        with mock.patch.dict(os.environ, test_env):
            with mock.patch("os.path.exists", side_effect=lambda path: False if "entity" in path else True):
                with mock.patch("os.makedirs") as mock_makedirs:
                    with mock.patch("shutil.copy") as mock_copy:
                        rdf_store = RDFStore()
                        template_src = os.path.join(test_env["HOME"], rdf_store.TEMPLATE_JSONLD)
                        mock_copy.assert_any_call(template_src, rdf_store.entity_file)
                        mock_makedirs.assert_any_call(os.path.dirname(rdf_store.entity_file), exist_ok=True)

    def test_constructor_activity_missing(self):
        """activity.jsonld が存在しない場合に TEMPLATE_JSONLD からコピーされるか"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }
        with mock.patch.dict(os.environ, test_env):
            with mock.patch("os.path.exists", side_effect=lambda path: False if "activity" in path else True):
                with mock.patch("os.makedirs") as mock_makedirs:
                    with mock.patch("shutil.copy") as mock_copy:
                        rdf_store = RDFStore()
                        template_src = os.path.join(test_env["HOME"], rdf_store.TEMPLATE_JSONLD)
                        mock_copy.assert_any_call(template_src, rdf_store.activity_file)
                        mock_makedirs.assert_any_call(os.path.dirname(rdf_store.activity_file), exist_ok=True)

    def test_constructor_agent_missing(self):
        """agent.jsonld が存在しない場合に TEMPLATE_JSONLD からコピーされるか"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }
        with mock.patch.dict(os.environ, test_env):
            with mock.patch("os.path.exists", side_effect=lambda path: False if "agent" in path else True):
                with mock.patch("os.makedirs") as mock_makedirs:
                    with mock.patch("shutil.copy") as mock_copy:
                        rdf_store = RDFStore()
                        template_src = os.path.join(test_env["HOME"], rdf_store.TEMPLATE_JSONLD)
                        mock_copy.assert_any_call(template_src, rdf_store.agent_file)
                        mock_makedirs.assert_any_call(os.path.dirname(rdf_store.agent_file), exist_ok=True)

    def test_query_success(self):
        """query関数の正常系テストケースです。"""
        store = RDFStore.__new__(RDFStore)

        mock_graph = mock.MagicMock()
        mock_graph.query.return_value = "mock result"

        store.graph = mock_graph

        query_string = "SELECT ?s WHERE { ?s ?p ?o }"
        result = store.query(query_string)

        mock_graph.query.assert_called_once_with(query_string)
        assert result == "mock result"

    def test_query_raises_exception(self):
        """query関数の異常系テストケース"""
        store = RDFStore.__new__(RDFStore)

        mock_graph = mock.MagicMock()
        mock_graph.query.side_effect = Exception("クエリエラー")
        store.graph = mock_graph

        with pytest.raises(Exception) as excinfo:
            store.query("SELECT ?s WHERE { ?s ?p ?o }")

        assert "クエリエラー" in str(excinfo.value)

    def test_load_graph_success(self, test_jsonld_files):
        """load_graphにて正常にグラフが読み込まれる場合のテストケースです。"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            # 一度だけ True を返す関数を作る
            with mock.patch("os.path.exists", return_value=True):
                store = RDFStore()

        # ここでファイルパスを差し替える
        store.vocab_file = test_jsonld_files["vocab"]
        store.entity_file = test_jsonld_files["entity"]
        store.activity_file = test_jsonld_files["activity"]
        store.agent_file = test_jsonld_files["agent"]

        # 実際に読み込み
        store.load_graph()

        # 検証
        assert isinstance(store.graph, Graph)
        assert len(store.graph) == 257

    def test_load_graph_file_read_fail(self, test_jsonld_files):
        """ファイルの読み込みに失敗する場合のテストケースです。"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                store = RDFStore()

        # ファイルパスをテスト用のファイルに差し替え
        store.vocab_file = test_jsonld_files["vocab"]
        store.entity_file = test_jsonld_files["entity"]
        store.activity_file = test_jsonld_files["activity"]
        store.agent_file = test_jsonld_files["agent"]

        # open は普通にモック
        m_open = mock.mock_open(read_data="invalid json")

        with mock.patch("builtins.open", m_open):
            # rdflibのgraph.parse → json読み込み時に例外を発生させる
            with mock.patch("rdflib.graph.Graph.parse", side_effect=Exception("読み込みエラー")):
                with pytest.raises(RuntimeError) as excinfo:
                    store.load_graph()

        assert "の読み込みに失敗しました" in str(excinfo.value)
        assert "読み込みエラー" in str(excinfo.value)

    def test_reload(self):
        """reload関数の正常実行テストケースです。"""
        store = RDFStore.__new__(RDFStore)

        with mock.patch.object(store, "load_graph") as mock_load_graph:
            store.reload()
            mock_load_graph.assert_called_once()

class TestProvenanceSearcher:
    """ProvenanceSearcherクラスのテストクラスです。"""

    def test_get_execution_user_success(self):
        """正常にエージェントが取得できる場合のテストケースです。"""
        mock_store = mock.Mock()
        mock_store.query.return_value = [{"agent": URIRef("urn:agent:test")}]

        searcher = ProvenanceSearcher(mock_store)
        result = searcher.get_excution_user("urn:agent:test")

        assert result == "urn:agent:test"

    def test_get_execution_user_not_found(self):
        """クエリ結果が空で、Noneが返るテストケースです。"""
        mock_store = mock.Mock()
        mock_store.query.return_value = []

        searcher = ProvenanceSearcher(mock_store)
        result = searcher.get_excution_user("urn:agent:unknown")

        assert result is None

    def test_get_execution_user_query_error(self):
        """クエリ実行で例外が発生する場合のテストケースです。"""
        mock_store = mock.Mock()
        mock_store.query.side_effect = Exception("クエリエラー")

        searcher = ProvenanceSearcher(mock_store)

        with pytest.raises(RuntimeError) as excinfo:
            searcher.get_excution_user("urn:agent:error")

        assert "RDFクエリの実行に失敗しました" in str(excinfo.value)

    def test_get_file_entity_success(self):
        """get_file_entityでエンティティが正しく取得できるテストケースです。"""
        mock_store = mock.Mock()
        mock_result = [ {"entity": "urn:entity:test-file"} ]
        mock_store.query.return_value = mock_result

        searcher = ProvenanceSearcher(rdf_store=mock_store)
        file_link = "http://example.com/file1.txt"

        result = searcher.get_file_entity(file_link)

        assert result == "urn:entity:test-file"
        mock_store.query.assert_called_once()

    def test_get_file_entity_not_found(self):
        """get_file_entityで該当するエンティティが見つからない場合のテストケースです。"""
        mock_store = mock.Mock()
        mock_store.query.return_value = []  # 結果なし

        searcher = ProvenanceSearcher(rdf_store=mock_store)

        result = searcher.get_file_entity("http://example.com/none.txt")

        assert result is None

    def test_get_file_entity_query_fail(self):
        """get_file_entityでクエリ実行時に例外が発生するテストケースです。"""
        mock_store = mock.Mock()
        mock_store.query.side_effect = Exception("SPARQL execution failed")

        searcher = ProvenanceSearcher(rdf_store=mock_store)

        with pytest.raises(RuntimeError) as excinfo:
            searcher.get_file_entity("http://example.com/file1.txt")

        assert "RDFクエリの実行に失敗しました" in str(excinfo.value)

    def test_get_entity_info_success(self):
        """get_entity_infoで情報が取得できるテストケースです。"""
        mock_store = mock.Mock()
        mock_graph = mock.Mock()
        mock_store.query.return_value = mock_graph

        searcher = ProvenanceSearcher(rdf_store=mock_store)
        entity_uri = "urn:entity:test"

        result = searcher.get_entity_info(entity_uri)

        assert result == mock_graph
        mock_store.query.assert_called_once()

        # クエリにURIが含まれているか軽く確認
        called_query = mock_store.query.call_args[0][0]
        assert f"<{entity_uri}>" in called_query

    def test_get_entity_info_query_fail(self):
        """RDFクエリ実行時に例外が発生するテストケースです。"""
        mock_store = mock.Mock()
        mock_store.query.side_effect = Exception("SPARQLエラー")

        searcher = ProvenanceSearcher(rdf_store=mock_store)

        with pytest.raises(RuntimeError) as excinfo:
            searcher.get_entity_info("urn:entity:fail")

        assert "RDFクエリの実行に失敗しました" in str(excinfo.value)

    def test_get_all_entity_info_success(self):
        """get_all_entity_infoでエンティティ情報が正常に取得できるテストケースです。"""
        mock_store = mock.Mock()
        mock_result = mock.Mock()
        mock_store.query.return_value = mock_result

        searcher = ProvenanceSearcher(rdf_store=mock_store)
        location = "file:///test/path/file.txt"

        result = searcher.get_all_entity_info(location)

        assert result == mock_result
        mock_store.query.assert_called_once()

        # クエリにlocationが含まれているか軽く確認
        called_query = mock_store.query.call_args[0][0]
        assert location in called_query

    def test_get_all_entity_info_query_fail(self):
        """RDFクエリ実行時に例外が発生した場合のテストケースです。"""
        mock_store = mock.Mock()
        mock_store.query.side_effect = Exception("SPARQLエラー")

        searcher = ProvenanceSearcher(rdf_store=mock_store)
        location = "file:///test/path/error.txt"

        with pytest.raises(RuntimeError) as excinfo:
            searcher.get_all_entity_info(location)

        assert "RDFクエリの実行に失敗しました" in str(excinfo.value)

    def test_get_activity_info_success(self):
        """get_activity_infoでアクティビティ情報が正常に取得できるテストケースです。"""
        mock_store = mock.Mock()
        mock_result = mock.Mock()
        mock_store.query.return_value = mock_result

        searcher = ProvenanceSearcher(rdf_store=mock_store)
        activity_uri = "urn:activity:test-activity"

        result = searcher.get_activity_info(activity_uri)

        assert result == mock_result
        mock_store.query.assert_called_once()

        # クエリ文字列に URI が含まれていることを軽く確認
        called_query = mock_store.query.call_args[0][0]
        assert activity_uri in called_query

    def test_get_activity_info_query_fail(self):
        """RDFクエリ実行時に例外が発生した場合のテストケースです。"""
        mock_store = mock.Mock()
        mock_store.query.side_effect = Exception("SPARQLエラー")

        searcher = ProvenanceSearcher(rdf_store=mock_store)
        activity_uri = "urn:activity:fail-activity"

        with pytest.raises(RuntimeError) as excinfo:
            searcher.get_activity_info(activity_uri)

        assert "RDFクエリの実行に失敗しました" in str(excinfo.value)

    def test_get_all_entities_success(self):
        """get_all_entitiesが正しくエンティティを返すテストケースです。"""
        mock_store = mock.Mock()

        # 疑似的なSPARQLクエリ結果
        mock_result = [
            {"label": "dir/path", "entity": "urn:entity:1"},
            {"label": "dir/path", "entity": "urn:entity:2"},
            {"label": "another/dir", "entity": "urn:entity:3"},
        ]

        mock_store.query.return_value = mock_result

        searcher = ProvenanceSearcher(rdf_store=mock_store)
        dir_path = "dir/path"

        result = searcher.get_all_entities(dir_path)

        expected = {
            "dir/path": ["urn:entity:1", "urn:entity:2"],
            "another/dir": ["urn:entity:3"],
        }

        assert result == expected
        mock_store.query.assert_called_once()

        called_query = mock_store.query.call_args[0][0]
        assert dir_path in called_query

    def test_get_all_entities_query_fail(self):
        """RDFクエリ実行時に例外が発生した場合のテストケースです。"""
        mock_store = mock.Mock()
        mock_store.query.side_effect = Exception("クエリエラー")

        searcher = ProvenanceSearcher(rdf_store=mock_store)

        with pytest.raises(RuntimeError) as excinfo:
            searcher.get_all_entities("some/path")

        assert "RDFクエリの実行に失敗しました" in str(excinfo.value)
























    def test_query_agent(self, test_jsonld_files):
        with mock.patch("data_governance.library.utils.research_flow_provenance.rdf.RDFStore.__init__", lambda self: None):
            rdf_store = RDFStore()

        rdf_store.vocab_file = test_jsonld_files["vocab"]
        rdf_store.entity_file = test_jsonld_files["entity"]
        rdf_store.activity_file = test_jsonld_files["activity"]
        rdf_store.agent_file = test_jsonld_files["agent"]
        rdf_store.graph = None

        rdf_store.load_graph()

        # クエリでagentを検索
        agent_uri = "urn:agent:ase4f2-8a7b6c5d-4e3f-2a1b-0c9d-87654321abcd"  # 実際のURIに合わせて調整
        query = f"""
            PREFIX prov: <http://www.w3.org/ns/prov#>

            SELECT ?agent
            WHERE {{
                ?agent a prov:Agent .
                FILTER (?agent = <{agent_uri}>)
            }}
        """

        result = rdf_store.query(query)
        print(result)
        # 結果が空じゃないことを確認
        assert len(result) > 0, "クエリでエージェントが見つかりませんでした"

        # 結果に指定したagent_uriが含まれていることを確認
        for row in result:
            print(str(row["agent"]))

    def test_query_entity(self, test_jsonld_files):
        with mock.patch("data_governance.library.utils.research_flow_provenance.rdf.RDFStore.__init__", lambda self: None):
            rdf_store = RDFStore()

        rdf_store.vocab_file = test_jsonld_files["vocab"]
        rdf_store.entity_file = test_jsonld_files["entity"]
        rdf_store.activity_file = test_jsonld_files["activity"]
        rdf_store.agent_file = test_jsonld_files["agent"]
        rdf_store.graph = None

        rdf_store.load_graph()

        # クエリでagentを検索
        file_link = "grdm:data/experiment/実験１/argument_data/論拠データ１.csv"# 実際のURIに合わせて調整
        query = f"""
        PREFIX prov: <http://www.w3.org/ns/prov#>

        SELECT ?entity
        WHERE {{
            ?entity a prov:Entity ;
                prov:atLocation <{file_link}> .

            FILTER NOT EXISTS {{
                ?entity prov:wasUsedBy ?activity .
                FILTER CONTAINS(STR(?activity), "deleteActivity")
            }}
        }}
        """

        result = rdf_store.query(query)
        print(result)
        # 結果が空じゃないことを確認
        assert len(result) > 0, "クエリでエージェントが見つかりませんでした"

        # 結果に指定したagent_uriが含まれていることを確認
        for row in result:
            print(str(row["entity"]))

    def test_query_entity2(self, test_jsonld_files):
        with mock.patch("data_governance.library.utils.research_flow_provenance.rdf.RDFStore.__init__", lambda self: None):
            rdf_store = RDFStore()

        rdf_store.vocab_file = test_jsonld_files["vocab"]
        rdf_store.entity_file = test_jsonld_files["entity"]
        rdf_store.activity_file = test_jsonld_files["activity"]
        rdf_store.agent_file = test_jsonld_files["agent"]
        rdf_store.graph = None

        rdf_store.load_graph()

        # クエリでagentを検索
        dir_path = "論拠データ1.csv"# 実際のURIに合わせて調整
        query = f"""
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>


        SELECT ?entity ?label
        WHERE {{
            ?entity a prov:Entity ;
                    rdfs:label ?label .

            FILTER (STR(?label) = "{dir_path}")

            FILTER NOT EXISTS {{
                ?entity prov:wasUsedBy ?activity .
                FILTER CONTAINS(STR(?activity), "deleteActivity")
            }}
        }}
        """

        results = rdf_store.query(query)
        print(results)
        # 結果が空じゃないことを確認
        assert len(results) > 0, "クエリでエージェントが見つかりませんでした"

        # 結果に指定したagent_uriが含まれていることを確認
        grouped = {}
        for row in results:
            label = str(row["label"])
            uri = str(row["entity"])
            grouped.setdefault(label, []).append(uri)

        print(grouped)
