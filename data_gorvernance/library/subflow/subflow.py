import os
from pathlib import Path

from .status import StatusFile, SubflowStatus, TaskStatus
from ..utils import file
from ..utils.file import File
from ..utils.diagram import DiagManager, add_link
from ..utils.config import path_config
from ..main_menu import ResearchFlowStatusOperater


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
                ).get_subflow_id(subflow_type)
        dir_name = parts[index + 2]
        if dir_name in id_list:
            subflow_id = dir_name

    return subflow_type, subflow_id


class SubFlow:

    def __init__(self, current_path: str, status_file :str, diag_file :str, using_task_dir: str) -> None:
        self.current_path = current_path
        self.subflow_status = StatusFile(status_file).read()
        self.diag = DiagManager(diag_file)
        self.task_dir = using_task_dir

    def setup_tasks(self, souce_task_dir: str):
        if os.path.isdir(self.task_dir):
            for task in self.subflow_status.tasks:
                self._copy_file_by_name(task.name + '.ipynb', souce_task_dir, self.task_dir)

    def _copy_file_by_name(self, target_filename: str, search_directory :str, destination_directory: str):
        for root, dirs, files in os.walk(search_directory):
            if target_filename in files:
                source_path = os.path.join(root, target_filename)
                relative_path = os.path.relpath(root, start=search_directory)
                destination_path = os.path.join(destination_directory, relative_path, target_filename)
                if not os.path.isfile(destination_path):
                    file.copy_file(source_path, destination_path)

    def generate(self, svg_path, tmp_diag, font, display_all=True):
        # tmp_diagは暫定的なもの。将来的にはself.diagを利用できるようにする
        self._update_diag(display_all)
        self.diag.generate_svg(tmp_diag, svg_path, font)
        add_link(str(svg_path), self.current_path, self.task_dir)

    def _update_diag(self, display_all=True):
        for task in self.subflow_status.tasks:
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
