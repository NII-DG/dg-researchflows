import os

from .status import StatusFile, TaskStatus
from ..utils import file
from ..utils.diagram import DiagManager, add_link
from ..utils.config import path_config
from ..main_menu.research_flow_status import ResearchFlowStatusOperater


def get_subflow_type_and_id(working_file_path: str):
    """ノートブックのパスを受け取ってsubflowの種別とidを返す

    Args:
        working_file_path (str): ノートブックのパス

    Raises:
        ValueError: working_file_pathにsubflow_typeが含まれない場合

    Returns:
        str: サブフロー種別
        str: サブフローID（無い場合はNone）
    """
    parts = os.path.normpath(working_file_path).split(os.sep)
    target_directory = path_config.RESEARCHFLOW
    subflow_type = ""
    subflow_id = None

    try:
        index = parts.index(target_directory)
    except:
        raise

    if index < len(parts) - 1:
        subflow_type = parts[index + 1]
    else:
        raise ValueError

    if index + 2 < len(parts) - 1:
        abs_root = path_config.get_abs_root_form_working_dg_file_path(working_file_path)
        id_list = ResearchFlowStatusOperater(
                    path_config.get_research_flow_status_file_path(abs_root)
                ).get_subflow_ids(subflow_type)
        dir_name = parts[index + 2]
        if dir_name in id_list:
            subflow_id = dir_name

    return subflow_type, subflow_id


def get_return_sub_flow_menu_relative_url_path(working_file_path: str)->str:
    subflow_type, subflow_id = get_subflow_type_and_id(working_file_path)
    if subflow_id is None:
        menu_path = path_config.get_sub_flow_menu_path(subflow_type)
        return os.path.join('../../../../..', menu_path)
    else:
        menu_path = path_config.get_sub_flow_menu_path(subflow_type, subflow_id)
        return os.path.join('../../../../../..', menu_path)


class SubFlow:

    def __init__(self, current_dir: str, status_file :str, diag_file :str, using_task_dir: str) -> None:
        self.current_dir = current_dir
        self.tasks = StatusFile(status_file).read().tasks
        self.diag = DiagManager(diag_file)
        self.task_dir = using_task_dir

    def setup_tasks(self, souce_task_dir: str):
        if os.path.isdir(souce_task_dir):
            for task in self.tasks:
                self._copy_file_by_name(task.name, souce_task_dir, self.task_dir)

    def _copy_file_by_name(self, target_file: str, search_directory :str, destination_directory: str):
        for root, dirs, files in os.walk(search_directory):
            for filename in files:
                if filename.startswith(target_file):
                    source_path = os.path.join(root, filename)
                    relative_path = file.relative_path(root, search_directory)
                    destination_path = os.path.join(destination_directory, relative_path, filename)
                    if not os.path.isfile(destination_path):
                        file.copy_file(source_path, destination_path)

    def generate(self, svg_path: str, tmp_diag: str, font: str, display_all=True):
        # tmp_diagは暫定的なもの。将来的にはself.diagを利用できるようにする
        self._update_diag(display_all)
        self.diag.generate_svg(tmp_diag, svg_path, font)
        task_dict = {task.id: task.name for task in self.tasks}
        add_link(svg_path, self.current_dir, self.task_dir, task_dict)

    def _update_diag(self, display_all=True):
        for task in self.tasks:
            self._adjust_by_status(task)
            self._adjust_by_optional(task, display_all)

    def _adjust_by_optional(self, task: TaskStatus, display_all=True):
        if task.disable:
            if display_all:
                self.diag.change_node_style(task.id, 'dotted')
            else:
                self.diag.delete_node(task.id)

    def _adjust_by_status(self, task: TaskStatus):
        if task.status == task.STATUS_UNFEASIBLE:
            self.diag.change_group_color(task.id, "#77787B")
        elif task.status == task.STATUS_DONE:
            self.diag.update_mark(task.id, "実行中")
        elif task.status == task.STATUS_DOING:
            self.diag.update_mark(task.id, "実行完了")
