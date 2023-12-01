import os
from typing import List
from datetime import datetime
import uuid

from dg_drawer.research_flow import ResearchFlowStatus, PhaseStatus, SubFlowStatus,FlowDrawer

from ..config import message as msg_config, path_config
from ..error import NotFoundSubflowDataError
from ..html.security import escape_html_text
from ..file import JsonFile


def get_subflow_type_and_id(working_file_path: str):
    """ノートブックのパスを受け取ってsubflowの種別とidを返す

    Args:
        working_file_path (str): researchflowディレクトリ配下のノートブックのファイルパス

    Returns:
        str: サブフロー種別（無い場合は空文字）
        str: サブフローID（無い場合は空文字）
    """
    working_file_path = os.path.normpath(working_file_path)
    parts = os.path.dirname(working_file_path).split(os.sep)
    target_directory = path_config.RESEARCHFLOW
    subflow_type = ""
    subflow_id = ""

    try:
        index = parts.index(target_directory)
    except:
        raise

    abs_root = path_config.get_abs_root_form_working_dg_file_path(working_file_path)
    rf_status = ResearchFlowStatusOperater(
                    path_config.get_research_flow_status_file_path(abs_root)
                )

    phase_index = index + 1
    if phase_index < len(parts):
        phase_list = rf_status.get_subflow_phases()
        dir_name = parts[phase_index]
        if dir_name in phase_list:
            subflow_type = dir_name

    id_index = index + 2
    if id_index < len(parts):
        id_list = rf_status.get_subflow_ids(subflow_type)
        dir_name = parts[id_index]
        if dir_name in id_list:
            subflow_id = dir_name

    return subflow_type, subflow_id


class ResearchFlowStatusOperater(JsonFile):

    def __init__(self, file_path: str):
        if os.path.isfile(file_path):
            super().__init__(file_path)
        else:
            raise FileNotFoundError(f'[ERROR] : Not Found File. File Path : {file_path}')


    def get_research_flow_status(self):
        return super().read()

    def get_data_dir(self, phase_name, id):
        """phase nameとidからdata_dirを取得する"""
        research_flow_status = self.load_research_flow_status()
        for phase in research_flow_status:
            if phase._name != phase_name:
                continue
            for sb in phase._sub_flow_data:
                if sb._id == id:
                    return sb._data_dir

    def get_svg_of_research_flow_status(self)->str:
        """Get SVG data of Research Flow Image by file path

        Returns:
            str: SVG data of Research Flow Image
        """
        research_flow_status = self.load_research_flow_status()
        # Update display pahse name
        research_flow_status = self.update_display_object(research_flow_status)
        fd = FlowDrawer(research_flow_status=research_flow_status)
        # generate SVG of Research Flow Image
        return fd.draw()

    def update_display_object(self, research_flow_status:List[PhaseStatus])-> List[PhaseStatus]:
        """画面表示ように調整する"""
        update_research_flow_status = []
        for phase in research_flow_status:
            phase.update_name(name = msg_config.get('research_flow_phase_display_name', phase._name))
            for sb in phase._sub_flow_data:
                sb._name = escape_html_text(sb._name)
            update_research_flow_status.append(phase)
        return update_research_flow_status

    def init_research_preparation(self, file_path:str):
        """研究準備ステータスの初期化"""
        # 研究準備のサブフローデータのサブフロー作成時間が-1の場合、現在の現時刻に更新する。
        research_flow_status = self.load_research_flow_status()
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
        self.update_file(research_flow_status)


    def update_file(self, research_flow_status:List[PhaseStatus]):
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
                sub_flow_unit_data['data_dir'] = sub_flow_unit._data_dir
                sub_flow_unit_data['link'] = sub_flow_unit._link
                sub_flow_unit_data['parent_ids'] = sub_flow_unit._parent_ids
                sub_flow_unit_data['create_datetime'] = sub_flow_unit._create_datetime
                phase_status_data['sub_flow_data'].append(sub_flow_unit_data)
            research_flow_status_data['research_flow_pahse_data'].append(phase_status_data)
        # リサーチフローステータス管理JSONをアップデート
        super().write(research_flow_status_data)


    def issue_uuidv4(self)->str:
        """UUIDv4の発行"""
        return str(uuid.uuid4())


    def exist_sub_flow_id_in_research_flow_status(self, research_flow_status:List[PhaseStatus], target_id:str)->bool:
        """リサーチフローステータス管理情報にサブフローIDが存在するかチェック"""

        for phase in research_flow_status:
            for sub_flow in phase._sub_flow_data:
                if sub_flow._id == target_id:
                    return True
        return False


    def issue_unique_sub_flow_id(self)->str:
        """ユニークなサブフローIDを発行する"""
        while True:
            candidate_id = self.issue_uuidv4()
            research_flow_status = self.load_research_flow_status()
            if self.exist_sub_flow_id_in_research_flow_status(research_flow_status, candidate_id):
                ## 存在する場合は、発行し直し
                continue
            else:
                ## ユニークID取得に成功
                return candidate_id

    def update_research_flow_status(self, creating_phase_seq_number, sub_flow_name, data_dir_name, parent_sub_flow_ids):
        """リサーチフローステータスの更新

        Args:
            creating_phase_seq_number (int): [作成フェーズ]

            sub_flow_name (str): [新規サブフロー名]

            parent_sub_flow_id (list[str]): [親サブフローID]
        """
        # リサーチフローステータス管理JSONの更新
        research_flow_status = self.load_research_flow_status()
        phase_name = None
        new_sub_flow_id = None
        for phase_status in research_flow_status:
            if phase_status._seq_number == creating_phase_seq_number:
                phase_name = phase_status._name
                current_datetime = datetime.now()
                new_sub_flow_id = self.issue_unique_sub_flow_id()
                new_subflow_item = SubFlowStatus(
                    id=new_sub_flow_id,
                    name=sub_flow_name,
                    data_dir=data_dir_name,
                    link=f'./{phase_name}/{new_sub_flow_id}/{path_config.MENU_NOTEBOOK}',
                    parent_ids=parent_sub_flow_ids,
                    create_datetime=int(current_datetime.timestamp())
                )
                phase_status._sub_flow_data.append(new_subflow_item)
            else:
                continue

        if phase_name is None:
            raise Exception(f'Not Found phase. target phase seq_number : {creating_phase_seq_number}')
        if new_sub_flow_id is None:
            raise Exception(f'Cannot Issue New Sub Flow ID')
        # リサーチフローステータス管理JSONの上書き
        self.update_file(research_flow_status)
        return phase_name, new_sub_flow_id

    def del_sub_flow_data_by_sub_flow_id(self, sub_flow_id):
        research_flow_status = self.load_research_flow_status()

        for phase_status in research_flow_status:
            remove_subflow = None
            for subflow in phase_status._sub_flow_data:
                if subflow._id == sub_flow_id:
                    remove_subflow = subflow
                else:
                    continue
            if remove_subflow is not None:
                phase_status._sub_flow_data.remove(remove_subflow)
            else:
                raise NotFoundSubflowDataError(f'There Is No Subflow Data to Delete. sub_flow_id : {sub_flow_id}')
        # リサーチフローステータス管理JSONの上書き
        self.update_file(research_flow_status)


    def is_unique_subflow_name(self, phase_seq_number, sub_flow_name)->bool:
        """サブフロー名のユニークチェック"""
        exist_phase = False
        research_flow_status = self.load_research_flow_status()
        for phase_status in research_flow_status:
            if phase_status._seq_number == phase_seq_number:
                exist_phase = True
                for sub_flow_item in phase_status._sub_flow_data:
                    if sub_flow_item._name == sub_flow_name:
                        return False
            else:
                continue

        if not exist_phase:
            raise Exception(f'Not Found phase. target phase seq_number : {phase_seq_number}')

        return True

    def is_unique_data_dir(self, phase_seq_number, data_dir_name)->bool:
        """データディレクトリ名のユニークチェック"""
        exist_phase = False
        research_flow_status = self.load_research_flow_status()
        for phase_status in research_flow_status:
            if phase_status._seq_number == phase_seq_number:
                exist_phase = True
                for sub_flow_item in phase_status._sub_flow_data:
                    if sub_flow_item._data_dir == data_dir_name:
                        return False
            else:
                continue

        if not exist_phase:
            raise Exception(f'Not Found phase. target phase seq_number : {phase_seq_number}')

        return True

    def load_research_flow_status(self)->List[PhaseStatus]:
        """リサーチフローステータス管理JSONからリサーチフローステータスインスタンスを取得する"""
        return ResearchFlowStatus.load_from_json(str(self.path))

    def get_subflow_phases(self)->List[str]:
        """全てのphase名を取得する"""
        research_flow_status = self.load_research_flow_status()
        phase_list = []
        for phase_status in research_flow_status:
            phase_list.append(phase_status._name)
        return phase_list

    def get_subflow_ids(self, phase_name: str)->List[str]:
        """指定したphaseにあるサブフローのidを全て取得する"""
        research_flow_status = self.load_research_flow_status()
        id_list = []
        for phase_status in research_flow_status:
            if phase_status._name != phase_name:
                continue
            for subflow_data in phase_status._sub_flow_data:
                id_list.append(subflow_data._id)
        return id_list
