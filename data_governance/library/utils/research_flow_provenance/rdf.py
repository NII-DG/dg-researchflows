"""RDFの操作を行うモジュールです"""

import os
import shutil
from typing import Optional
from rdflib import Graph
from rdflib.query import Result
from owlrl import DeductiveClosure, OWLRL_Semantics

from library.utils.config import path_config

class RDFStore:
    """来歴情報をRDFとして読み込むクラスです。

    RDFオブジェクトを直接操作する処理を記述しています。

    Attributes:
        class:
            PROV_VOCAB(str): 語彙ファイルの名前
            PROV_ENTITY(str): エンティティを記録するファイルの名前
            PROV_ACTIVITY(str): アクティビティを記録するファイルの名前
            PROV_AGENT(str): エージェントを記録するファイルの名前
            TEMPLATE_JSONLD(str): 来歴ファイルのテンプレートファイルのパス
            VOCAB_JSONLD(str): 語彙ファイルのパス
        instances:
            self.vocab_file(str): 語彙ファイルの絶対パス
            self.entity_file(str): エンティティを記録するJSON-LDファイルの絶対パス
            self.activity_file(str): アクティビティを記録するJSON-LDファイルの絶対パス
            self.agent_file(str): エージェントを記録するJSON-LDファイルの絶対パス
            self.graph(Graph): グラフオブジェクトのインスタンス

    """
    PROV_VOCAB = "vocab.jsonld"
    PROV_ENTITY = "entity.jsonld"
    PROV_ACTIVITY = "activity.jsonld"
    PROV_AGENT = "agent.jsonld"

    TEMPLATE_JSONLD = "data_governance/library/utils/research_flow_provenance/template.jsonld"
    VOCAB_JSONLD = "data_governance/library/utils/research_flow_provenance/vocab.jsonld"

    def __init__(self):
        """クラスのコンストラクタです。

        JSON-LDファイルのパスを取得します。

        """
        home = os.environ['HOME']
        env_name = os.environ['JUPYTERHUB_SERVER_NAME']
        base_path = os.path.join(home, path_config.DG_RESEARCHFLOW_FOLDER, env_name)

        self.vocab_file = os.path.join(base_path, self.PROV_VOCAB)
        self.entity_file = os.path.join(base_path, self.PROV_ENTITY)
        self.activity_file = os.path.join(base_path, self.PROV_ACTIVITY)
        self.agent_file = os.path.join(base_path, self.PROV_AGENT)

        if not os.path.exists(self.vocab_file):
            # 出力先ディレクトリがなければ作成する
            os.makedirs(os.path.dirname(self.vocab_file), exist_ok=True)

            shutil.copy(os.path.join(home, self.VOCAB_JSONLD), self.vocab_file)

        for path in [self.entity_file, self.activity_file, self.agent_file]:
            if not os.path.exists(path):
                os.makedirs(os.path.dirname(path), exist_ok=True)

                shutil.copy(os.path.join(home, self.TEMPLATE_JSONLD), path)

    def query(self, query: str):
        """クエリで検索を行う関数です。

        引数として渡されたクエリを実行する関数です。

        Args:
            query (str): クエリ文

        Returns:
            _type_: 実行結果

        """
        return self.graph.query(query)

    def load_graph(self):
        """ファイルを読み込む関数です。

        RDF形式で読み込み、推論エンジンを適用します。

        Raises:
            RuntimeError: JSON-LDファイルの読み込みに失敗した。

        """
        jsonld_files = [self.vocab_file, self.entity_file, self.activity_file, self.agent_file]

        self.graph = Graph()
        for file in jsonld_files:
            try:
                self.graph.parse(file, format="json-ld")
            except Exception as e:
                raise RuntimeError(f"{file}の読み込みに失敗しました: {e}")

        DeductiveClosure(OWLRL_Semantics).expand(self.graph)

    def reload(self):
        """再読み込みする関数です。"""
        self.load_graph()

class ProvenanceSearcher:
    """来歴情報を検索するクラスです。

    RDFStoreで読み込んだRDFに対してクエリを実行する処理を記述しています。

    Attributes:
        instances:
            rdf_store(RDFStore): RDFStoreクラスのインスタンス

    """
    def __init__(self, rdf_store: RDFStore):
        """クラスのインスタンスの初期化を行うメソッドです。

        Args:
            rdf_store (RDFStore): RDFStoreクラスのインスタンス

        """
        self.rdf_store = rdf_store

    def get_excution_user(self, agent_uri:str)-> Optional[str]:
        """実行ユーザーの情報を取得する関数です。

        Args:
            agent_uri (str): エージェントのURI

        Returns:
            Optional[str]: 実行ユーザーが存在する場合はURIを返す。

        Raises:
            RuntimeError: クエリの実行に失敗した。

        """
        query = f"""
        PREFIX prov: <http://www.w3.org/ns/prov#>

        SELECT ?agent
        WHERE {{
            ?agent a prov:Agent .
            FILTER (?agent = <{agent_uri}>)
        }}
        """
        try:
            results = self.rdf_store.query(query)
        except Exception as e:
            raise RuntimeError(f"RDFクエリの実行に失敗しました: {e}") from e

        for row in results:
            return str(row["agent"])

        return None

    def get_file_entity(self, file_link: str) ->Optional[str]:
        """指定されたリンクを持つ有効なエンティティをひとつ取得する。

        Args:
            file_link (str):エンティティのGRDMリンク

        Returns:
            Optional[str]: 該当するエンティティが見つかった場合にURIを返す

        Raises:
            RuntimeError: クエリの実行に失敗した

        """
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
        try:
            result = self.rdf_store.query(query)
        except Exception as e:
            raise RuntimeError(f"RDFクエリの実行に失敗しました: {e}") from e

        for row in result:
            return str(row["entity"])

        return None

    def get_file_entity_list(self, file_link: str) ->Optional[list]:
        """指定されたリンクを持つ有効なエンティティを全て取得する。

        Args:
            file_link (str):エンティティのGRDMリンク

        Returns:
            Optional[list]: 該当するエンティティが見つかった場合にURIを返す

        Raises:
            RuntimeError: クエリの実行に失敗した

        """
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
        try:
            result = self.rdf_store.query(query)

        except Exception as e:
            raise RuntimeError(f"RDFクエリの実行に失敗しました: {e}") from e

        entities = []
        for row in result:
            entities.append(str(row["entity"]))

        if entities:
            return entities
        else:
            return None

    def get_entity_info(self, entity_uri: str) -> Result:
        """指定されたエンティティの情報を取得する。

        Args:
            entity_uri (str): エンティティのURI

        Returns:
            Result: 指定したエンティティに関する全情報

        Raises:
            RuntimeError: クエリの実行に失敗した

        """
        query = f"""
        PREFIX prov: <http://www.w3.org/ns/prov#>

        CONSTRUCT {{
        <{entity_uri}> ?p ?o .
        }}
        WHERE {{
            <{entity_uri}> ?p ?o .

        }}

        """
        try:
            results = self.rdf_store.query(query)
        except Exception as e:
            raise RuntimeError(f"RDFクエリの実行に失敗しました: {e}") from e

        return results

    def get_all_entity_info(self, location: str) -> Result:
        """指定されたファイルの全てのエンティティの情報を取得する。

        Args:
            location (str): エンティティのGRDMリンク

        Returns:
            Result: クエリの実行結果

        Raises:
            RuntimeError: クエリの実行に失敗した

        """
        query = f"""
        PREFIX prov: <http://www.w3.org/ns/prov#>

        CONSTRUCT {{
            ?entity ?p ?o .
        }}
        WHERE {{
            ?entity a prov:Entity ;
                    prov:atLocation ?location .
            ?entity ?p ?o .

            FILTER(STR(?location) = "{location}")
        }}
        """
        try:
            result = self.rdf_store.query(query)
        except Exception as e:
            raise RuntimeError(f"RDFクエリの実行に失敗しました: {e}") from e

        return result

    def get_activity_info(self, activity_uri: str) -> Result:
        """指定されたエンティティの情報を取得する。

        Args:
            activity_uri (str): アクティビティのURI

        Returns:
            Result: 指定したアクティビティの全情報

        Raises:
            RuntimeError: クエリの実行に失敗した。

        """
        query = f"""
        PREFIX prov: <http://www.w3.org/ns/prov#>

        CONSTRUCT {{
        <{activity_uri}> ?p ?o .
        }}
        WHERE {{
        <{activity_uri}> ?p ?o .
        }}

        """
        try:
            results = self.rdf_store.query(query)
        except Exception as e:
            raise RuntimeError(f"RDFクエリの実行に失敗しました: {e}") from e

        return results

    def get_all_entities(self, dir_path: str) -> dict:
        """指定されたディレクトリ内の全てのエンティティを取得する。

        Args:
            dir_path (str): ディレクトリパス

        Returns:
            dict: 該当するエンティティのlabelとURIの辞書型データ。

        Raises:
            RuntimeError: クエリの実行に失敗した。

        """
        query = f"""
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?entity ?label
        WHERE {{
            ?entity a prov:Entity ;
                rdfs:label ?label .

            FILTER(CONTAINS(STR(?label), "{dir_path}"))

            FILTER NOT EXISTS {{
                ?entity prov:wasUsedBy ?activity .
                FILTER(CONTAINS(STR(?activity), "deleteActivity"))
            }}
        }}
        """
        try:
            results = self.rdf_store.query(query)
        except Exception as e:
            raise RuntimeError(f"RDFクエリの実行に失敗しました: {e}") from e

        grouped = {}
        for row in results:
            label = str(row["label"])
            uri = str(row["entity"])
            grouped.setdefault(label, []).append(uri)

        return grouped