"""リサーチフローステータス関連の処理を行う関数やクラスが記載されたモジュールです。"""
from datetime import datetime
import os
import uuid

from dg_drawer.research_flow import ResearchFlowStatus, PhaseStatus, SubFlowStatus, FlowDrawer

from library.utils.config import message as msg_config, path_config
from library.utils.error import NotFoundSubflowDataError
from library.utils.file import JsonFile
from library.utils.html.security import escape_html_text


def get_subflow_type_and_id(working_file_path: str) -> tuple[str, str]:
    """サブフローの種別とidを取得するメソッドです。

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
    rf_status = ResearchFlowStatusOperater(path_config.get_research_flow_status_file_path(abs_root))

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


def get_data_dir(working_file_path: str) -> str:
    """該当するデータディレクトリまでの絶対パスを取得するメソッドです。

    Args:
        working_file_path (str): データディレクトリを指定する作業ディレクトリのファイルパス

    Returns:
        str:該当するデータディレクトリの絶対パス

    Raises:
        Exception:subflow_typeまたはsubflow_idが取得できなかった
        Exception:ディレクトリ名が取得できなかった

    """
    working_file_path = os.path.normpath(working_file_path)
    abs_root = path_config.get_abs_root_form_working_dg_file_path(working_file_path)

    subflow_type, subflow_id = get_subflow_type_and_id(working_file_path)
    if not subflow_type or not subflow_id:
        raise Exception(f'## [INTERNAL ERROR] : don\'t get subflow type or id.')
    try:
        rf_status_file = path_config.get_research_flow_status_file_path(abs_root)
        rf_status = ResearchFlowStatusOperater(rf_status_file)
        data_dir_name = rf_status.get_data_dir(subflow_type, subflow_id)

    except Exception as e:
        raise Exception(f'## [INTERNAL ERROR] : don\'t get directory name of data') from e
    return path_config.get_task_data_dir(abs_root, subflow_type, data_dir_name)


class ResearchFlowStatusFile(JsonFile):
    """リサーチフローステータスの参照や操作を行うクラスです。"""

    def __init__(self, file_path: str):
        """クラスのインスタンスの初期化を行うメソッドです。コンストラクタ

        Args:
            file_path (str):ファイルパス

        Raises:
            FileNotFoundError:指定したパスのファイルが存在しない

        """
        if os.path.isfile(file_path):
            super().__init__(file_path)
        else:
            raise FileNotFoundError(f'[ERROR] : Not Found File. File Path : {file_path}')

    def load_research_flow_status(self) -> list[PhaseStatus]:
        """リサーチフローステータス管理JSONからリサーチフローステータスのインスタンスを取得するメソッドです。

        Returns:
            list[PhaseStatus]:リサーチフローステータスのリスト

        """
        return ResearchFlowStatus.load_from_json(str(self.path))

    def update_file(self, research_flow_status: list[PhaseStatus]):
        """リサーチフローステータス管理JSONの更新を行うメソッドです。

        Args:
            research_flow_status (list[PhaseStatus]): 更新に用いるリサーチフローステータス管理情報

        """
        # research_flow_statusを基にリサーチフローステータス管理JSONを更新する。
        research_flow_status_data = {}
        research_flow_status_data['research_flow_phase_data'] = []

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
            research_flow_status_data['research_flow_phase_data'].append(
                phase_status_data)
        # リサーチフローステータス管理JSONをアップデート
        super().write(research_flow_status_data)

    def issue_uuidv4(self) -> str:
        """UUIDv4の発行を行うメソッドです。

        Returns:
            str:発行したUUIDを文字列に変換したもの

        """
        return str(uuid.uuid4())

    def exist_sub_flow_id_in_research_flow_status(
        self, research_flow_status: list[PhaseStatus], target_id: str
    ) -> bool:
        """リサーチフローステータス管理情報に同一のサブフローIDが存在するか確認するメソッドです。

        Args:
            research_flow_status (list[PhaseStatus]): リサーチフローステータス管理情報

        Returns:
            bool:target_idと一致するサブフローIDが存在するかの判定に用いるフラグ

        """
        for phase in research_flow_status:
            for sub_flow in phase._sub_flow_data:
                if sub_flow._id == target_id:
                    return True
        return False

    def issue_unique_sub_flow_id(self) -> str:
        """固有のサブフローIDを発行するメソッドです。

        Returns:
            str:新たに発行した固有のサブフローID

        """
        while True:
            candidate_id = self.issue_uuidv4()
            return candidate_id

    def is_unique_subflow_name(self, phase_seq_number: int, sub_flow_name: str) -> bool:
        """フェーズ内に同じ名前のサブフローが存在するかの確認を行うメソッドです。

        Args:
            phase_seq_number:フェーズシーケンス番号
            sub_flow_name:サブフロー名

        Returns:
            bool:同一のサブフロー名が存在するかのフラグ

        Raises:
            Exception:引数で指定したフェーズが存在しない

        """
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

    def is_unique_data_dir(self, phase_seq_number: int, data_dir_name: str) -> bool:
        """フェーズ内に同じ名前のデータフォルダが存在するかの確認を行うメソッドです。

        Args:
            phase_seq_number (int):フェーズシーケンス番号
            data_dir_name (str):データフォルダ名

        Returns:
            bool:同一のデータフォルダ名が存在するかのフラグ

        Raises:
            Exception:一致するフェーズが存在しない

        """
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


class ResearchFlowStatusOperater(ResearchFlowStatusFile):
    """リサーチフローステータスの参照や操作をおこなうクラスです。"""

    def get_svg_of_research_flow_status(self) -> str:
        """リサーチフローイメージのSVGデータを取得するメソッドです。

        Returns:
            str:リサーチフローイメージのSVGデータ

        """
        research_flow_status = self.load_research_flow_status()
        # Update display phase name
        research_flow_status = self.update_display_object(research_flow_status)
        fd = FlowDrawer(research_flow_status=research_flow_status)
        # generate SVG of Research Flow Image
        return fd.draw()

    def update_display_object(self, research_flow_status: list[PhaseStatus]) -> list[PhaseStatus]:
        """リサーチフローステータス管理情報を画面表示用に調整するメソッドです。

        Args:
            research_flow_status (list[PhaseStatus]):リサーチフローステータス管理情報

        Returns:
            list[PhaseStatus]:画面表示用に調整を行ったリサーチフローステータス管理情報

        """
        update_research_flow_status = []
        for phase in research_flow_status:
            phase.update_name(name=msg_config.get('research_flow_phase_display_name', phase._name))
            for sb in phase._sub_flow_data:
                sb._name = escape_html_text(sb._name)
            update_research_flow_status.append(phase)
        return update_research_flow_status

    def init_research_preparation(self):
        """研究準備ステータスの初期化を行うメソッドです。"""
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

        # リサーチフローステータス管理JSONを更新する。
        self.update_file(research_flow_status)

    def create_sub_flow(
        self, creating_phase_seq_number: int, sub_flow_name: str,
        data_dir_name: str, parent_sub_flow_ids: list[str]
    ) -> tuple[str, str]:
        """新規のサブフローを作成し、リサーチフローステータスに追加するメソッドです。

        Args:
            creating_phase_seq_number(int):サブフローを作成するフェーズのシーケンス番号
            sub_flow_name(str): 新規サブフロー名
            date_dir_name(str):作成するディレクトリ名
            parent_sub_flow_ids(list[str]):親サブフローID

        Returns:
            str:新規のサブフローを作成したフェーズの名前
            str:新しく作成したサブフローのID

        Raises:
            Exception:引数で指定しフェーズが存在しない
            Exception:新しく作成したサブフローのIDが発行できない

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

    def del_sub_flow_data_by_sub_flow_id(self, sub_flow_id: str):
        """指定したサブフローデータの削除を行うメソッドです。

        Args:
            sub_flow_id (str):削除対象となるサブフローデータのID

        Raises:
            NotFoundSubflowDataError:IDが一致するサブフローデータが存在しない

        """
        research_flow_status = self.load_research_flow_status()

        for phase_status in research_flow_status:
            remove_subflow = None
            for subflow in phase_status._sub_flow_data:
                if subflow._id == sub_flow_id:
                    remove_subflow = subflow
                    break
                else:
                    continue
            if remove_subflow is not None:
                phase_status._sub_flow_data.remove(remove_subflow)
                break
        else:
            raise NotFoundSubflowDataError(f'There Is No Subflow Data to Delete. sub_flow_id : {sub_flow_id}')
        # リサーチフローステータス管理JSONの上書き
        self.update_file(research_flow_status)

    def relink_sub_flow(self, phase_seq_number: int, sub_flow_id: str, parent_sub_flow_ids: list[str]):
        """親サブフローを変更するメソッドです。

        Args:
            phase_seq_number (int):対象のフェーズシーケンス番号
            sub_flow_id (str): 対象のサブフローID
            parent_sub_flow_ids (list[str]):変更後の親サブフローID

        Raises:
            NotFoundSubflowDataError:IDが一致するサブフローデータが存在しない

        """
        research_flow_status = self.load_research_flow_status()
        for phase_status in research_flow_status:
            if phase_status._seq_number != phase_seq_number:
                continue
            for sf in phase_status._sub_flow_data:
                if sf._id == sub_flow_id:
                    sf._parent_ids = parent_sub_flow_ids
                    break
            else:
                raise NotFoundSubflowDataError(f'There Is No Subflow Data to Relink. sub_flow_id : {sub_flow_id}')
            break
        self.update_file(research_flow_status)

    def rename_sub_flow(
        self, phase_seq_number: int, sub_flow_id: str,
        sub_flow_name: str, data_dir_name: str
    ):
        """サブフロー名とディレクトリ名を変更するメソッドです。

        Args:
            phase_seq_number (int):対象のフェーズシーケンス番号
            sub_flow_id (str):対象のサブフローID
            sub_flow_name (str):変更後のサブフロー名
            data_dir_name (str):変更後のディレクトリ名

        Raises:
            NotFoundSubflowDataError:IDが一致するサブフローデータが存在しない

        """
        research_flow_status = self.load_research_flow_status()
        for phase_status in research_flow_status:
            if phase_status._seq_number != phase_seq_number:
                continue
            for sf in phase_status._sub_flow_data:
                if sf._id == sub_flow_id:
                    sf._name = sub_flow_name
                    sf._data_dir = data_dir_name
                    break
            else:
                raise NotFoundSubflowDataError(f'There Is No Subflow Data to Rename. sub_flow_id : {sub_flow_id}')
            break
        self.update_file(research_flow_status)

    def get_flow_name_and_dir_name(self, phase_seq_number: int, id: str) -> tuple[str, str]:
        """指定したサブフローデータのサブフロー名とディレクトリ名を取得するメソッドです。

        Args:
            phase_seq_number (int):対象のフェーズシーケンス番号
            id (str):対象のサブフローID

        Returns:
            str:サブフロー名
            str:ディレクトリ名

        Raises:
            NotFoundSubflowDataError:IDが一致するサブフローデータが存在しない

        """
        research_flow_status = self.load_research_flow_status()
        for phase in research_flow_status:
            if phase._seq_number != phase_seq_number:
                continue
            for sb in phase._sub_flow_data:
                if sb._id == id:
                    return sb._name, sb._data_dir
        else:
            raise NotFoundSubflowDataError(f'There Is No Data Directory Name. sub_flow_id : {id}')

    def get_data_dir(self, phase_name: str, id: str) -> str:
        """指定したサブフローデータのディレクトリ名を取得するメソッドです。

        Args:
            phase_name (str):対象のフェーズ名
            id (str):対象のサブフローID

        Returns:
            str:ディレクトリ名

        Raises:
            NotFoundSubflowDataError:IDが一致するサブフローデータが存在しない

        """
        research_flow_status = self.load_research_flow_status()
        for phase in research_flow_status:
            if phase._name != phase_name:
                continue
            for sb in phase._sub_flow_data:
                if sb._id == id:
                    return sb._data_dir
        else:
            raise NotFoundSubflowDataError(f'There Is No Data Directory Name. sub_flow_id : {id}')

    def get_subflow_phase(self, phase_seq_number: int) -> str:
        """指定したフェーズの名前を取得するメソッドです。

        Args:
            phase_seq_number (int):対象のフェーズシーケンス番号

        Returns:
            str:フェーズ名

        Raises:
            Exception:フェーズシーケンス番号が一致するフェーズが存在しない

        """
        research_flow_status = self.load_research_flow_status()
        for phase_status in research_flow_status:
            if phase_status._seq_number == phase_seq_number:
                return phase_status._name
        else:
            raise Exception(f'There is no phase. phase_seq_number : {phase_seq_number}')

    def get_subflow_phases(self) -> list[str]:
        """リサーチフローステータスに存在する全てのフェーズ名を取得するメソッドです。

        Returns:
            list[str]:全フェーズ名のリスト

        """
        research_flow_status = self.load_research_flow_status()
        phase_list = []
        for phase_status in research_flow_status:
            phase_list.append(phase_status._name)
        return phase_list

    def get_subflow_ids(self, phase_name: str) -> list[str]:
        """指定したフェーズの全サブフローIDを取得するメソッドです。

        Args:
            phase_name (str):対象のフェーズ名

        Returns:
            list[str]:対象のフェーズに存在する全サブフローIDのリスト

        """
        research_flow_status = self.load_research_flow_status()
        id_list = []
        for phase_status in research_flow_status:
            if phase_status._name != phase_name:
                continue
            for subflow_data in phase_status._sub_flow_data:
                id_list.append(subflow_data._id)
        return id_list

    def get_phase_subflow_id_name(self):
        """研究準備を除くリサーチフローステータスに存在する全てのフェーズとサブフローID、サブフロー名を取得するメソッドです。

        Returns:
            dict: フェーズとサブフローID、サブフロー名を返す
        """
        research_flow_status = self.load_research_flow_status()
        sub_flow_dict = {}
        for phase in research_flow_status:
            if phase._name != 'plan' and phase._sub_flow_data != []:
                value = self.get_id_name(phase)
                sub_flow_dict[phase._name] = value
        return sub_flow_dict

    def get_id_name(self, phase: str) -> dict:
        """研究準備を除くリサーチフローステータスに存在する全てのサブフローID、サブフロー名を取得するメソッドです。

        Args:
            phase (str): フェーズ名

        Returns:
            dict: サブフローIDとサブフロー名の辞書を返す。
        """
        id_name_dict = {}
        for data in phase._sub_flow_data:
            id_name_dict[data._id] = data._name
        return id_name_dict
