from pathlib import Path
from tempfile import TemporaryDirectory

from IPython.display import display, SVG

from . import file
from .file import JsonFile
from .diagram import DiagManager, generate_svg_diag
from .status import StatusFile, Tasks, TaskConfig

class SubFlow:

    def __init__(self) -> None:
        pass

    def render(self, diag_file, status_file, notebook_dir, abs_current, font, display_all=True):
        diag = DiagManager(diag_file)
        tasks = StatusFile(status_file).read()
        self._update(diag, tasks, display_all)
        with TemporaryDirectory() as workdir:
            tmp_diag = Path(workdir) / 'skeleton.diag'
            file.copy_file(diag, tmp_diag)
            skeleton = Path(workdir) / 'skeleton.svg'
            generate_svg_diag(skeleton, tmp_diag, font, abs_current,notebook_dir)
            display(SVG(filename=skeleton))

    def _update(self, diag: DiagManager, tasks: Tasks, display_all=True):
        for task in tasks.config:
            self._adjust_by_status(diag, task)
            if not display_all:
                self._adjust_by_disabled

    def _adjust_by_disabled(self, diag: DiagManager, task: TaskConfig):
        if task.disabled:
            pass

    def _adjust_by_status(self, diag: DiagManager, task: TaskConfig):
        if task.status == task.STATUS_UNFEASIBLE:
            diag.change_group_color(task.id, "#77787B")
        elif task.status == task.STATUS_DONE:
            diag.update_mark(task.id, "実行中")
        elif task.status == task.STATUS_DOING:
            diag.update_mark(task.id, "実行完了")
