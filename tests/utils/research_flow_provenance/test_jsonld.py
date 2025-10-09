"""jsonld.pyファイルのテストを記述したモジュールです。"""

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import uuid

import unittest.mock as mock
import pytest
from unittest import mock
from data_governance.library.utils.research_flow_provenance.jsonld import generated_id, ProvenanceEditor

def test_generated_id():
    """test_generated_idの正常系テスト"""
    fake_uuid = uuid.UUID("12345678-1234-5678-1234-567812345678")

    with mock.patch("data_governance.library.utils.research_flow_provenance.jsonld.uuid.uuid4", return_value=fake_uuid):
        result = generated_id("base_id")

    assert result == "base_id-12345678-1234-5678-1234-567812345678"

class TestProvenanceEditor:
    """ProvenanceEditorクラスをテストするクラスです。"""

    def test__constructor_1(self):
        """コンストラクタの正常系テスト（すべてのファイルが存在する場合）"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan',
        }

        with mock.patch.dict(os.environ, test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        assert editor.entity_file == "/home/jovyan/data_governance/researchflow/test_env/entity.jsonld"
        assert editor.activity_file == "/home/jovyan/data_governance/researchflow/test_env/activity.jsonld"
        assert editor.agent_file == "/home/jovyan/data_governance/researchflow/test_env/agent.jsonld"

    def test__constructor_2(self):
        """entity.jsonld が存在しない場合、テンプレートからコピーされるか"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan',
        }

        # os.path.exists の返り値（順に entity, activity, agent, template の存在）
        with mock.patch.dict(os.environ, test_env):
            with mock.patch("os.path.exists", side_effect=[False, True, True, True]):
                with mock.patch("os.makedirs") as makedirs_mock:
                    with mock.patch("shutil.copy") as copy_mock:
                        ProvenanceEditor()
                        copy_mock.assert_called_with(
                            "/home/jovyan/data_governance/library/utils/research_flow_provenance/template.jsonld",
                            "/home/jovyan/data_governance/researchflow/test_env/entity.jsonld"
                        )

    def test__constructor_3(self):
        """activity.jsonld が存在しない場合、テンプレートからコピーされるか"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan',
        }

        with mock.patch.dict(os.environ, test_env):
            with mock.patch("os.path.exists", side_effect=[True, False, True, True]):
                with mock.patch("os.makedirs") as makedirs_mock:
                    with mock.patch("shutil.copy") as copy_mock:
                        ProvenanceEditor()
                        copy_mock.assert_called_with(
                            "/home/jovyan/data_governance/library/utils/research_flow_provenance/template.jsonld",
                            "/home/jovyan/data_governance/researchflow/test_env/activity.jsonld"
                        )

    def test__constructor_4(self):
        """agent.jsonld が存在しない場合、テンプレートからコピーされるか"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan',
        }

        with mock.patch.dict(os.environ, test_env):
            with mock.patch("os.path.exists", side_effect=[True, True, False, True]):
                with mock.patch("os.makedirs") as makedirs_mock:
                    with mock.patch("shutil.copy") as copy_mock:
                        ProvenanceEditor()
                        copy_mock.assert_called_with(
                            "/home/jovyan/data_governance/library/utils/research_flow_provenance/template.jsonld",
                            "/home/jovyan/data_governance/researchflow/test_env/agent.jsonld"
                        )

    def test_create_activity_all_args(self):
        """create_activityを全引数ありで実行するテストケースです"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        # ファイル存在は正常とする
        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        # モック対象：open, json.load, json.dump
        mock_activity_data = {"@graph": []}

        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_activity_data))) as mock_file:
            with mock.patch("json.load", return_value=mock_activity_data) as mock_json_load:
                with mock.patch("json.dump") as mock_json_dump:
                    # 引数全部ありパターン
                    activity_id = "urn:activity:test_activity"
                    activity_type = "Test Activity"
                    used_entities = ["urn:entity:1", "urn:entity:2"]
                    agent_id = ["urn:agent:1", "urn:agent:2"]
                    comment = "これはテストのコメントです"
                    old_provenances = ["urn:entity:old1", "urn:entity:old2"]

                    editor.create_activity(
                        activity_id=activity_id,
                        activity_type=activity_type,
                        used_entities=used_entities,
                        agent_id=agent_id,
                        comment=comment,
                        old_provenances=old_provenances
                    )

                    # json.dumpに渡された辞書（activity_data）の中身をチェック
                    args, kwargs = mock_json_dump.call_args
                    dumped_data = args[0]  # json.dumpの第一引数が書き込むデータ

                    # @graph に新しいactivityが追加されているはず
                    new_activity = dumped_data["@graph"][-1]

                    assert new_activity["@id"] == activity_id
                    assert new_activity["label"] == activity_type
                    assert new_activity["prov:used"] == [{"@id": e} for e in used_entities]
                    assert new_activity["prov:wasAssociatedWith"] == [{"@id": e} for e in agent_id]
                    assert new_activity["comment"] == comment

                    # old_provenances が prov:qualifiedUsage に反映されているか
                    qualified_usage = new_activity.get("prov:qualifiedUsage", [])
                    assert len(qualified_usage) == len(old_provenances)
                    for usage, old_id in zip(qualified_usage, old_provenances):
                        assert usage["@type"] == "prov:Usage"
                        assert usage["label"] == "old provenance"
                        assert usage["prov:entity"] == old_id
                    print(f"kekka{ProvenanceEditor.__module__}")

    def test_create_activity_without_comment(self):
        """create_activityをコメント引数なしで実行するテストケースです"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        mock_activity_data = {"@graph": []}

        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_activity_data))) as mock_file:
            with mock.patch("json.load", return_value=mock_activity_data):
                with mock.patch("json.dump") as mock_json_dump:
                    activity_id = "urn:activity:002"
                    activity_type = "Test Activity Without Comment"
                    used_entities = ["urn:entity:010"]
                    agent_id = "urn:agent:010"
                    old_provenances = ["urn:entity:old10"]

                    # commentは渡さない（デフォルトNone）
                    editor.create_activity(
                        activity_id=activity_id,
                        activity_type=activity_type,
                        used_entities=used_entities,
                        agent_id=agent_id,
                        old_provenances=old_provenances
                    )

                    args, _ = mock_json_dump.call_args
                    dumped_data = args[0]
                    new_activity = dumped_data["@graph"][-1]

                    assert new_activity["@id"] == activity_id
                    assert new_activity["label"] == activity_type
                    assert new_activity["prov:used"] == [{"@id": e} for e in used_entities]
                    assert new_activity["prov:wasAssociatedWith"] == [{"@id": agent_id}]

                    # commentキーは存在しないことを確認
                    assert "comment" not in new_activity

                    # old_provenancesは反映される
                    qualified_usage = new_activity.get("prov:qualifiedUsage", [])
                    assert len(qualified_usage) == len(old_provenances)

    def test_create_activity_without_old_provenances(self):
        """create_activityをold_provenance引数なしで実行するテストケースです"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        mock_activity_data = {"@graph": []}

        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_activity_data))) as mock_file:
            with mock.patch("json.load", return_value=mock_activity_data):
                with mock.patch("json.dump") as mock_json_dump:
                    activity_id = "urn:activity:003"
                    activity_type = "Test Activity Without Old Provenances"
                    used_entities = ["urn:entity:020"]
                    agent_id = "urn:agent:020"
                    comment = "コメントあり"

                    # old_provenancesは渡さない（デフォルトNone）
                    editor.create_activity(
                        activity_id=activity_id,
                        activity_type=activity_type,
                        used_entities=used_entities,
                        agent_id=agent_id,
                        comment=comment
                    )

                    args, _ = mock_json_dump.call_args
                    dumped_data = args[0]
                    new_activity = dumped_data["@graph"][-1]

                    assert new_activity["@id"] == activity_id
                    assert new_activity["label"] == activity_type
                    assert new_activity["prov:used"] == [{"@id": e} for e in used_entities]
                    assert new_activity["prov:wasAssociatedWith"] == [{"@id": agent_id}]

                    # commentは存在する
                    assert new_activity["comment"] == comment

                    # old_provenancesが無いので prov:qualifiedUsage はないはず
                    assert "prov:qualifiedUsage" not in new_activity

    def test_create_activity_str_agent(self):
        """create_activityをagent_id引数が文字列で実行するテストケースです"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        mock_activity_data = {"@graph": []}

        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_activity_data))) as mock_file:
            with mock.patch("json.load", return_value=mock_activity_data):
                with mock.patch("json.dump") as mock_json_dump:
                    activity_id = "urn:activity:003"
                    activity_type = "Test Activity Without Old Provenances"
                    used_entities = ["urn:entity:020"]
                    agent_id = "urn:agent:020"
                    comment = "コメントあり"

                    # old_provenancesは渡さない（デフォルトNone）
                    editor.create_activity(
                        activity_id=activity_id,
                        activity_type=activity_type,
                        used_entities=used_entities,
                        agent_id=agent_id
                    )

                    args, _ = mock_json_dump.call_args
                    dumped_data = args[0]
                    new_activity = dumped_data["@graph"][-1]

                    assert new_activity["@id"] == activity_id
                    assert new_activity["label"] == activity_type
                    assert new_activity["prov:used"] == [{"@id": e} for e in used_entities]
                    assert new_activity["prov:wasAssociatedWith"] == [{"@id": agent_id}]

    def test_create_activity_file_read_fail(self):
        """ファイルの読み込みに失敗する場合のテストケースです"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        # openは普通にモックしておく
        m_open = mock.mock_open(read_data="invalid json")

        with mock.patch("builtins.open", m_open):
            # json.loadでJSONDecodeErrorを発生させる
            with mock.patch("json.load", side_effect=json.JSONDecodeError("Expecting value", "doc", 0)):
                with pytest.raises(RuntimeError) as excinfo:
                    editor.create_activity(
                        activity_id="urn:activity:error",
                        activity_type="Error Activity",
                        used_entities=["urn:entity:error"],
                        agent_id="urn:agent:error"
                    )

                assert "読み込みに失敗しました" in str(excinfo.value)

    def test_create_activity_file_write_fail(self):
        """ファイルの書き込みに失敗する場合のテストケースです。"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        mock_activity_data = {"@graph": []}

        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_activity_data))):
            with mock.patch("json.load", return_value=mock_activity_data):
                # json.dump に side_effect を直接設定
                with mock.patch("json.dump", side_effect=IOError("書き込みエラー発生")):
                    with pytest.raises(RuntimeError) as excinfo:
                        editor.create_activity(
                            activity_id="urn:activity:write_error",
                            activity_type="Write Error Activity",
                            used_entities=["urn:entity:write_error"],
                            agent_id="urn:agent:write_error"
                        )

                    assert "書き込みに失敗しました" in str(excinfo.value)

    def test_create_entity_all_args(self):
        """create_entityを全引数ありで実行するテストケースです"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        # モック読み込みデータ
        mock_entity_data = {"@graph": []}

        # generated_idはUUIDが入るため固定値にモック
        fake_entity_id = "urn:entity:test-uuid-1234"
        with mock.patch("data_governance.library.utils.research_flow_provenance.jsonld.generated_id", return_value=fake_entity_id):
            with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_entity_data))) as m_open:
                with mock.patch("json.load", return_value=mock_entity_data):
                    with mock.patch("json.dump") as mock_json_dump:
                        dst_path = "/path/to/dst_file.txt"
                        location = "urn:location:test"
                        hash_value = "deadbeef123456"
                        activity_id = "copyActivity:xyz"
                        src_path = ["src1.txt", "src2.txt"]
                        agents = ["urn:agent1", "urn:agent2"]

                        entity_id = editor.create_entity(
                            dst_path=dst_path,
                            location=location,
                            hash_value=hash_value,
                            activity_id=activity_id,
                            src_path=src_path,
                            agents=agents
                        )

                        # 戻り値はモックIDと同じ
                        assert entity_id == fake_entity_id

                        args, _ = mock_json_dump.call_args
                        dumped_data = args[0]
                        new_entity = dumped_data["@graph"][-1]

                        # id, type, label の基本情報チェック
                        assert new_entity["@id"] == fake_entity_id
                        assert new_entity["@type"] == "prov:Entity"
                        assert new_entity["label"] == dst_path

                        # atLocation
                        assert new_entity["prov:atLocation"]["@id"] == location

                        # checksum
                        assert new_entity["dcat:checksum"]["hashValue"] == hash_value
                        assert new_entity["dcat:checksum"]["checksumAlgorithm"] == "SHA-256"

                        # modifyActivity以外
                        assert "prov:wasDerivedFrom" in new_entity
                        assert new_entity["prov:wasDerivedFrom"] == [{"@id": p} for p in src_path]

                        # wasGeneratedBy
                        assert new_entity["prov:wasGeneratedBy"]["@id"] == activity_id

                        # agents
                        assert "prov:wasAttributedTo" in new_entity
                        assert new_entity["prov:wasAttributedTo"] == [{"@id": a} for a in agents]

    def test_create_entity_without_some_args(self):
        """create_entityをsrc_path,activity_id,agents引数なしで実行するテストケースです"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        # モック読み込みデータ
        mock_entity_data = {"@graph": []}

        # generated_idはUUIDが入るため固定値にモック
        fake_entity_id = "urn:entity:test-uuid-1234"
        with mock.patch("data_governance.library.utils.research_flow_provenance.jsonld.generated_id", return_value=fake_entity_id):
            with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_entity_data))) as m_open:
                with mock.patch("json.load", return_value=mock_entity_data):
                    with mock.patch("json.dump") as mock_json_dump:
                        dst_path = "/path/to/dst_file.txt"
                        location = "urn:location:test"
                        hash_value = "deadbeef123456"

                        entity_id = editor.create_entity(
                            dst_path=dst_path,
                            location=location,
                            hash_value=hash_value,
                        )

                        # 戻り値はモックIDと同じ
                        assert entity_id == fake_entity_id

                        args, _ = mock_json_dump.call_args
                        dumped_data = args[0]
                        new_entity = dumped_data["@graph"][-1]

                        # id, type, label の基本情報チェック
                        assert new_entity["@id"] == fake_entity_id
                        assert new_entity["@type"] == "prov:Entity"
                        assert new_entity["label"] == dst_path

                        # atLocation
                        assert new_entity["prov:atLocation"]["@id"] == location

                        # checksum
                        assert new_entity["dcat:checksum"]["hashValue"] == hash_value
                        assert new_entity["dcat:checksum"]["checksumAlgorithm"] == "SHA-256"

                        # src_pathなし
                        assert "prov:wasDerivedFrom" not in new_entity
                        assert "prov:wasRevisionOf" not in new_entity

                        # Activityなし
                        assert "prov:wasGeneratedBy" not in new_entity

                        # agents
                        assert "prov:wasAttributedTo" not in new_entity

    def test_create_entity_with_str_src_path(self):
        """create_entityをsrc_pathが文字列の引数で実行するテストケースです"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        # モック読み込みデータ
        mock_entity_data = {"@graph": []}

        # generated_idはUUIDが入るため固定値にモック
        fake_entity_id = "urn:entity:test-uuid-1234"
        with mock.patch("data_governance.library.utils.research_flow_provenance.jsonld.generated_id", return_value=fake_entity_id):
            with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_entity_data))) as m_open:
                with mock.patch("json.load", return_value=mock_entity_data):
                    with mock.patch("json.dump") as mock_json_dump:
                        dst_path = "/path/to/dst_file.txt"
                        location = "urn:location:test"
                        hash_value = "deadbeef123456"
                        activity_id = "copyActivity:xyz"
                        src_path = "src1.txt"
                        agents = ["urn:agent1", "urn:agent2"]

                        entity_id = editor.create_entity(
                            dst_path=dst_path,
                            location=location,
                            hash_value=hash_value,
                            activity_id=activity_id,
                            src_path=src_path,
                            agents=agents
                        )

                        # 戻り値はモックIDと同じ
                        assert entity_id == fake_entity_id

                        args, _ = mock_json_dump.call_args
                        dumped_data = args[0]
                        new_entity = dumped_data["@graph"][-1]

                        # id, type, label の基本情報チェック
                        assert new_entity["@id"] == fake_entity_id
                        assert new_entity["@type"] == "prov:Entity"
                        assert new_entity["label"] == dst_path

                        # atLocation
                        assert new_entity["prov:atLocation"]["@id"] == location

                        # checksum
                        assert new_entity["dcat:checksum"]["hashValue"] == hash_value
                        assert new_entity["dcat:checksum"]["checksumAlgorithm"] == "SHA-256"

                        # modifyActivity以外
                        assert "prov:wasDerivedFrom" in new_entity
                        assert new_entity["prov:wasDerivedFrom"] == [{"@id": src_path}]

                        # wasGeneratedBy
                        assert new_entity["prov:wasGeneratedBy"]["@id"] == activity_id

                        # agents
                        assert "prov:wasAttributedTo" in new_entity
                        assert new_entity["prov:wasAttributedTo"] == [{"@id": a} for a in agents]

    def test_create_entity_with_modify_activity(self):
        """create_entityをactivity_idにmodifyActivityを含む引数で実行するテストケースです"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        # モック読み込みデータ
        mock_entity_data = {"@graph": []}

        # generated_idはUUIDが入るため固定値にモック
        fake_entity_id = "urn:entity:test-uuid-1234"
        with mock.patch("data_governance.library.utils.research_flow_provenance.jsonld.generated_id", return_value=fake_entity_id):
            with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_entity_data))) as m_open:
                with mock.patch("json.load", return_value=mock_entity_data):
                    with mock.patch("json.dump") as mock_json_dump:
                        dst_path = "/path/to/dst_file.txt"
                        location = "urn:location:test"
                        hash_value = "deadbeef123456"
                        activity_id = "modifyActivity:xyz"
                        src_path = ["src1.txt", "src2.txt"]
                        agents = ["agent1", "agent2"]

                        entity_id = editor.create_entity(
                            dst_path=dst_path,
                            location=location,
                            hash_value=hash_value,
                            activity_id=activity_id,
                            src_path=src_path,
                            agents=agents
                        )

                        # 戻り値はモックIDと同じ
                        assert entity_id == fake_entity_id

                        args, _ = mock_json_dump.call_args
                        dumped_data = args[0]
                        new_entity = dumped_data["@graph"][-1]

                        # id, type, label の基本情報チェック
                        assert new_entity["@id"] == fake_entity_id
                        assert new_entity["@type"] == "prov:Entity"
                        assert new_entity["label"] == dst_path

                        # atLocation
                        assert new_entity["prov:atLocation"]["@id"] == location

                        # checksum
                        assert new_entity["dcat:checksum"]["hashValue"] == hash_value
                        assert new_entity["dcat:checksum"]["checksumAlgorithm"] == "SHA-256"

                        # src_pathがリストなのでwasRevisionOfがある（activity_idに"modifyActivity"含むので）
                        assert "prov:wasRevisionOf" in new_entity
                        assert new_entity["prov:wasRevisionOf"] == [{"@id": p} for p in src_path]

                        # wasGeneratedBy
                        assert new_entity["prov:wasGeneratedBy"]["@id"] == activity_id

                        # agents
                        assert "prov:wasAttributedTo" in new_entity
                        assert new_entity["prov:wasAttributedTo"] == [{"@id": a} for a in agents]

    def test_create_entity_with_str_agents(self):
        """create_entityをagents引数が文字列で実行するテストケースです"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        # モック読み込みデータ
        mock_entity_data = {"@graph": []}

        # generated_idはUUIDが入るため固定値にモック
        fake_entity_id = "urn:entity:test-uuid-1234"
        with mock.patch("data_governance.library.utils.research_flow_provenance.jsonld.generated_id", return_value=fake_entity_id):
            with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_entity_data))) as m_open:
                with mock.patch("json.load", return_value=mock_entity_data):
                    with mock.patch("json.dump") as mock_json_dump:
                        dst_path = "/path/to/dst_file.txt"
                        location = "urn:location:test"
                        hash_value = "deadbeef123456"
                        activity_id = "modifyActivity:xyz"
                        src_path = ["src1.txt", "src2.txt"]
                        agents = "agent1"

                        entity_id = editor.create_entity(
                            dst_path=dst_path,
                            location=location,
                            hash_value=hash_value,
                            activity_id=activity_id,
                            src_path=src_path,
                            agents=agents
                        )

                        # 戻り値はモックIDと同じ
                        assert entity_id == fake_entity_id

                        args, _ = mock_json_dump.call_args
                        dumped_data = args[0]
                        new_entity = dumped_data["@graph"][-1]

                        # id, type, label の基本情報チェック
                        assert new_entity["@id"] == fake_entity_id
                        assert new_entity["@type"] == "prov:Entity"
                        assert new_entity["label"] == dst_path

                        # atLocation
                        assert new_entity["prov:atLocation"]["@id"] == location

                        # checksum
                        assert new_entity["dcat:checksum"]["hashValue"] == hash_value
                        assert new_entity["dcat:checksum"]["checksumAlgorithm"] == "SHA-256"

                        # src_pathがリストなのでwasRevisionOfがある（activity_idに"modifyActivity"含むので）
                        assert "prov:wasRevisionOf" in new_entity
                        assert new_entity["prov:wasRevisionOf"] == [{"@id": p} for p in src_path]

                        # wasGeneratedBy
                        assert new_entity["prov:wasGeneratedBy"]["@id"] == activity_id

                        # agents
                        assert "prov:wasAttributedTo" in new_entity
                        assert new_entity["prov:wasAttributedTo"] == [{"@id":agents}]

    def test_create_entity_file_read_fail(self):
        """ファイルの読み込みに失敗する場合のテストケースです。"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        # open は通常通りモック
        m_open = mock.mock_open(read_data="invalid json")

        with mock.patch("builtins.open", m_open):
            # json.load を使おうとすると JSONDecodeError を出す
            with mock.patch("json.load", side_effect=json.JSONDecodeError("Expecting value", "doc", 0)):
                with pytest.raises(RuntimeError) as excinfo:
                    editor.create_entity(
                        dst_path="/path/to/file.txt",
                        location="urn:location:test",
                        hash_value="hash123",
                        activity_id="activity001",
                        src_path="src.txt",
                        agents="agent001"
                    )

                assert "読み込みに失敗しました" in str(excinfo.value)

    def test_create_entity_file_write_fail(self):
        """ファイルの書き込みに失敗する場合のテストケースです。"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        mock_entity_data = {"@graph": []}
        fake_entity_id = "urn:entity:test-id"

        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_entity_data))):
            with mock.patch("json.load", return_value=mock_entity_data):
                with mock.patch("data_governance.library.utils.research_flow_provenance.jsonld.generated_id", return_value=fake_entity_id):
                    #  json.dump に side_effect を設定して書き込みエラーを発生させる
                    with mock.patch("json.dump", side_effect=IOError("書き込みエラー")):
                        with pytest.raises(RuntimeError) as excinfo:
                            editor.create_entity(
                                dst_path="/path/to/file.txt",
                                location="urn:location:test",
                                hash_value="hash123",
                                activity_id="activity001",
                                src_path="src.txt",
                                agents="agent001"
                            )

                        # エラーメッセージに書き込み失敗と出ることを確認
                        assert "書き込みに失敗しました" in str(excinfo.value)

    def test_create_collection_all_args(self):
        """create_collectionを全引数ありで実行するテストケースです"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        mock_entity_data = {"@graph": []}
        fake_id = "urn:collection:explicit-label"

        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_entity_data))):
            with mock.patch("json.load", return_value=mock_entity_data):
                with mock.patch("data_governance.library.utils.research_flow_provenance.jsonld.generated_id", return_value=fake_id):
                    with mock.patch("json.dump") as mock_json_dump:
                        result_id = editor.create_collection(
                            members=["urn:entity:1", "urn:entity:2"],
                            dst_path="/some/path/test_folder",
                            location="/some/path/test_folder",
                            label="explicit-label"
                        )

                        assert result_id == fake_id
                        dumped_data = mock_json_dump.call_args[0][0]
                        collection = dumped_data["@graph"][-1]

                        assert collection["@id"] == fake_id
                        assert collection["@type"] == "prov:Collection"
                        assert collection["label"] == "explicit-label"
                        assert collection["prov:hadMember"] == [{"@id": "urn:entity:1"}, {"@id": "urn:entity:2"}]
                        assert collection["prov:atLocation"] == {"@id": "/some/path/test_folder"}

    def test_create_collection_without_label(self):
        """create_collectionをlabel引数無しで実行するテストケースです"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        mock_entity_data = {"@graph": []}

        dst_path = "/some/path/auto_label_folder"
        auto_label = Path(dst_path).name
        expected_id = f"urn:collection:{auto_label}"

        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_entity_data))):
            with mock.patch("json.load", return_value=mock_entity_data):
                with mock.patch("data_governance.library.utils.research_flow_provenance.jsonld.generated_id", return_value=expected_id):
                    with mock.patch("json.dump") as mock_json_dump:
                        result_id = editor.create_collection(
                            members=["urn:entity:1", "urn:entity:2"],
                            dst_path=dst_path,
                            location=dst_path,
                            label=None
                        )

                        assert result_id == expected_id

                        dumped_data = mock_json_dump.call_args[0][0]
                        collection = dumped_data["@graph"][-1]

                        assert collection["@id"] == expected_id
                        assert collection["@type"] == "prov:Collection"
                        assert collection["label"] == auto_label
                        assert collection["prov:hadMember"] == [{"@id": "urn:entity:1"}, {"@id": "urn:entity:2"}]
                        assert collection["prov:atLocation"] == {"@id": dst_path}

    def test_create_collection_without_dst_path(self):
        """create_collectionをdst_path引数無しで実行するテストケースです"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        mock_entity_data = {"@graph": []}

        label = "explicit-label"
        expected_id = f"urn:collection:{label}"

        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_entity_data))):
            with mock.patch("json.load", return_value=mock_entity_data):
                with mock.patch("data_governance.library.utils.research_flow_provenance.jsonld.generated_id", return_value=expected_id):
                    with mock.patch("json.dump") as mock_json_dump:
                        result_id = editor.create_collection(
                            members=["urn:entity:1"],
                            dst_path=None,
                            location=None,
                            label=label
                        )

                        assert result_id == expected_id

                        dumped_data = mock_json_dump.call_args[0][0]
                        collection = dumped_data["@graph"][-1]

                        assert collection["@id"] == expected_id
                        assert collection["@type"] == "prov:Collection"
                        assert collection["label"] == label
                        assert collection["prov:hadMember"] == [{"@id": "urn:entity:1"}]
                        assert "prov:atLocation" not in collection

    def test_create_collection_file_read_fail(self):
        """ファイルの読み込みに失敗する場合のテストケースです。"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        m_open = mock.mock_open(read_data="invalid json")

        with mock.patch("builtins.open", m_open):
            with mock.patch("json.load", side_effect=json.JSONDecodeError("Expecting value", "doc", 0)):
                with pytest.raises(RuntimeError) as excinfo:
                    editor.create_collection(
                        members=["urn:entity:1"],
                        dst_path="/some/path",
                        location="/some/path"
                    )

                assert "の読み込みに失敗しました" in str(excinfo.value)

    def test_create_collection_file_write_fail(self):
        """ファイルの書き込みに失敗する場合のテストケースです。"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        mock_entity_data = {"@graph": []}
        expected_id = "urn:collection:test-collection"

        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_entity_data))):
            with mock.patch("json.load", return_value=mock_entity_data):
                with mock.patch("data_governance.library.utils.research_flow_provenance.jsonld.generated_id", return_value=expected_id):
                    #  書き込み時に IOError を発生させる
                    with mock.patch("json.dump", side_effect=IOError("書き込み失敗")):
                        with pytest.raises(RuntimeError) as excinfo:
                            editor.create_collection(
                                members=["urn:entity:1"],
                                label="test-collection"
                            )

                        assert "の書き込みに失敗しました" in str(excinfo.value)

    def test_edit_entity_with_was_revision_of(self):
        """edit_entityでprov:wasRevisionOfを更新する通常の成功ケース。"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        entity_id = "urn:entity:test123"
        activity_id = "urn:activity:edit456"
        new_entities = ["urn:entity:src1", "urn:entity:src2"]

        # 元データには prov:wasRevisionOf が存在しているパターン
        mock_entity_data = {
            "@graph": [
                {
                    "@id": entity_id,
                    "label": "test123.txt",
                    "prov:wasRevisionOf": [{"@id": "urn:entity:old1"}],
                    "prov:wasInfluencedBy": [{"@id": "urn:activity:old"}],
                    "prov:wasDerivedFrom": [{"@id": "urn:entity:old1"}]
                }
            ]
        }

        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_entity_data))) as m:
            with mock.patch("json.load", return_value=mock_entity_data):
                with mock.patch("json.dump") as mock_json_dump:
                    # 関数実行
                    old_provenance = editor.edit_entity(entity_id, activity_id, new_entities)

                    # 書き出されたデータを取得
                    dumped_data = mock_json_dump.call_args[0][0]
                    updated_entity = dumped_data["@graph"][0]

                    # アサーション
                    assert updated_entity["@id"] == entity_id

                    # prov:wasRevisionOf が新しい new_entities に置き換えられていること
                    assert updated_entity["prov:wasRevisionOf"] == [
                        {"@id": "urn:entity:src1"},
                        {"@id": "urn:entity:src2"}
                    ]

                    # prov:wasInfluencedBy に activity_id が追加されていること
                    assert {"@id": activity_id} in updated_entity["prov:wasInfluencedBy"]

                    # prov:wasRevisionOf があるときは、old_provenance は空
                    assert old_provenance == []

    def test_edit_entity_with_new_entities_none(self):
        """edit_entityでnew_entitiesがNoneの場合のテストケース"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        entity_id = "urn:entity:test456"

        # prov:wasDerivedFrom 付きのエンティティデータ
        mock_entity_data = {
            "@graph": [
                {
                    "@id": entity_id,
                    "label": "test456.txt",
                    "prov:wasDerivedFrom": [{"@id": "urn:entity:old_src1"}, {"@id": "urn:entity:old_src2"}]
                }
            ]
        }

        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_entity_data))):
            with mock.patch("json.load", return_value=mock_entity_data):
                with mock.patch("json.dump") as mock_json_dump:
                    # 関数実行
                    old_provenance = editor.edit_entity(entity_id, None, None)

                    dumped_data = mock_json_dump.call_args[0][0]
                    updated_entity = dumped_data["@graph"][0]

                    # 検証
                    assert updated_entity["@id"] == entity_id
                    assert "prov:wasDerivedFrom" not in updated_entity  # 削除されていること
                    assert old_provenance == ["urn:entity:old_src1", "urn:entity:old_src2"]
    
    def test_edit_entity_with_derived_from_update(self):
        """edit_entityでprov:wasRevisionOfが存在しない場合にprov:wasDerivedFromが更新されるテスト"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        entity_id = "urn:entity:test789"
        activity_id = "urn:activity:edit999"
        new_entities = ["urn:entity:new1"]

        mock_entity_data = {
            "@graph": [
                {
                    "@id": entity_id,
                    "label": "test789.txt",
                    "prov:wasDerivedFrom": [{"@id": "urn:entity:old_src"}]
                    # Note: prov:wasRevisionOf がないパターン
                }
            ]
        }

        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_entity_data))):
            with mock.patch("json.load", return_value=mock_entity_data):
                with mock.patch("json.dump") as mock_json_dump:
                    # 関数実行
                    editor.edit_entity(entity_id, activity_id, new_entities)

                    dumped_data = mock_json_dump.call_args[0][0]
                    updated_entity = dumped_data["@graph"][0]

                    # 検証
                    assert updated_entity["@id"] == entity_id
                    assert updated_entity["prov:wasDerivedFrom"] == [{"@id": "urn:entity:new1"}]
                    assert {"@id": activity_id} in updated_entity["prov:wasInfluencedBy"]

    def test_edit_entity_entity_not_found(self):
        """エンティティが見つからなに場合のテストケースです。"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        mock_data = {
            "@graph": [
                {
                    "@id": "urn:entity:other",
                    "label": "not_target.txt"
                }
            ]
        }

        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_data))):
            with mock.patch("json.load", return_value=mock_data):
                with pytest.raises(ValueError) as e:
                    editor.edit_entity("urn:entity:not_found")
                assert "指定されたエンティティIDが存在しません" in str(e.value)

    def test_edit_entity_json_load_error(self):
        """ファイル読み込みに失敗する場合のテストケースです。"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        with mock.patch("builtins.open", mock.mock_open()):
            with mock.patch("json.load", side_effect=json.JSONDecodeError("Expecting value", "doc", 0)):
                with pytest.raises(RuntimeError) as e:
                    editor.edit_entity("urn:entity:any")
                assert "の読み込みに失敗しました" in str(e.value)

        def test_edit_collection_file_read_fail(self):
            """ファイルの読み込みに失敗する場合のテストケース"""
            test_env = {
                'JUPYTERHUB_SERVER_NAME': 'test_env',
                'HOME': '/home/jovyan'
            }

            with mock.patch.dict("os.environ", test_env):
                with mock.patch("os.path.exists", return_value=True):
                    editor = ProvenanceEditor()

            entity_id = "urn:collection:test-collection"
            activity_id = "urn:activity:test-activity"
            new_member = ["urn:entity:member1"]

            # openやjson.loadで読み込み時にIOErrorを発生させる
            with mock.patch("builtins.open", mock.mock_open()) as mock_open:
                mock_open.side_effect = IOError("ファイル読み込み失敗")
                with pytest.raises(RuntimeError) as excinfo:
                    editor.edit_collection(entity_id, activity_id, new_member)

            assert "の読み込みに失敗しました" in str(excinfo.value)

    def test_edit_entity_file_write_error(self):
        """ファイルの書き込みに失敗する場合のテストケースです。"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env), \
            mock.patch("os.path.exists", return_value=True):
            editor = ProvenanceEditor()

        entity_id = "urn:entity:test"
        activity_id = "urn:activity:edit"
        new_entities = ["urn:entity:new1"]

        mock_data = {
            "@graph": [
                {
                    "@id": entity_id,
                    "prov:wasDerivedFrom": [{"@id": "old"}]
                }
            ]
        }

        # 読み込み用 open は正常
        m_open_read = mock.mock_open(read_data=json.dumps(mock_data))

        # 書き込み用 open だけ IOError を発生させる
        def open_side_effect(file, mode='r', *args, **kwargs):
            if mode.startswith('w'):
                raise IOError("write error")
            return m_open_read.return_value

        with mock.patch("builtins.open", side_effect=open_side_effect), \
            mock.patch("json.load", return_value=mock_data):

            with pytest.raises(RuntimeError) as e:
                editor.edit_entity(entity_id, activity_id, new_entities)

            assert "の書き込みに失敗しました" in str(e.value)

    def test_edit_collection_full_args(self):
        """_edit_collectionを全引数ありで実行した場合のテストケースです。"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        entity_id = "urn:collection:test-collection"
        activity_id = "urn:activity:test-activity"
        new_member = ["urn:entity:member1", "urn:entity:member2"]

        # 元のコレクションデータ
        mock_entity_data = {
            "@graph": [
                {
                    "@id": entity_id,
                    "prov:hadMember": [{"@id": "urn:entity:old-member"}],
                    "prov:wasInfluencedBy": [{"@id": "urn:activity:old"}],
                }
            ]
        }

        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_entity_data))):
            with mock.patch("json.load", return_value=mock_entity_data):
                with mock.patch("json.dump") as mock_json_dump:
                    editor.edit_collection(entity_id, activity_id, new_member)

                    # json.dump が呼ばれた際の実際のデータを確認
                    args, kwargs = mock_json_dump.call_args
                    updated_data = args[0]

                    # prov:hadMemberがnew_memberに更新されているか
                    collection = next(item for item in updated_data["@graph"] if item["@id"] == entity_id)
                    assert collection["prov:hadMember"] == [{"@id": m} for m in new_member]

                    # prov:wasInfluencedByにactivity_idが追加されているか
                    influenced = collection.get("prov:wasInfluencedBy", [])
                    assert {"@id": activity_id} in influenced
    
    def test_edit_collection_file_read_fail(self):
        """ファイルの読み込みに失敗する場合のテストケース"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        entity_id = "urn:collection:test-collection"
        activity_id = "urn:activity:test-activity"
        new_member = ["urn:entity:member1"]

        # openやjson.loadで読み込み時にIOErrorを発生させる
        with mock.patch("builtins.open", mock.mock_open()) as mock_open:
            mock_open.side_effect = IOError("ファイル読み込み失敗")
            with pytest.raises(RuntimeError) as excinfo:
                editor.edit_collection(entity_id, activity_id, new_member)

        assert "の読み込みに失敗しました" in str(excinfo.value)



    def test_edit_collection_file_write_fail(self):
        """ファイルの書き込みに失敗する場合のテストケースです。"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        entity_id = "urn:collection:test-collection"
        activity_id = "urn:activity:test-activity"
        new_member = ["urn:entity:member1"]

        mock_entity_data = {
            "@graph": [
                {
                    "@id": entity_id,
                    "prov:hadMember": [{"@id": "urn:entity:old-member"}]
                }
            ]
        }

        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_entity_data))):
            with mock.patch("json.load", return_value=mock_entity_data):
                with mock.patch("json.dump", side_effect=IOError("書き込み失敗")):
                    with pytest.raises(RuntimeError) as excinfo:
                        editor.edit_collection(entity_id, activity_id, new_member)

        assert "の書き込みに失敗しました" in str(excinfo.value)

    def test_create_agent_all_args(self):
        """create_agentを全引数ありで実行した場合のテストケースです。"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        agent_id = "urn:agent:test-agent"
        agent_type = ["prov:Person"]
        agent_name = "Test Agent"
        comment = "This is a test agent."

        mock_agent_data = {"@graph": []}

        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_agent_data))) as mock_file:
            with mock.patch("json.load", return_value=mock_agent_data):
                with mock.patch("json.dump") as mock_json_dump:
                    result = editor.create_agent(agent_id, agent_type, agent_name, comment)

        # 戻り値の検証
        assert result == agent_id

        # json.dumpが呼ばれているか確認
        mock_json_dump.assert_called_once()
        dumped_data = mock_json_dump.call_args[0][0]

        # 新しいエージェントが追加されているか確認
        added_agent = dumped_data["@graph"][-1]
        assert added_agent["@id"] == agent_id
        assert added_agent["@type"] == agent_type
        assert added_agent["label"] == agent_name
        assert added_agent["comment"] == comment

    def test_create_agent_without_comment(self):
        """create_agentをコメント引数無しで実行する場合のテストケースです。"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        agent_id = "urn:agent:test-agent"
        agent_type = ["prov:Organization"]
        agent_name = "Test Org"
        comment = None

        mock_agent_data = {"@graph": []}

        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_agent_data))):
            with mock.patch("json.load", return_value=mock_agent_data):
                with mock.patch("json.dump") as mock_json_dump:
                    result = editor.create_agent(agent_id, agent_type, agent_name, comment)

        # 戻り値の検証
        assert result == agent_id

        # json.dumpが呼ばれているか確認
        mock_json_dump.assert_called_once()
        dumped_data = mock_json_dump.call_args[0][0]

        # 新しいエージェントが正しく追加されたか確認
        added_agent = dumped_data["@graph"][-1]
        assert added_agent["@id"] == agent_id
        assert added_agent["@type"] == agent_type
        assert added_agent["label"] == agent_name
        assert "comment" not in added_agent  # comment は含まれない

    def test_create_agent_file_read_fail(self):
        """ファイルの読み込みに失敗する場合のテストケース"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        agent_id = "urn:agent:test-agent"
        agent_type = ["prov:Person"]
        agent_name = "Test Agent"
        comment = "This is a test agent."

        # openの呼び出しで IOError を発生させる
        with mock.patch("builtins.open", mock.mock_open()) as mock_open:
            mock_open.side_effect = IOError("ファイル読み込み失敗")

            with pytest.raises(RuntimeError) as excinfo:
                editor.create_agent(agent_id, agent_type, agent_name, comment)

        assert "の読み込みに失敗しました" in str(excinfo.value)

    def test_create_agent_file_write_fail(self):
        """ファイルの書き込みに失敗する場合のテストケースです。"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        agent_id = "urn:agent:test-agent"
        agent_type = ["prov:Person"]
        agent_name = "Test Agent"
        comment = "テストコメント"

        mock_agent_data = {"@graph": []}

        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_agent_data))):
            with mock.patch("json.load", return_value=mock_agent_data):
                with mock.patch("json.dump", side_effect=IOError("書き込み失敗")):
                    with pytest.raises(RuntimeError) as excinfo:
                        editor.create_agent(
                            agent_id=agent_id,
                            agent_type=agent_type,
                            agent_name=agent_name,
                            comment=comment
                        )

        assert "の書き込みに失敗しました" in str(excinfo.value)

    def test_generated_end_timestamp(self):
        """_generated_end_timestampの正常実行テストケースです。"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        fixed_time = datetime(2025, 8, 29, 15, 30, 0, tzinfo=timezone(timedelta(hours=9)))
        iso_time = fixed_time.isoformat()

        with mock.patch("data_governance.library.utils.research_flow_provenance.jsonld.datetime") as mock_datetime:
            mock_datetime.now.return_value = fixed_time
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            mock_datetime.timezone = timezone
            mock_datetime.timedelta = timedelta

            result = editor._generated_end_timestamp()

            assert result == iso_time

    def test_delete_activity_success(self):
        """正常にアクティビティを削除できるケース"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env), \
             mock.patch("os.path.exists", return_value=True):
            editor = ProvenanceEditor()

        target_uri = "urn:activity:target"
        mock_data = {
            "@graph": [
                {"@id": "urn:activity:target", "label": "target"},
                {"@id": "urn:activity:keep", "label": "keep"}
            ]
        }

        m_open_read = mock.mock_open(read_data=json.dumps(mock_data))

        with mock.patch("builtins.open", side_effect=lambda file, mode='r', *args, **kwargs:
                        m_open_read.return_value if mode.startswith('r') else mock.mock_open().return_value), \
             mock.patch("json.load", return_value=mock_data), \
             mock.patch("json.dump") as mock_json_dump:

            editor.delete_activity(target_uri)

            written_data = mock_json_dump.call_args[0][0]
            updated_graph = written_data["@graph"]

            assert all(entry["@id"] != target_uri for entry in updated_graph)
            assert any(entry["@id"] == "urn:activity:keep" for entry in updated_graph)

    def test_delete_activity_not_found(self):
        """削除対象のアクティビティが存在しないケース"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env), \
             mock.patch("os.path.exists", return_value=True):
            editor = ProvenanceEditor()

        mock_data = {
            "@graph": [
                {"@id": "urn:activity:other", "label": "other"}
            ]
        }

        m_open_read = mock.mock_open(read_data=json.dumps(mock_data))

        with mock.patch("builtins.open", side_effect=lambda file, mode='r', *args, **kwargs:
                        m_open_read.return_value if mode.startswith('r') else mock.mock_open().return_value), \
             mock.patch("json.load", return_value=mock_data), \
             mock.patch("json.dump") as mock_json_dump:

            editor.delete_activity("urn:activity:not_found")

            written_data = mock_json_dump.call_args[0][0]
            assert written_data["@graph"] == mock_data["@graph"]

    def test_delete_activity_read_error(self):
        """読み込みエラー（IOError）が発生するケース"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env), \
             mock.patch("os.path.exists", return_value=True):
            editor = ProvenanceEditor()

        with mock.patch("builtins.open", side_effect=IOError("read error")):
            with pytest.raises(RuntimeError) as e:
                editor.delete_activity("urn:activity:target")

            assert "の読み込みに失敗しました" in str(e.value)

    def test_delete_activity_write_error(self):
        """書き込みエラー（IOError）が発生するケース"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env), \
             mock.patch("os.path.exists", return_value=True):
            editor = ProvenanceEditor()

        mock_data = {
            "@graph": [
                {"@id": "urn:activity:target", "label": "target"},
                {"@id": "urn:activity:keep", "label": "keep"}
            ]
        }

        m_open_read = mock.mock_open(read_data=json.dumps(mock_data))

        def open_side_effect(file, mode='r', *args, **kwargs):
            if mode.startswith("w"):
                raise IOError("write error")
            return m_open_read.return_value

        with mock.patch("builtins.open", side_effect=open_side_effect), \
             mock.patch("json.load", return_value=mock_data):

            with pytest.raises(RuntimeError) as e:
                editor.delete_activity("urn:activity:target")

            assert "の書き込みに失敗しました" in str(e.value)

    def test_delete_entity_success(self):
        """正常にエンティティを削除できるケース"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env), \
             mock.patch("os.path.exists", return_value=True):
            editor = ProvenanceEditor()

        target_uri = "urn:entity:target"
        mock_data = {
            "@graph": [
                {"@id": target_uri, "label": "target"},
                {"@id": "urn:entity:keep", "label": "keep"}
            ]
        }

        m_open_read = mock.mock_open(read_data=json.dumps(mock_data))

        with mock.patch("builtins.open", side_effect=lambda file, mode='r', *args, **kwargs:
                        m_open_read.return_value if mode.startswith('r') else mock.mock_open().return_value), \
             mock.patch("json.load", return_value=mock_data), \
             mock.patch("json.dump") as mock_json_dump:

            editor.delete_entity(target_uri)

            written_data = mock_json_dump.call_args[0][0]
            updated_graph = written_data["@graph"]

            assert all(entry["@id"] != target_uri for entry in updated_graph)
            assert any(entry["@id"] == "urn:entity:keep" for entry in updated_graph)

    def test_delete_entity_not_found(self):
        """削除対象のエンティティが存在しない場合でも例外が発生しないケース"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env), \
             mock.patch("os.path.exists", return_value=True):
            editor = ProvenanceEditor()

        mock_data = {
            "@graph": [
                {"@id": "urn:entity:other", "label": "other"}
            ]
        }

        m_open_read = mock.mock_open(read_data=json.dumps(mock_data))

        with mock.patch("builtins.open", side_effect=lambda file, mode='r', *args, **kwargs:
                        m_open_read.return_value if mode.startswith('r') else mock.mock_open().return_value), \
             mock.patch("json.load", return_value=mock_data), \
             mock.patch("json.dump") as mock_json_dump:

            editor.delete_entity("urn:entity:not_found")

            written_data = mock_json_dump.call_args[0][0]
            assert written_data["@graph"] == mock_data["@graph"]

    def test_delete_entity_read_error(self):
        """読み込みエラー（IOError）が発生するケース"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env), \
             mock.patch("os.path.exists", return_value=True):
            editor = ProvenanceEditor()

        with mock.patch("builtins.open", side_effect=IOError("read error")):
            with pytest.raises(RuntimeError) as e:
                editor.delete_entity("urn:entity:target")

            assert "の読み込みに失敗しました" in str(e.value)

    def test_delete_entity_write_error(self):
        """書き込みエラー（IOError）が発生するケース"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env), \
             mock.patch("os.path.exists", return_value=True):
            editor = ProvenanceEditor()

        mock_data = {
            "@graph": [
                {"@id": "urn:entity:target", "label": "target"},
                {"@id": "urn:entity:keep", "label": "keep"}
            ]
        }

        m_open_read = mock.mock_open(read_data=json.dumps(mock_data))

        def open_side_effect(file, mode='r', *args, **kwargs):
            if mode.startswith("w"):
                raise IOError("write error")
            return m_open_read.return_value

        with mock.patch("builtins.open", side_effect=open_side_effect), \
             mock.patch("json.load", return_value=mock_data):

            with pytest.raises(RuntimeError) as e:
                editor.delete_entity("urn:entity:target")

            assert "の書き込みに失敗しました" in str(e.value)

    def test_change_entity_label_success(self):
        """正常にエンティティのラベルを変更できるケース"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env), \
             mock.patch("os.path.exists", return_value=True):
            editor = ProvenanceEditor()

        entity_id = "urn:entity:test123"
        new_label = "New Label"

        mock_data = {
            "@graph": [
                {"@id": entity_id, "label": "Old Label"},
                {"@id": "urn:entity:other", "label": "Other Label"}
            ]
        }

        m_open_read = mock.mock_open(read_data=json.dumps(mock_data))

        with mock.patch("builtins.open", side_effect=lambda file, mode='r', *args, **kwargs:
                        m_open_read.return_value if mode.startswith('r') else mock.mock_open().return_value), \
             mock.patch("json.load", return_value=mock_data), \
             mock.patch("json.dump") as mock_json_dump:

            editor.change_entity_label(entity_id, new_label)

            dumped_data = mock_json_dump.call_args[0][0]
            updated_entity = next(item for item in dumped_data["@graph"] if item["@id"] == entity_id)

            assert updated_entity["label"] == new_label

    def test_change_entity_label_success(self):
        """正常にエンティティのラベルを変更できるケース"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env), \
            mock.patch("os.path.exists", return_value=True):
            editor = ProvenanceEditor()

        entity_id = "urn:entity:test123"
        new_label = "New Label"
        new_location = "New Location"  # ここを追加

        mock_data = {
            "@graph": [
                {"@id": entity_id, "label": "Old Label"},
                {"@id": "urn:entity:other", "label": "Other Label"}
            ]
        }

        m_open_read = mock.mock_open(read_data=json.dumps(mock_data))

        with mock.patch("builtins.open", side_effect=lambda file, mode='r', *args, **kwargs:
                        m_open_read.return_value if mode.startswith('r') else mock.mock_open().return_value), \
            mock.patch("json.load", return_value=mock_data), \
            mock.patch("json.dump") as mock_json_dump:

            # new_location を引数に追加して呼び出す
            editor.change_entity_label(entity_id, new_label, new_location)

            dumped_data = mock_json_dump.call_args[0][0]
            updated_entity = next(item for item in dumped_data["@graph"] if item["@id"] == entity_id)

            assert updated_entity["label"] == new_label
            assert updated_entity["prov:atLocation"]["@id"] == new_location

    def test_change_entity_label_read_error(self):
        """ファイル読み込みエラーが発生するケース"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env), \
            mock.patch("os.path.exists", return_value=True):
            editor = ProvenanceEditor()

        with mock.patch("builtins.open", side_effect=IOError("read error")):
            with pytest.raises(RuntimeError) as e:
                # new_location を追加
                editor.change_entity_label("urn:entity:test", "New Label", "New Location")

            assert "の読み込みに失敗しました" in str(e.value)

    def test_change_entity_label_write_error(self):
        """ファイル書き込みエラーが発生するケース"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env), \
            mock.patch("os.path.exists", return_value=True):
            editor = ProvenanceEditor()

        mock_data = {
            "@graph": [
                {"@id": "urn:entity:test", "label": "Old Label"}
            ]
        }

        m_open_read = mock.mock_open(read_data=json.dumps(mock_data))

        def open_side_effect(file, mode='r', *args, **kwargs):
            if mode.startswith("w"):
                raise IOError("write error")
            return m_open_read.return_value

        with mock.patch("builtins.open", side_effect=open_side_effect), \
            mock.patch("json.load", return_value=mock_data):

            with pytest.raises(RuntimeError) as e:
                # new_location 引数を追加
                editor.change_entity_label("urn:entity:test", "New Label", "New Location")

            assert "の書き込みに失敗しました" in str(e.value)

    def test_get_file_list(self):
        """正常系テストケースです。"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict(os.environ, test_env), \
            mock.patch("os.path.exists", return_value=True), \
            mock.patch("data_governance.library.utils.config.path_config.DG_RESEARCHFLOW_FOLDER", "data_governance/researchflow"):

            editor = ProvenanceEditor()

            file_list = editor.get_file_list()

            base_path = os.path.join(test_env['HOME'], "data_governance/researchflow", test_env['JUPYTERHUB_SERVER_NAME'])
            expected_list = [
                os.path.join(base_path, editor.PROV_ENTITY),
                os.path.join(base_path, editor.PROV_ACTIVITY),
                os.path.join(base_path, editor.PROV_AGENT),
            ]

            assert file_list == expected_list


    


    
