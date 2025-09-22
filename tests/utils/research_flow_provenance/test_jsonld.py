"""jsonld.pyファイルのテストを記述したモジュールです。"""

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import uuid
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

    def test___init__1(self):
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

    def test___init__2(self):
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

    def test___init__3(self):
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

    def test___init__4(self):
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

                    print("=== dumpされたactivity_data ===")
                    print(json.dumps(dumped_data, indent=2, ensure_ascii=False))
                    print("===============================")

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

                    print("=== dumpされたactivity_data ===")
                    print(json.dumps(dumped_data, indent=2, ensure_ascii=False))
                    print("===============================")

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

                    print("=== dumpされたactivity_data ===")
                    print(json.dumps(dumped_data, indent=2, ensure_ascii=False))
                    print("===============================")

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

                    print("=== dumpされたactivity_data ===")
                    print(json.dumps(dumped_data, indent=2, ensure_ascii=False))
                    print("===============================")

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

                        print("=== dumpされたactivity_data ===")
                        print(json.dumps(dumped_data, indent=2, ensure_ascii=False))
                        print("===============================")

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

                        print("=== dumpされたactivity_data ===")
                        print(json.dumps(dumped_data, indent=2, ensure_ascii=False))
                        print("===============================")

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

                        print("=== dumpされたactivity_data ===")
                        print(json.dumps(dumped_data, indent=2, ensure_ascii=False))
                        print("===============================")

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

                        print("=== dumpされたactivity_data ===")
                        print(json.dumps(dumped_data, indent=2, ensure_ascii=False))
                        print("===============================")

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

                        print("=== dumpされたactivity_data ===")
                        print(json.dumps(dumped_data, indent=2, ensure_ascii=False))
                        print("===============================")

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

                        print("=== dumpされたactivity_data ===")
                        print(json.dumps(dumped_data, indent=2, ensure_ascii=False))
                        print("===============================")

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
        """edit_entityでwasRevisionOfを更新するテストケースです。"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        # 1. 環境変数とファイルパスモック
        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        # 2. テストデータ準備
        entity_id = "urn:entity:test123"
        activity_id = "urn:activity:edit456"
        new_entities = ["urn:entity:src1", "urn:entity:src2"]

        mock_entity_data = {
            "@graph": [
                {
                    "@id": entity_id,
                    "label": "test123.txt",
                    "prov:wasRevisionOf": [{"@id": "urn:entity:old1"}],
                    "prov:wasInfluencedBy": [{"@id": "urn:activity:old"}],
                }
            ]
        }

        # 3. open + json.load + json.dump をモック
        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_entity_data))):
            with mock.patch("json.load", return_value=mock_entity_data):
                with mock.patch("json.dump") as mock_json_dump:
                    # 4. 関数実行
                    editor.edit_entity(entity_id, activity_id, new_entities)

                    # 5. dump 呼び出しデータを確認
                    dumped_data = mock_json_dump.call_args[0][0]
                    updated_entity = dumped_data["@graph"][0]

                    print("=== dumpされたactivity_data ===")
                    print(json.dumps(dumped_data, indent=2, ensure_ascii=False))
                    print("===============================")

                    # 6. 検証
                    assert updated_entity["@id"] == entity_id
                    assert updated_entity["prov:wasRevisionOf"] == [
                        {"@id": "urn:entity:src1"},
                        {"@id": "urn:entity:src2"}
                    ]
                    # prov:wasInfluencedBy はリストとして追加されているか
                    assert {"@id": activity_id} in updated_entity["prov:wasInfluencedBy"]

    def test_edit_entity_with_was_derived_from(self):
        """edit_entityでwasDerivedFromを更新するテストケースです。"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        # 1. 環境変数とファイルパスモック
        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        # 2. テストデータ準備
        entity_id = "urn:entity:no_revision"
        activity_id = "urn:activity:update789"
        new_entities = ["urn:entity:sourceA", "urn:entity:sourceB"]

        mock_entity_data = {
            "@graph": [
                {
                    "@id": entity_id,
                    "label": "sample.txt",
                    "prov:wasDerivedFrom": [{"@id": "urn:entity:old1"}]
                }
            ]
        }

        # 3. open + json.load + json.dump をモック
        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_entity_data))):
            with mock.patch("json.load", return_value=mock_entity_data):
                with mock.patch("json.dump") as mock_json_dump:
                    # 4. 関数実行
                    editor.edit_entity(entity_id, activity_id, new_entities)

                    # 5. 結果確認
                    dumped_data = mock_json_dump.call_args[0][0]
                    updated_entity = dumped_data["@graph"][0]

                    print("=== dumpされたactivity_data ===")
                    print(json.dumps(dumped_data, indent=2, ensure_ascii=False))
                    print("===============================")

                    assert updated_entity["@id"] == entity_id
                    assert updated_entity["prov:wasDerivedFrom"] == [
                        {"@id": "urn:entity:sourceA"},
                        {"@id": "urn:entity:sourceB"}
                    ]
                    assert {"@id": activity_id} in updated_entity["prov:wasInfluencedBy"]

    def test_edit_entity_not_found(self):
        """edit_entityを存在しないentity_idで実行した場合のテストケースです。"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        # 存在しない entity_id を指定
        entity_id = "urn:entity:not_exist"
        activity_id = "urn:activity:dummy"
        new_entities = ["urn:entity:x"]

        # @graph 内に一致する @id が存在しない
        mock_entity_data = {
            "@graph": [
                {"@id": "urn:entity:other"}
            ]
        }

        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_entity_data))):
            with mock.patch("json.load", return_value=mock_entity_data):
                # 例外が発生するか検証
                with pytest.raises(ValueError) as excinfo:
                    editor.edit_entity(entity_id, activity_id, new_entities)

                assert f"指定されたエンティティIDが存在しません" in str(excinfo.value)

    def test_edit_entity_file_read_error(self):
        """ファイルの読み込みに失敗する場合のテストケースです。"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        entity_id = "urn:entity:any"
        activity_id = "urn:activity:any"
        new_entities = ["urn:entity:x"]

        # open() が IOError を発生させるようにする
        with mock.patch("builtins.open", side_effect=IOError("読み込み失敗")):
            with pytest.raises(RuntimeError) as excinfo:
                editor.edit_entity(entity_id, activity_id, new_entities)

            assert "の読み込みに失敗しました" in str(excinfo.value)

    def test_edit_entity_file_write_fail(self):
        """ファイルの書き込みに失敗する場合のテストケースです。"""
        test_env = {
            'JUPYTERHUB_SERVER_NAME': 'test_env',
            'HOME': '/home/jovyan'
        }

        with mock.patch.dict("os.environ", test_env):
            with mock.patch("os.path.exists", return_value=True):
                editor = ProvenanceEditor()

        entity_id = "urn:entity:test-entity"
        activity_id = "urn:activity:test-activity"
        new_entities = ["urn:entity:new-1"]

        mock_entity_data = {
            "@graph": [
                {
                    "@id": entity_id,
                    "label": "file.txt",
                    "prov:wasRevisionOf": [{"@id": "urn:entity:old"}],
                }
            ]
        }

        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_entity_data))):
            with mock.patch("json.load", return_value=mock_entity_data):
                # 書き込みで IOError を発生
                with mock.patch("json.dump", side_effect=IOError("書き込み失敗")):
                    with pytest.raises(RuntimeError) as excinfo:
                        editor.edit_entity(entity_id, activity_id, new_entities)

                    assert "の書き込みに失敗しました" in str(excinfo.value)

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
                    print("=== dumpされたactivity_data ===")
                    print(json.dumps(updated_data, indent=2, ensure_ascii=False))
                    print("===============================")

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

        print("=== dumpされたactivity_data ===")
        print(json.dumps(dumped_data, indent=2, ensure_ascii=False))
        print("===============================")

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

        print("=== dumpされたactivity_data ===")
        print(json.dumps(dumped_data, indent=2, ensure_ascii=False))
        print("===============================")

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
