import json
from typing import List
from datetime import datetime
from dg_drawer.research_flow import ResearchFlowStatus, PhaseStatus, FlowDrawer
from ..utils.config import path_config, message as msg_config

class ResearchFlowStatusFile():

    @classmethod
    def get_research_flow_status(cls, file_path:str):
        with open(file_path) as file:
            return json.load(file)


    @classmethod
    def get_svg_of_research_flow_status(cls, file_path:str)->str:
        """Get SVG data of Research Flow Image by file path

        Returns:
            str: SVG data of Research Flow Image
        """
        research_flow_status = ResearchFlowStatus.load_from_json(file_path)
        # Update display pahse name
        research_flow_status = ResearchFlowStatusFile.update_display_phase_name(research_flow_status)
        fd = FlowDrawer(research_flow_status=research_flow_status)
        # generate SVG of Research Flow Image
        return fd.draw()

    @classmethod
    def update_display_phase_name(cls, research_flow_status:List[PhaseStatus])-> List[PhaseStatus]:
        """フェーズの表示名更新"""
        update_research_flow_status = []
        for phase in research_flow_status:
            phase.update_name(name = msg_config.get('research_flow_phase_display_name', phase._name))
            update_research_flow_status.append(phase)
        return update_research_flow_status

    @classmethod
    def init_research_preparation(cls, file_path:str):
        """研究準備ステータスの初期化"""
        # 研究準備のサブフローデータのサブフロー作成時間が-1の場合、現在の現時刻に更新する。
        research_flow_status = ResearchFlowStatus.load_from_json(file_path)
        for phase_status in research_flow_status:
            if phase_status._seq_number == 1:
                # 研究準備フェーズ
                if phase_status._sub_flow_data[0]._create_datetime == -1:
                    # create_datetimeが-1場合、初回アクセスのため現在時刻を埋める
                    # 現在の日時を取得
                    current_datetime = datetime.now()
                    # 現在時刻を埋める
                    phase_status._sub_flow_data[0]._create_datetime = int(current_datetime.timestamp())
            else:
                continue

        #リサーチフローステータス管理JSONを更新する。
        ResearchFlowStatusFile.update_file(file_path, research_flow_status)



    @classmethod
    def update_file(cls, file_path:str, research_flow_status:List[PhaseStatus]):
        # research_flow_statusを基にリサーチフローステータス管理JSONを更新する。
        research_flow_status_data = {}
        research_flow_status_data['research_flow_pahse_data'] = []

        for phase_status in research_flow_status:
            phase_status_data = {}
            phase_status_data['seq_number'] = phase_status._seq_number
            phase_status_data['name'] = phase_status._name
            phase_status_data['sub_flow_data'] = []
            for sub_flow_unit in phase_status._sub_flow_data:
                sub_flow_unit_data = {}
                sub_flow_unit_data['id'] = sub_flow_unit._id
                sub_flow_unit_data['name'] = sub_flow_unit._name
                sub_flow_unit_data['link'] = sub_flow_unit._link
                sub_flow_unit_data['parent_ids'] = sub_flow_unit._parent_ids
                sub_flow_unit_data['create_datetime'] = sub_flow_unit._create_datetime
                phase_status_data['sub_flow_data'].append(sub_flow_unit_data)
            research_flow_status_data['research_flow_pahse_data'].append(phase_status_data)
        # リサーチフローステータス管理JSONをアップデート
        with open(file_path, 'w') as file:
            json.dump(research_flow_status_data, file, indent=4)
