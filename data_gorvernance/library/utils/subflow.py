from pathlib import Path
from tempfile import TemporaryDirectory

from IPython.display import display, SVG

from subprocess import run
from .status import Tasks, TaskConfig


class DiagManager:

    def __init__(self, file_path: str) -> None:
        self.path = Path(file_path)

    def change_group_color(self, group_id: str, color: str):
        pass

    def update_mark(self, node_id:str, value: str):
        pass

class SVGManager:

    def __init__(self, diag_file, font_file) -> None:
        self.diag = diag_file
        self.font = font_file

    def _generate_skeleton(self, output, diag, font):
        run(['blockdiag', '-f', font, '-Tsvg', '-o', output, diag], check=True)

    def generate(self, skeleton, dir_path):
            self._generate_skeleton(skeleton, Path(self.diag), Path(self.font))
            _embed_detail_information(Path(output), skeleton, Path(dir_path))
            return output


class SubFlow(DiagManager, SVGManager):

    def __init__(self, diag_path: str, font) -> None:
        DiagManager.__init__(self, diag_path)
        SVGManager.__init__(self, diag_path, font)


    def update(self, tasks: Tasks, display_all=True):
        for task in tasks.config:
            self.adjust_by_status(task)
            if not display_all:
                self.adjust_by_disabled

    def adjust_by_disabled(self, task: TaskConfig):
        pass

    def adjust_by_status(self, task: TaskConfig):
        if task.status == task.STATUS_UNFEASIBLE:
            self.change_group_color(task.id, "#77787B")
        elif task.status == task.STATUS_DONE:
            self.update_mark(task.id, "実行中")
        elif task.status == task.STATUS_DOING:
            self.update_mark(task.id, "実行完了")

    def render(self, dir_path):
        with TemporaryDirectory() as workdir:
            skeleton = Path(workdir) / 'skeleton.svg'
            self.generate(skeleton, dir_path)
            display(SVG(filename=skeleton))
