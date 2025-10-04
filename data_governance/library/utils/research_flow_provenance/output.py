"""来歴情報をREADME.mdに出力する処理を記述したモジュールです。"""

from dataclasses import dataclass
import os
from pathlib import Path
import re

from rdflib.query import Result
from rdflib import Namespace, URIRef
from .rdf import ProvenanceSearcher

from library.utils.config import path_config
# from rdflib.namespace import RDFS, Namespace

@dataclass
class FileInfo:
    """ファイルの来歴情報を管理するためのデータクラスです。

    Attributes:
        class:
            file_name(str): ファイル名
            file_path(str): ファイルパス
            link(str): GRDMリンク
            related_files:(list[dict[str, str]]): 関連するファイルの情報

    """
    file_name: str
    file_path: str
    link: str
    related_files: list[dict[str, str]]

class OutputProvenance:
    """来歴情報をREADME.mdに出力するクラスです。

    Attributes:
        class:
            TEMPLATE_README(str): テンプレートのREADMEファイルのパス
        instances:
            searcher(ProvenanceSearcher): ProvenanceSearcherクラスのインスタンス

    """
    TEMPLATE_README = "data_governance/library/utils/research_flow_provenance/base_readme.md"

    def __init__(self, searcher: ProvenanceSearcher):
        """クラスのコンストラクタです。"""
        self.searcher = searcher

    def write(self, update_files: list):
        """ファイルの来歴情報をREADME.mdに記述する関数です。

        Args:
            update_files (list): 更新対象のファイル

        """
        update_informations ={}
        for file in update_files:
            results = self.searcher.get_all_entity_info(file)
            subflow, info = self.set_file_info(results, file)
            update_informations.setdefault(subflow, []).append(info)

        home = os.environ['HOME']
        base_path = os.path.join(home,  path_config.DATA)

        for subflow, info_list in update_informations.items():
            readme_path = Path(os.path.join(base_path, subflow, "README.md"))
            # 初回のみテンプレートから生成
            if not readme_path.exists():
                template_path = os.path.join(home, self.TEMPLATE_README)
                template_text = Path(template_path).read_text(encoding="utf-8")
                updated_template = re.sub(
                    r"(##\s*サブフロー：)",
                    rf"\1{subflow}",
                    template_text,
                    flags=re.MULTILINE
                )
                readme_path.write_text(updated_template, encoding="utf-8")

            readme_text = readme_path.read_text(encoding="utf-8")

            # セクション抽出 (全文, file_path, link)
            section_pattern = r"(##\s+\[.+?（(.+?)）\]\((https?://[^\)]+)\)[\s\S]*?)(?=\n## |\Z)"
            matched_sections = re.findall(section_pattern, readme_text)

            def remove_sections(text: str, sections: list) ->str:
                """ファイル本文からセクション部分を全て除去するための置換処理

                Args:
                    text (str): README.mdの本文
                    sections (list): 置換するセクション

                Returns:
                    str: 置換するセクションを除去したREADME.mdの本文
                """
                for sec in sections:
                    text = text.replace(sec, "")
                return text

            all_sections_text = [sec for sec, _, _ in matched_sections]
            readme_body = remove_sections(readme_text, all_sections_text).strip()

            # リンクごとにセクションをまとめる
            sections_by_link = {}
            for section, file_path, link in matched_sections:
                sections_by_link.setdefault(link, []).append(section)

            new_links = set(fi.link for fi in info_list)

            # ここで既存のセクションから新リンクに該当するものは辞書からも削除し置換準備
            for link in new_links:
                if link in sections_by_link:
                    del sections_by_link[link]

            # 新しいセクション作成
            new_sections = {}
            link_to_path = {}

            for file_info in info_list:
                header = f"## [{file_info.file_name}（{file_info.file_path}）]({file_info.link})"
                related_lines = [
                    (
                        f'{rel["type"]}：{rel["label"]}（削除済み）'
                        if rel["location"] == "削除済み"
                        else f'{rel["type"]}：[{"{0}".format(rel["label"])}]({rel["location"]})'
                    )
                    for rel in file_info.related_files
                ]

                new_section = "\n".join([header] + related_lines) + "\n"
                new_sections[file_info.link] = new_section
                link_to_path[file_info.link] = file_info.file_path

            # 残った既存セクションを残す
            merged_sections = {}
            for link, sections in sections_by_link.items():
                # 複数あっても先頭だけ保持
                merged_sections[link] = sections[0]

            # 新セクションを追加
            merged_sections.update(new_sections)

            # file_pathでソート
            for link in merged_sections:
                if link not in link_to_path:
                    link_to_path[link] = "zzz"

            sorted_links = sorted(merged_sections.keys(), key=lambda l: link_to_path.get(l, "zzz"))
            sorted_sections = [merged_sections[link].strip() for link in sorted_links]

            final_text = readme_body + "\n\n" + "\n\n".join(sorted_sections) + "\n"
            readme_path.write_text(final_text, encoding="utf-8")

    def set_file_info(self, results:Result, location: str) -> FileInfo:
        """ファイルの来歴情報をセットする関数です。

        Args:
            results (Result): クエリの実行結果（エンティティ情報）
            location (str): 更新対象のファイルリンク

        Returns:
            FileInfo: ファイルの来歴情報をFileInfoクラスにセットしたもの

        """
        prov = Namespace("http://www.w3.org/ns/prov#")
        rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")

        def get_label_location(entity_uri: str) -> tuple[str, str]:
            """"指定されたエンティティのラベルとロケーションを取得する関数です。

            Args:
                entity_uri (str): エンティティのURI

            Returns:
                tuple[str, str]: ラベルとロケーション

            """
            entity_results = self.searcher.get_entity_info(entity_uri)
            entity_graph = entity_results.graph
            entity_subject = URIRef(entity_uri)

            label = entity_graph.value(subject=entity_subject, predicate=rdfs.label)
            location = None
            for _, _, activity_uri in entity_graph.triples((entity_subject, prov.wasUsedBy, None)):
                if "deleteActivity" in str(activity_uri):
                    location = "削除済み"

            if not location:
                location = entity_graph.value(subject=entity_subject, predicate=prov.atLocation)

            return label, location

        # activityタイプごとのpredicateとtype名の対応辞書（wasGeneratedBy側）
        activity_predicates = {
            "copyActivity": (prov.wasDerivedFrom, "コピー元"),
            "modifyActivity": (prov.wasRevisionOf, "編集元"),
            "compileActivity": (prov.wasDerivedFrom, "コンパイル元"),
            "exportActivity": (prov.wasDerivedFrom, "出力元"),
            "uploadActivity": (prov.wasDerivedFrom, "アップロード元"),
            "deleteActivity": (prov.wasDerivedFrom, "削除済み")
        }
        # wasUsedBy側
        used_activity_predicates = {
            "copyActivity": (prov.hadDerivation, "コピー先"),
            "modifyActivity": (prov.hadRevision, "編集先"),
            "compileActivity": (prov.hadDerivation, "コンパイル先"),
            "exportActivity": (prov.hadDerivation, "出力先"),
            "uploadActivity": (prov.hadDerivation, "アップロード先"),
            "deleteActivity": (prov.hadDerivedFrom, "削除済み")
        }

        graph = results.graph
        for s, p, o in graph.triples((None, rdfs.label, None)):
            label = str(o)
            break

        file_path = Path(label)
        file_name = file_path.name

        parts = label.split("/")
        subflow_name = "/".join(parts[2:4])

        related_files = []
        for subject in set(graph.subjects()):

            activities = list(graph.objects(subject=subject, predicate=prov.wasGeneratedBy))
            for activity in activities:
                for act_key, (predicate, type_name) in activity_predicates.items():
                    if act_key in activity:
                        entities = list(graph.objects(subject=subject, predicate=predicate))
                        for entity in entities:
                            related_file_info ={}
                            related_file_info["activity"] = activity
                            related_file_info["type"] = type_name
                            if str(entity).startswith("urn:collection"):
                                entity_results = self.searcher.get_entity_info(entity)
                                entity_graph = entity_results.graph
                                entity_subject = URIRef(entity)
                                for member in entity_graph.objects(subject=entity_subject, predicate=prov.hadMember):
                                    related_file_info ={}
                                    related_label, related_location = get_label_location(member)
                                    related_file_info["activity"] = activity
                                    related_file_info["type"] = type_name
                                    related_file_info["label"] = related_label
                                    related_file_info["location"] = related_location
                                    related_files.append(related_file_info)

                            elif act_key == "uploadActivity":
                                related_file_info["label"] = entity
                                related_file_info["location"] = entity
                                related_files.append(related_file_info)
                            else:
                                related_label, related_location = get_label_location(entity)
                                related_file_info["label"] = related_label
                                related_file_info["location"] = related_location
                                related_files.append(related_file_info)

            was_used_activities = list(graph.objects(subject=subject, predicate=prov.wasUsedBy))
            for activity in was_used_activities:
                for act_key, (predicate, type_name) in used_activity_predicates.items():
                    if act_key in activity:
                        entities = list(graph.objects(subject=subject, predicate=predicate))
                        for entity in entities:
                            related_file_info ={}
                            related_file_info["activity"] = activity
                            related_file_info["type"] = type_name
                            related_label, related_location = get_label_location(entity)
                            related_file_info["label"] = related_label
                            related_file_info["location"] = related_location
                            related_files.append(related_file_info)

            was_member_collections = list(graph.objects(subject=subject, predicate=prov.wasMemberOf))
            for collection in was_member_collections:
                collection_results = self.searcher.get_entity_info(collection)
                collection_graph = collection_results.graph
                collection_subject = URIRef(collection)
                collection_activities = list(collection_graph.objects(subject=collection_subject, predicate=prov.wasUsedBy))
                for activity in collection_activities:
                    for act_key, (predicate, type_name) in used_activity_predicates.items():
                        if act_key in activity:
                            entities = list(collection_graph.objects(subject=collection_subject, predicate=predicate))
                            for entity in entities:
                                related_file_info ={}
                                related_file_info["activity"] = activity
                                related_file_info["type"] = type_name
                                related_label, related_location = get_label_location(entity)
                                related_file_info["label"] = related_label
                                related_file_info["location"] = related_location
                                related_files.append(related_file_info)

        return subflow_name, FileInfo(file_name=file_name, file_path=label, link=location,
                                            related_files=related_files)