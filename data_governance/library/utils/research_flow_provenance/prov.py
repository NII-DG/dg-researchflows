"""来歴情報を管理するモジュールです。"""

import hashlib
import os
from pathlib import Path
from urllib.parse import urljoin

from rdflib import Namespace, URIRef
from library.utils.research_flow_provenance.output import OutputProvenance
from library.utils.research_flow_provenance.rdf import RDFStore, ProvenanceSearcher
from library.utils.research_flow_provenance.jsonld import generated_id
from library.utils.storage_provider.grdm.external import External

from .jsonld import ProvenanceEditor


def calculate_sha256(path: str) -> str:
    """ハッシュ値を計算する関数です。

    Args:
        path (str): ファイルのパス

    Returns:
        str: ハッシュ値

    """
    # SHA-256 ハッシュを計算
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()

class ProvenanceManager:
    """来歴情報を管理するためのクラスです。

    Attributes:
        class:
            ACTIVITY_BASE(str): アクティビティのURIのベース部分
            AGENT_BASE(str): エージェントのURIのベース部分
            FILE_COPY_BASE(str): コピーアクティビティのベース部分
            FILE_MODIFY_BASE(str): 編集アクティビティのベース部分
            FILE_COMPILE_BASE(str): コンパイルアクティビティのベース部分
            FILE_EXPORT_BASE(str): エクスポートアクティビティのベース部分
            FILE_UPLOAD_BASE(str): アップロードアクティビティのベース部分
            FILE_DELETE_BASE(str): 削除アクティビティのベース部分
            COLLECTION_EDIT_BASE(str): コレクション編集アクティビティのベース部分
            PROVENANCE_EDIT_BASE(str): プロビナンス編集アクティビティのベース部分

        instances:
            dispatch_map(dict):ディスパッチ用のマッピング情報
            token(str): GRDMトークン
            grdm_url(str): GRDMのベースURL
            project_id(str): GRDMのプロジェクトID
            rdf_store(str): RDFStoreクラスのインスタンス
            searcher(str): ProvenanceSearcherクラスのインスタンス
            output(str): OutputProvenanceクラスのインスタンス
            editor(str): ProvenanceEditorクラスのインスタンス
            external(str): Externalクラスのインスタンス
            excution_user(str): 実行ユーザーのURI
            grdm_file_info: GRDM上のファイル情報

    """
    ACTIVITY_BASE = "urn:activity:"
    AGENT_BASE = "urn:agent:"

    FILE_COPY_BASE = ACTIVITY_BASE + "copyActivity:"
    FILE_MODIFY_BASE = ACTIVITY_BASE + "modifyActivity:"
    FILE_COMPILE_BASE = ACTIVITY_BASE + "compileActivity:"
    FILE_EXPORT_BASE = ACTIVITY_BASE + "exportActivity:"
    FILE_UPLOAD_BASE = ACTIVITY_BASE + "uploadActivity:"
    FILE_DELETE_BASE = ACTIVITY_BASE + "deleteActivity:"
    COLLECTION_EDIT_BASE = ACTIVITY_BASE + "collectionEditActivity"
    PROVENANCE_EDIT_BASE = ACTIVITY_BASE + "provenanceEditActivity"

    def __init__(self, token: str, grdm_url: str, project_id: str):
        """クラスのインスタンスの初期化を行うメソッドです。

        Args:
            token (str): GRDMトークン
            grdm_url (str): GRDMのベースURL
            project_id (str): GRDMのプロジェクトID

        """
        self.dispatch_map = {
            "File Copy": self._handle_file_copy,
            "File Modify": self._handle_file_modify,
            "File Compile": self._handle_file_compile,
            "File Export": self._handle_file_export,
            "File Upload": self._handle_file_upload,
            "File Delete": self._handle_file_delete,
            "Collection Edit": self._handle_collection_edit,
            "Provenance Edit": self._handle_provenance_edit,
            "Delete Activity": self._handle_delete_activity
        }

        self.token =token
        self.grdm_url = grdm_url
        self.project_id = project_id

        self.rdf_store = RDFStore()
        self.searcher = ProvenanceSearcher(self.rdf_store)
        self.output = OutputProvenance(self.searcher)
        self.editor = ProvenanceEditor()
        self.external = External()

        self.rdf_store.load_graph()
        self.excution_user = self._get_execution_user()

    def _get_execution_user(self):
        """実行ユーザーの情報を取得する関数です。"""

        response = self.external.get_user_info(self.grdm_url, self.token)

        user_id = response['data']['id']
        agent_uri = self.AGENT_BASE + user_id

        result = self.searcher.get_excution_user(agent_uri)

        if result:
            return result
        else:
            agent_type=["prov:Agent", "prov:Person"]
            user_name = str(response['data']['attributes']['full_name'])
            agent_uri =self.editor.create_agent(agent_uri, agent_type, user_name)
            return agent_uri

    async def handle(self, activity_type: str, *args, **kwargs):
        """各アクティビティのハンドル関数の入り口となる関数です。

        Args:
            activity_type (str): アクティビティのタイプ

        Returns:
            Any: ハンドラー関数を実行する

        """
        self.grdm_file_info = await self.external.list_(self.token, self.grdm_url, self.project_id, "osfstorage/data/")

        handler = self.dispatch_map.get(activity_type)

        return handler(activity_type, *args, **kwargs)

    def _handle_file_copy(self, activity_type: str, copied_files: dict):
        """コピーアクティビティを処理するための関数です。

        Args:
            activity_type (str): アクティビティタイプ（コピー）
            copied_files (dict): コピー元、コピー先ファイル

        Raises:
            FileNotFoundError: 対処のファイルがGRDM上に存在しない場合のエラーです。

        """
        base_id = self.FILE_COPY_BASE
        activity_id = generated_id(base_id)

        updated_files = []
        src_entities =[]
        for dst_file, src_file in copied_files.items():
            # コピー元の処理
            convert_path = self.convert_grdm_path(src_file)
            if convert_path in self.grdm_file_info:
                src_link = self.convert_grdm_link(self.grdm_file_info[convert_path])
                updated_files.append(src_link)
                src_uri = self.searcher.get_file_entity(src_link)
                if not src_uri:
                    src_value = calculate_sha256(src_file)
                    src_uri = self.editor.create_entity(convert_path, src_link, src_value)
            else:
                raise FileNotFoundError(f"{convert_path}がGRDMに存在しません。")
            src_entities.append(src_uri)

            #　コピー先の処理
            dst_hash = calculate_sha256(dst_file)
            convert_path = self.convert_grdm_path(dst_file)
            if convert_path in self.grdm_file_info:
                dst_link = self.convert_grdm_link(self.grdm_file_info[convert_path])
                self.editor.create_entity(convert_path, dst_link, dst_hash, activity_id, src_uri, self.excution_user)
                updated_files.append(dst_link)
            else:
                raise FileNotFoundError(f"{convert_path}がGRDMに存在しません。")

        # アクティビティ作成
        self.editor.create_activity(activity_id, activity_type, src_entities, self.excution_user)
        #再読み込み
        self.rdf_store.reload()

        self.output.write(updated_files)

    def _handle_file_modify(self, activity_type: str, src_file:str, dst_file:str):
        """修正アクティビティを処理するための関数"""
        base_id = self.FILE_MODIFY_BASE
        activity_id = generated_id(base_id)

        # この部分は共通化する？
        updated_files = []
        src_entities =[]

        # 修正元の処理
        convert_path = self.convert_grdm_path(src_file)
        if convert_path in self.grdm_file_info:
            src_link = self.convert_grdm_link(self.grdm_file_info[convert_path])
            updated_files.append(src_link)
            src_uri = self.searcher.get_file_entity(src_link)
            if not src_uri:
                src_value = calculate_sha256(src_file)
                src_uri = self.editor.create_entity(convert_path, src_link, src_value)
        else:
            raise FileNotFoundError(f"{convert_path}がGRDMに存在しない")
        src_entities.append(src_uri)

        #　修正先の処理
        dst_hash = calculate_sha256(dst_file)
        convert_path = self.convert_grdm_path(dst_file)
        if convert_path in self.grdm_file_info:
            dst_link = self.convert_grdm_link(self.grdm_file_info[convert_path])
            self.editor.create_entity(convert_path, dst_link, dst_hash, activity_id, src_uri, self.excution_user)
            updated_files.append(dst_link)
        else:
            raise FileNotFoundError(f"{convert_path}がGRDMに存在しない")

        # アクティビティ作成
        self.editor.create_activity(activity_id, activity_type, src_entities, self.excution_user)

        self.rdf_store.reload()

        self.output.write(updated_files)

    def _handle_file_compile(self, activity_type: str, dst_file: str, tex_list:list=None, argument_list:list=None, figure_list:list=None, agent_info:list=None):
        """コンパイルアクティビティを処理するための関数"""
        base_id = self.FILE_COMPILE_BASE
        activity_id = generated_id(base_id)

        updated_files = []
        src_entities =[]
        for src_file in tex_list:
            # 草稿ファイルの処理
            convert_path = self.convert_grdm_path(src_file)
            if convert_path in self.grdm_file_info:
                src_link = self.convert_grdm_link(self.grdm_file_info[convert_path])
                updated_files.append(src_link)
                src_uri = self.searcher.get_file_entity(src_link)
                if not src_uri:
                    src_value = calculate_sha256(src_file)
                    src_uri = self.editor.create_entity(convert_path, src_link, src_value)
            else:
                raise FileNotFoundError(f"{convert_path}がGRDMに存在しない")
            src_entities.append(src_uri)

        argument_entity = []
        for src_file in argument_list:
            # 論拠データの処理
            convert_path = self.convert_grdm_path(src_file)
            if convert_path in self.grdm_file_info:
                src_link = self.convert_grdm_link(self.grdm_file_info[convert_path])
                updated_files.append(src_link)
                src_uri = self.searcher.get_file_entity(src_link)
                if not src_uri:
                    src_value = calculate_sha256(src_file)
                    src_uri = self.editor.create_entity(convert_path, src_link, src_value)
            else:
                raise FileNotFoundError(f"{convert_path}がGRDMに存在しない")
            argument_entity.append(src_uri)
        argument_collections = self.editor.create_collection(members=argument_entity, label="argument_data_collection")
        src_entities.append(argument_collections)

        figure_entity = []
        for src_file in figure_list:
            # 論拠データの処理
            convert_path = self.convert_grdm_path(src_file)
            if convert_path in self.grdm_file_info:
                src_link = self.convert_grdm_link(self.grdm_file_info[convert_path])
                updated_files.append(src_link)
                src_uri = self.searcher.get_file_entity(src_link)
                if not src_uri:
                    src_value = calculate_sha256(src_file)
                    src_uri = self.editor.create_entity(convert_path, src_link, src_value)
            else:
                raise FileNotFoundError(f"{convert_path}がGRDMに存在しない")
            figure_entity.append(src_uri)
        figure_collections = self.editor.create_collection(members=figure_entity, label="figure_collection")
        src_entities.append(figure_collections)

        agent_list = []
        agent_list.append(self.excution_user)
        if agent_info:
            for agent in agent_info:
                agent_uri = self.AGENT_BASE + agent["agent_name"]
                agent_list.append(agent_uri)
                self.editor.create_agent(agent_uri, agent["agent_type"], agent["agent_name"])

        #　コンパイル先の処理
        dst_hash = calculate_sha256(dst_file)
        convert_path = self.convert_grdm_path(dst_file)
        if convert_path in self.grdm_file_info:
            dst_link = self.convert_grdm_link(self.grdm_file_info[convert_path])
            self.editor.create_entity(convert_path, dst_link, dst_hash, activity_id, src_entities, agent_list)
            updated_files.append(dst_link)
        else:
            raise FileNotFoundError(f"{convert_path}がGRDMに存在しない")

        # アクティビティ作成
        self.editor.create_activity(activity_id, activity_type, src_entities, agent_list)

        self.rdf_store.reload()

        self.output.write(updated_files)

    def _handle_file_export(self, activity_type: str, dst_file: str, src_files: list, agent_info:list=None):
        """エクスポートアクティビティを処理するための関数"""
        base_id = self.FILE_EXPORT_BASE
        activity_id = generated_id(base_id)

        # この部分は共通化する？
        updated_files = []
        src_entities =[]
        for src_file in src_files:
            # エクスポート元の処理
            convert_path = self.convert_grdm_path(src_file)
            if convert_path in self.grdm_file_info:
                src_link = self.convert_grdm_link(self.grdm_file_info[convert_path])
                updated_files.append(src_link)
                src_uri = self.searcher.get_file_entity(src_link)
                if not src_uri:
                    src_value = calculate_sha256(src_file)
                    src_uri = self.editor.create_entity(convert_path, src_link, src_value)
            else:
                raise FileNotFoundError(f"{convert_path}がGRDMに存在しない")
            src_entities.append(src_uri)

        agent_list = []
        agent_list.append(self.excution_user)
        if agent_info:
            for agent in agent_info:
                agent_uri = self.AGENT_BASE + agent["agent_name"]
                agent_list.append(agent_uri)
                self.editor.create_agent(agent_uri, agent["agent_type"], agent["agent_name"])

        #　エクスポート先の処理
        dst_hash = calculate_sha256(dst_file)
        convert_path = self.convert_grdm_path(dst_file)
        if convert_path in self.grdm_file_info:
            dst_link = self.convert_grdm_link(self.grdm_file_info[convert_path])
            self.editor.create_entity(convert_path, dst_link, dst_hash, activity_id, src_uri, agent_list)
            updated_files.append(dst_link)
        else:
            raise FileNotFoundError(f"{convert_path}がGRDMに存在しない")

        # アクティビティ作成
        self.editor.create_activity(activity_id, activity_type, src_entities, agent_list)

        self.rdf_store.reload()

        self.output.write(updated_files)

    def _handle_file_upload(self, activity_type: str, upload_files: dict):
        """アップロードアクティビティを処理するための関数"""
        base_id = self.FILE_UPLOAD_BASE
        activity_id = generated_id(base_id)

        updated_files = []
        src_list =[]
        for dst_path, src_link in upload_files.items():
            #　アップロード先のパス
            dst_hash = calculate_sha256(dst_path)
            convert_path = self.convert_grdm_path(dst_path)
            if convert_path in self.grdm_file_info:
                dst_link = self.convert_grdm_link(self.grdm_file_info[convert_path])
                self.editor.create_entity(convert_path, dst_link, dst_hash, activity_id, src_link, self.excution_user)
                updated_files.append(dst_link)
            else:
                raise FileNotFoundError(f"{convert_path}がGRDMに存在しません。")

            src_list.append(src_link)

        # アクティビティ作成
        self.editor.create_activity(activity_id, activity_type, src_list, self.excution_user)
        #再読み込み
        self.rdf_store.reload()

        self.output.write(updated_files)

    def _handle_file_delete(self, activity_type: str, deleted_files: list):
        """削除アクティビティを処理するための関数"""
        base_id = self.FILE_DELETE_BASE
        activity_id = generated_id(base_id)

        updated_files = []
        # 削除済みファイルの探索
        for deleted_file in deleted_files:
            convert_path = self.convert_grdm_path(deleted_file)
            if convert_path in self.grdm_file_info:
                delete_link = self.convert_grdm_link(self.grdm_file_info[convert_path])
                delete_uri = self.searcher.get_file_entity_list(delete_link)
                if not delete_uri :
                    raise FileNotFoundError(f"{convert_path}のEntityが存在しない")
                updated_files.extend(delete_uri)
            else:
                raise FileNotFoundError(f"{convert_path}がGRDMに存在しない")

        # アクティビティ作成
        self.editor.create_activity(activity_id, activity_type, updated_files, self.excution_user)

        # self.rdf_store.reload()

        # self.output.write(updated_files)

    def _handle_collection_edit(self, activity_type: str, collection_info: list):
        """コレクション編集アクティビティを処理するための関数"""
        base_id = self.COLLECTION_EDIT_BASE

        updated_files = []
        for collection in collection_info:
            activity_id = generated_id(base_id)
            self.editor.edit_collection(collection["collection_id"], activity_id, collection["new_member"])
            updated_files = list(set(updated_files + collection["old_member"] + collection["new_member"]))
            src_entities =[collection["collection_id"]]

            # アクティビティ作成
            self.editor.create_activity(activity_id, activity_type, src_entities, self.excution_user, old_provenances=collection["old_member"])

        self.rdf_store.reload()

        self.output.write(updated_files)

    def _handle_provenance_edit(self, activity_type: str, entity_id: str, old_provenance: list, new_provenance: list, comment: str=""):
        """来歴編集アクティビティを処理するための関数"""
        base_id = self.COLLECTION_EDIT_BASE

        activity_id = generated_id(base_id)
        self.editor.edit_entity(entity_id, activity_id, new_provenance)

        # アクティビティ作成
        self.editor.create_activity(activity_id, activity_type, entity_id, self.excution_user, old_provenance)

        self.rdf_store.reload()
        updated_files = list(set(old_provenance + new_provenance))
        self.output.write(updated_files)

    def _handle_delete_activity(self, activity_type:str, activity_uri: str, update_files: list):
        """アクティビティを削除する際の関数です。"""

        results = self.searcher.get_activity_info(activity_uri)
        prov = Namespace("http://www.w3.org/ns/prov#")
        activity_graph = results.graph
        activity_subject = URIRef(activity_uri)
        generated_entity = activity_graph.value(subject=activity_subject, predicate=prov.generated)

        self.editor.delete_activity(activity_uri)

        src_entities = self.editor.edit_entity(str(generated_entity))

        for entity in src_entities:
            if str(entity).startswith("urn:collection"):
                self.editor.delete_entity(entity)

        #再読み込み
        self.rdf_store.reload()
        file_links = []
        for file in update_files:
            convert_path = self.convert_grdm_path(file)
            if convert_path in self.grdm_file_info:
                file_link = self.convert_grdm_link(self.grdm_file_info[convert_path])
                file_links.append(file_link)

        self.output.write(file_links)

    # def check_entity_exists(self, file_paths:list):
    #     """指定されたファイルパスのファイルのエンティティが存在するかを確認する関数。"""

    #     results = []
    #     for file in file_paths:
    #         result = self.searcher.get_file_entity(file)
    #         if result:
    #             results.append(result)
    #         else:
    #             editor = ProvenanceEditor()
    #             hash_value = calculate_sha256(file)
    #             path = file.split("data", 1)[1]
    #             path = os.path.join("osfstorage/data", path)
    #             if path in self.grdm_file_info:
    #                 value = self.grdm_file_info[path]
    #             else:
    #                 raise Exception("ファイルなし")
    #             location = os.path.join(self.grdm_url, self.project_id, "files/osfstorage", value)
    #             results.append(editor.create_entity(path, location, hash_value))

    #     return results

    def convert_grdm_path(self, path):
        """GRDM用のパスに変換する関数です。"""
        # これpath_configとかにいれる？
        base_path = "/home/jovyan"
        osfstorage = "osfstorage"

        trimmed = os.path.relpath(path, base_path)

        return os.path.join(osfstorage, trimmed)

    def convert_grdm_link(self, file_id):
        """GRDMのファイル閲覧ページ用のlinkを作成する。"""
        # これpath_configとかにいれる？
        files = "files"
        osfstorage = "osfstorage"

        path = "/".join([self.project_id, files, osfstorage, file_id])
        return urljoin(self.grdm_url + "/", path)

    def check_file_exist(self, dir_path: str):
        """来歴情報を記述したファイルが存在するかを確認する関数です。"""

        base_path = "/home/jovyan"
        osfstorage = "osfstorage"

        base_trimmed = os.path.relpath(dir_path, base_path)
        results = self.searcher.get_all_entities(os.path.join(osfstorage, base_trimmed))

        all_files = {}
        error_files = {}
        for label, ids in results.items():
            osf_trimmed = os.path.relpath(label, osfstorage)
            file_path = os.path.join(base_path, osf_trimmed)

            all_files[file_path] = ids
            if not os.path.exists(file_path):
                error_files[file_path] = ids

        return all_files, error_files

    def get_activity_info(self, uri_list: list):
        """指定されたエンティティの関連情報を取得する関数です。"""

        prov = Namespace("http://www.w3.org/ns/prov#")
        rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")

        src_files = {}
        for uri in uri_list:
            results = self.searcher.get_entity_info(uri)

            if len(results) > 0:
                prov = Namespace("http://www.w3.org/ns/prov#")
                entity_graph = results.graph
                entity_subject = URIRef(uri)
                location = entity_graph.value(subject=entity_subject, predicate=prov.atLocation)
                subflow, info = self.output.set_file_info(results, location)

                for info in info.related_files:
                    activity_key = str(info["activity"])
                    activity_dict = src_files.setdefault(activity_key, {})
                    if not activity_dict:
                        activity_dict["type"] = info["type"]

                    activity_dict.setdefault("label", []).append(str(info["label"]))

        return src_files
