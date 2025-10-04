"""来歴情報をJSON-LDに記録するためのモジュールです。

JSON-LDファイルに来歴情報を書き込む処理を記載します。
"""

import json
import os
import shutil
from typing import Union
import uuid

from datetime import datetime, timezone, timedelta
from pathlib import Path

from library.utils.config import path_config

def generated_id(base_id: str) -> str:
    """UUIDを付与し、完全なURIを生成する関数です。

    Args:
        base_id (str): ベースとなる文字列

    Returns:
        str: UUIDを付与したid
    """
    return f"{base_id}-{uuid.uuid4()}"

class ProvenanceEditor:
    """来歴情報を編集するためのクラスです。

    JSON-LDファイルに対する書き込みを行う処理をまとめています。

    Attributtes:
        class:
            PROV_ENTITY(str): エンティティを記録するファイルの名前
            PROV_ACTIVITY(str): アクティビティを記録するファイルの名前
            PROV_AGENT(str): エージェントを記録するファイルの名前
            ENTITY_BASE(str): エンティティのURIの先頭部分
            COLLECTION_BASE(str): コレクションのURIの先頭部分
            ACTIVITY_BASE(str): アクティビティのURIの先頭部分
            AGENT_BASE(str): エージェントのURIの先頭部分
            TEMPLATE_JSONLD(str): 来歴ファイルのテンプレートファイルのパス
        instannce:
            self.entity_file(str): エンティティを記録するJSON-LDファイルの絶対パス
            self.activity_file(str): アクティビティを記録するJSON-LDファイルの絶対パス
            self.agent_file(str): エージェントを記録するJSON-LDファイルの絶対パス

    """
    # JSON-LDファイル名
    PROV_ENTITY = "entity.jsonld"
    PROV_ACTIVITY = "activity.jsonld"
    PROV_AGENT = "agent.jsonld"

    # URIの先頭部分
    ENTITY_BASE = "urn:entity:"
    COLLECTION_BASE = "urn:collection:"
    ACTIVITY_BASE = "urn:activity:"
    AGENT_BASE = "urn:agent:"

    TEMPLATE_JSONLD = "data_governance/library/utils/research_flow_provenance/template.jsonld"

    def __init__(self):
        """クラスのインスタンスの初期化を行うメソッドです。

        JSON-LDファイルのパスを取得します。

        """
        home = os.environ['HOME']
        env_name = os.environ['JUPYTERHUB_SERVER_NAME']
        base_path = os.path.join(home, path_config.DG_RESEARCHFLOW_FOLDER, env_name)

        self.entity_file = os.path.join(base_path, self.PROV_ENTITY)
        self.activity_file = os.path.join(base_path, self.PROV_ACTIVITY)
        self.agent_file = os.path.join(base_path, self.PROV_AGENT)

        for path in [self.entity_file, self.activity_file, self.agent_file]:
            if not os.path.exists(path):
                # 出力先ディレクトリがなければ作成する
                os.makedirs(os.path.dirname(path), exist_ok=True)

                shutil.copy(os.path.join(home, self.TEMPLATE_JSONLD), path)

    def create_activity(
            self, activity_id: str, activity_type: str, used_entities: list,
            agent_id: Union[str, list], comment: str=None,
            old_provenances: list=None):
        """アクティビティを新規作成する関数です。

        Args:
            activity_id (str): 作成するアクティビティのURI
            activity_type (str): アクティビティのタイプ（コピーやアップロードなど）
            used_entities (list): このアクティビティが使用したエンティティのリスト
            agent_id (Union[str, list]): このアクティビティを実行したエージェントのURI
            comment (str): このアクティビティに関するコメント
                            デフォルトはNone
            old_provenances (list): 来歴情報の編集アクティビティのみ使用する過去の来歴情報
                                    デフォルトはNone

        Raises:
            RuntimeError: 来歴情報ファイルの読み込み/書き込みに失敗した。
        """

        ended_time = self._generated_end_timestamp()
        try:
            with open(self.activity_file, "r", encoding="utf-8") as f:
                activity_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise RuntimeError(f"{self.activity_file}の読み込みに失敗しました: {e}") from e
        graph = activity_data.get("@graph", [])

        if not isinstance(agent_id, list):
            agent_id = [agent_id]

        new_activity = {
            "@id": activity_id,
            "@type": "prov:Activity",
            "label": activity_type,
            "prov:endedAtTime": {
                "@value": ended_time,
                "@type": "xsd:dateTime"
            },
            "prov:used": [{"@id": entity} for entity in used_entities],
            "prov:wasAssociatedWith": [{"@id": agent} for agent in agent_id],
        }

        if comment:
            new_activity["comment"] = comment

        if old_provenances:
            new_activity["prov:qualifiedUsage"] = [
                {
                    "@type": "prov:Usage",
                    "label": "old provenance",
                    "prov:entity": entity_id
                }
                for entity_id in old_provenances
            ]

        graph.append(new_activity)
        activity_data["@graph"] = graph

        try:
            with open(self.activity_file, "w", encoding="utf-8") as f:
                json.dump(activity_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise RuntimeError(f"{self.activity_file}の書き込みに失敗しました: {e}") from e

    def create_entity(
            self, dst_path: str, location: str, hash_value:str,
            activity_id: str=None, src_path: Union[str, list[str]]=None,
            agents: Union[str, list]=None) -> str:
        """エンティティを新規作成する関数です。

        Args:
            dst_path (str): 新しく作成するエンティティのファイルパス
            location (str): 新しく作成するエンティティのGRDMリンク
            hash_value (str): 新しく作成するエンティティのファイルのハッシュ値
            activity_id (str): エンティティを作成するアクティビティのURI
                                デフォルトはNone
            src_path (Union[str, list[str]]): エンティティの派生元となるエンティティのURI
            　　　　　　　　　　　　　　　　　　　デフォルトはNone
            agents (Optional[Union[str, list]]): エンティティを作成したエージェントのURI
                                                    デフォルトはNone
        Returns:
            str: 作成したエンティティのURI

        Raises:
            RuntimeError: 来歴情報ファイルの読み込み/書き込みに失敗した。

        """
        try:
            with open(self.entity_file, "r", encoding="utf-8") as f:
                entity_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise RuntimeError(f"{self.entity_file}の読み込みに失敗しました: {e}") from e

        graph = entity_data.get("@graph", [])

        base_id = self.ENTITY_BASE + Path(dst_path).name

        entity_id = generated_id(base_id)

        new_entity = {
            "@id": entity_id,
            "@type": "prov:Entity",
            "label": dst_path,
            "prov:atLocation":{
                "@id": location
            },
            "dcat:checksum": {
                "checksumAlgorithm": "SHA-256",
                "hashValue": hash_value
            }
        }
        if src_path:
            if isinstance(src_path, str):
                src_path = [src_path]
            if "modifyActivity" in activity_id:
                new_entity["prov:wasRevisionOf"] = [{"@id": path} for path in src_path]
            else:
                new_entity["prov:wasDerivedFrom"] = [{"@id": path} for path in src_path]
            new_entity["prov:wasGeneratedBy"] = {"@id":activity_id}

        if agents:
            if isinstance(agents, str):
                agents = [agents]
            new_entity["prov:wasAttributedTo"] = [{"@id": path} for path in agents]

        graph.append(new_entity)
        entity_data["@graph"] = graph

        try:
            with open(self.entity_file, "w", encoding="utf-8") as f:
                json.dump(entity_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise RuntimeError(f"{self.entity_file}の書き込みに失敗しました: {e}") from e

        return entity_id

    def create_collection(
            self, members: list, dst_path: str=None,
            location: str=None, label: str=None) -> str:
        """コレクションを作成する関数です。

        Args:
            members (list): コレクションのメンバー
            dst_path (str): コレクションのフォルダパス
            　　　　　　　　　デフォルトはNone　
            location（str): コレクションのGRDMリンク
                            デフォルトはNone
            label (str): コレクションが実体を持たないときに渡される固定の文字列
                        　デフォルトはNone

        Returns:
            str: 作成したコレクションURI

        Raises:
            RuntimeError: 来歴情報ファイルの読み込み/書き込みに失敗した。

        """
        try:
            with open(self.entity_file, "r", encoding="utf-8") as f:
                entity_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise RuntimeError(f"{self.entity_file}の読み込みに失敗しました: {e}") from e

        graph = entity_data.get("@graph", [])

        if label is None:
            label = Path(dst_path).name
        base_id = self.COLLECTION_BASE + label

        entity_id = generated_id(base_id)

        new_collection = {
            "@id": entity_id,
            "@type": "prov:Collection",
            "label": label,
            "prov:hadMember": [{"@id": member} for member in members],
        }
        if location:
            new_collection["prov:atLocation"] = {"@id": location}

        graph.append(new_collection)
        entity_data["@graph"] = graph

        try:
            with open(self.entity_file, "w", encoding="utf-8") as f:
                json.dump(entity_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise RuntimeError(f"{self.entity_file}の書き込みに失敗しました: {e}") from e

        return entity_id

    def edit_entity(self, entity_id: str, activity_id: str=None, new_entities: list=None):
        """エンティティを編集する関数です。

        Args:
            entity_id (str): 編集を行うエンティティのURI
            activity_id (str): 編集を行うアクティビティのURI
            new_entities (list): 新しく関連付けるエンティティのURI

        Raises:
            RuntimeError: 来歴情報ファイルの読み込み/書き込みに失敗した。
            ValueError: 指定されたエンティティURIが存在しない。

        """
        try:
            with open(self.entity_file, "r", encoding="utf-8") as f:
                entity_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise RuntimeError(f"{self.entity_file}の読み込みに失敗しました: {e}") from e

        graph = entity_data.get("@graph", [])

        entity = next((item for item in graph if item.get("@id") == entity_id), None)

        if not entity:
            raise ValueError(f"指定されたエンティティIDが存在しません: {entity_id}")

        old_provenance = []
        derived_from = entity["prov:wasDerivedFrom"]
        if not new_entities:

            old_provenance = [item["@id"] for item in derived_from if "@id" in item]
            # キーごと削除
            del entity["prov:wasDerivedFrom"]

        else:

            if "prov:wasRevisionOf" in entity:
                entity["prov:wasRevisionOf"] = [{"@id": _id} for _id in new_entities]

            else:
                old_provenance = [item["@id"] for item in derived_from if "@id" in item]
                entity["prov:wasDerivedFrom"] = [{"@id": _id} for _id in new_entities]

            entity.setdefault("prov:wasInfluencedBy", []).extend([{"@id": activity_id}])

        try:
            with open(self.entity_file, "w", encoding="utf-8") as f:
                json.dump(entity_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise RuntimeError(f"{self.entity_file}の書き込みに失敗しました: {e}") from e

        return old_provenance

    def edit_collection(self, entity_id: str, activity_id: str, new_member: list):
        """コレクションを編集する関数です。

        Args:
            entity_id (str): 編集を行うコレクションのURI
            activity_id (str): 編集を行うアクティビティのURI
            new_member (list): 新しく関連付けるエンティティのURI

        Raises:
            RuntimeError: 来歴情報ファイルの読み込み/書き込みに失敗した。

        """
        try:
            with open(self.entity_file, "r", encoding="utf-8") as f:
                entity_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise RuntimeError(f"{self.entity_file}の読み込みに失敗しました: {e}") from e

        graph = entity_data.get("@graph", [])

        collection = next((item for item in graph if item.get("@id") == entity_id), None)

        collection["prov:hadMember"] = [{"@id": _id} for _id in new_member]

        collection.setdefault("prov:wasInfluencedBy", []).extend([{"@id": activity_id}])

        try:
            with open(self.entity_file, "w", encoding="utf-8") as f:
                json.dump(entity_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise RuntimeError(f"{self.entity_file}の書き込みに失敗しました: {e}") from e

    def create_agent(self, agent_id: str, agent_type: list, agent_name: str, comment: str=None) ->str:
        """エージェントを作成する関数です。

        Args:
            agent_id (str): 作成するエージェントのURI
            agent_type (list): エージェントのタイプ（personやsoftwareなど）
            agent_name (str): エージェント名
            comment (str): エージェントに関するコメント
                            デフォルトはNone

        Returns:
            str: 作成したエージェントのURI

        Raises:
            RuntimeError: 来歴情報ファイルの読み込み/書き込みに失敗した。

        """
        try:
            with open(self.agent_file, "r", encoding="utf-8") as f:
                agent_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise RuntimeError(f"{self.agent_file}の読み込みに失敗しました: {e}") from e

        graph = agent_data.get("@graph", [])

        new_agent = {
            "@id": agent_id,
            "@type": agent_type,
            "label": agent_name
        }
        if comment:
            new_agent["comment"] = comment

        graph.append(new_agent)
        agent_data["@graph"] = graph

        try:
            with open(self.agent_file, "w", encoding="utf-8") as f:
                json.dump(agent_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise RuntimeError(f"{self.agent_file}の書き込みに失敗しました: {e}") from e

        return agent_id

    def _generated_end_timestamp(self) -> str:
        """アクティビティ終了時間を出力する関数です。

        Returns:
            str: アクティビティの終了時間。

        """
        return datetime.now(timezone(timedelta(hours=9))).isoformat()

    def delete_activity(self, activity_uri:str):
        """アクティビティを削除する関数です。"""
        try:
            with open(self.activity_file, "r", encoding="utf-8") as f:
                activity_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise RuntimeError(f"{self.activity_file}の読み込みに失敗しました: {e}") from e

        graph = activity_data.get("@graph", [])

        # 一致したら除外（≒一致しないものだけ残す）
        filtered_graph = []
        for entry in graph:
            if entry.get("@id") == activity_uri:
                continue  # 一致 → 除外
            filtered_graph.append(entry)

        # グラフを更新
        activity_data["@graph"] = filtered_graph

        try:
            with open(self.activity_file, "w", encoding="utf-8") as f:
                json.dump(activity_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise RuntimeError(f"{self.activity_file}の書き込みに失敗しました: {e}") from e

    def delete_entity(self, entity_uri:str):
        """エンティティの削除関数です。"""
        try:
            with open(self.entity_file, "r", encoding="utf-8") as f:
                entity_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise RuntimeError(f"{self.entity_file}の読み込みに失敗しました: {e}") from e

        graph = entity_data.get("@graph", [])

        # 一致したら除外（≒一致しないものだけ残す）
        filtered_graph = []
        for entry in graph:
            if entry.get("@id") == entity_uri:
                continue  # 一致 → 除外
            filtered_graph.append(entry)

        # グラフを更新
        entity_data["@graph"] = filtered_graph

        try:
            with open(self.entity_file, "w", encoding="utf-8") as f:
                json.dump(entity_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise RuntimeError(f"{self.entity_file}の書き込みに失敗しました: {e}") from e
        
    def change_entity_label(self, entity_id: str, new_label: str):
        """エンティティのラベルを編集する関数です。

        Args:
            entity_id (str): 編集を行うエンティティのURI
            new_label (str): 新しく関連付けるエンティティのラベル

        Raises:
            RuntimeError: 来歴情報ファイルの読み込み/書き込みに失敗した。
            ValueError: 指定されたエンティティURIが存在しない。

        """
        try:
            with open(self.entity_file, "r", encoding="utf-8") as f:
                entity_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise RuntimeError(f"{self.entity_file}の読み込みに失敗しました: {e}") from e

        graph = entity_data.get("@graph", [])

        entity = next((item for item in graph if item.get("@id") == entity_id), None)

        if not entity:
            raise ValueError(f"指定されたエンティティIDが存在しません: {entity_id}")

        entity["label"] = new_label

        try:
            with open(self.entity_file, "w", encoding="utf-8") as f:
                json.dump(entity_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise RuntimeError(f"{self.entity_file}の書き込みに失敗しました: {e}") from e

    def get_file_list(self) -> list:
        """来歴ファイルのリストを返すメソッドです。

        Returns:
            list: 来歴ファイルのリスト
        """
        return [self.entity_file, self.activity_file, self.agent_file]
