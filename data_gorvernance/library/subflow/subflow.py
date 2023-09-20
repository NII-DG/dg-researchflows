import os
from pathlib import Path

from .status import StatusFile, SubflowStatus, TaskStatus
from ..utils import file
from ..utils.file import File
from ..utils.diagram import DiagManager, generate_svg_diag
from ..utils.config import path_config as p


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

    def update_status(self):
        self.subflow_status.update_task_unexcuted()

    def generate(self, workdir, font, display_all=True):
        self._update_flow(self.diag, self.subflow_status, display_all)
        tmp_diag = Path(workdir) / 'skeleton.diag'
        File(str(tmp_diag)).write(self.diag.content)
        skeleton = Path(workdir) / 'skeleton.svg'
        generate_svg_diag(str(skeleton), str(tmp_diag), font, self.current_path, self.task_dir)

    def _update_flow(self, diag: DiagManager, status: SubflowStatus, display_all=True):
        for task in status.tasks:
            self._adjust_by_status(diag, task)
            self._adjust_by_optional(diag, task, display_all)

    def _adjust_by_optional(self, diag: DiagManager, task: TaskStatus, display_all=True):
        if task.disable:
            if display_all:
                diag.change_node_style(task.id, 'dotted')
            else:
                diag.delete_node(task.id)

    def _adjust_by_status(self, diag: DiagManager, task: TaskStatus):
        if task.status == task.STATUS_UNFEASIBLE:
            diag.change_group_color(task.id, "#77787B")
        elif task.status == task.STATUS_DONE:
            diag.update_mark(task.id, "実行中")
        elif task.status == task.STATUS_DOING:
            diag.update_mark(task.id, "実行完了")
