import os

from ..utils.setting import SubflowStatusFile, SubflowTask
from ..utils import file
from ..utils.diagram import DiagManager, init_config, update_svg
from ..utils.config import path_config


script_dir = os.path.dirname(os.path.abspath(__file__))


class SubFlowManager:

    def __init__(self, current_dir: str, status_file :str, diag_file :str, using_task_dir: str) -> None:
        self.current_dir = current_dir
        self.tasks = SubflowStatusFile(status_file).read().tasks
        self.diag_file = diag_file
        self.task_dir = using_task_dir

    def setup_tasks(self, souce_task_dir: str):
        if os.path.isdir(souce_task_dir):
            for task in self.tasks:
                self._copy_file_by_name(task.name, souce_task_dir, self.task_dir)

    def _copy_file_by_name(self, target_file: str, search_directory :str, destination_directory: str):
        for root, dirs, files in os.walk(search_directory):
            for filename in files:
                if not filename.startswith(target_file):
                    continue
                # if filename.startswith(target_file) のとき
                source_dir = root
                relative_path = file.relative_path(root, search_directory)
                destination_dir = os.path.join(destination_directory, relative_path)

                source_file = os.path.join(source_dir, filename)
                destination_file = os.path.join(destination_dir, filename)
                if not os.path.isfile(destination_file):
                    file.copy_file(source_file, destination_file)

                source_images = os.path.join(source_dir, path_config.IMAGES)
                destination_images = os.path.join(destination_dir, path_config.IMAGES)
                if not os.path.isdir(destination_images):
                    file.copy_dir(source_images, destination_images, overwrite=True)


    def generate(self, svg_path: str, tmp_diag: str, font: str, display_all=True):
        # 毎回元ファイルを読み込む
        self.diag = DiagManager(self.diag_file)
        # tmp_diagは暫定的なもの。将来的にはself.diagを利用できるようにする
        self.svg_config = {}
        for task in self.tasks:
            self.svg_config.update(init_config(task.id, task.name))
        self._update(display_all)
        self.diag.generate_svg(tmp_diag, svg_path, font)
        update_svg(svg_path, self.current_dir, self.task_dir, self.svg_config)

    def _update(self, display_all=True):
        for task in self.tasks:
            self._adjust_by_status(task, display_all)
            self._adjust_by_optional(task, display_all)

    def _adjust_by_optional(self, task: SubflowTask, display_all=True):
        if task.disable:
            if display_all:
                #self.diag.update_node_style(task.id, 'dotted')
                pass
            else:
                # self.diag.delete_node(task.id)
                # 以下暫定処理
                self.diag.update_node_color(task.id, "#77787B")
                self.svg_config[task.id]['is_link'] = False

    def _adjust_by_status(self, task: SubflowTask, display_all=True):
        if task.disable and not display_all:
            return

        if task.is_multiple:
            self.diag.update_node_stacked(task.id)

        if task.status == task.STATUS_UNFEASIBLE:
            self.diag.update_node_color(task.id, "#e6e5e3")
            self.svg_config[task.id]['is_link'] = False
            return

        icon_dir = "../data/icon"
        icon_dir = os.path.abspath(os.path.join(script_dir, icon_dir))
        icon_dir = file.relative_path(icon_dir, self.current_dir)
        if task.status == task.STATUS_DONE:
            self.diag.update_node_icon(task.id, icon_dir + "/check_mark.png")
        elif task.status == task.STATUS_DOING:
            self.diag.update_node_icon(task.id, icon_dir + "/loading.png")
            self.svg_config[task.id]['init_nb'] = False

