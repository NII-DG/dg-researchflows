import logging
from logging import FileHandler
import os
from pathlib import Path
import datetime

from ..config import path_config
from ..setting import get_subflow_type_and_id


class BaseLogger:

    def __init__(self, output_dir="."):
        self.logger = logging.getLogger(__name__)
        self.date = datetime.datetime.now().strftime('%Y%m%d')
        self.log_dir = output_dir
        self._update_handler()

    def reset_file(self, fmt):
        now_date = datetime.datetime.now().strftime('%Y%m%d')
        if self.date != now_date:
            self.date = now_date
            self._update_handler()
        self.set_formatter(fmt)

    def _update_handler(self):
        if self.logger.hasHandlers():
            handler = self.logger.handlers[0]
            self.logger.removeHandler(handler)
        log_file = self.date + ".log"
        log_file = os.path.join(self.log_dir, log_file)
        self.handler = FileHandler(log_file)
        self.logger.addHandler(self.handler)

    def set_formatter(self, fmt:str):
        formatter = logging.Formatter(fmt)
        self.handler.setFormatter(formatter)

    def set_log_level(self, level):
        if level == 'debug':
            self.logger.setLevel(logging.DEBUG)
        elif level == 'info':
            self.logger.setLevel(logging.INFO)
        elif level == 'warning':
            self.logger.setLevel(logging.WARNING)
        elif level == 'error':
            self.logger.setLevel(logging.ERROR)
        elif level == 'critical':
            self.logger.setLevel(logging.CRITICAL)

class UserActivityLog(BaseLogger):

    def __init__(self, nb_working_file, notebook_name):
        """
        Args:
            nb_working_file (str): ノートブック名を含む絶対パス
        """
        # set log config
        log_dir = self._get_log_dir(nb_working_file)
        super().__init__(log_dir)
        self.set_log_level('info')
        # set items
        self.username = os.environ['JUPYTERHUB_USER']
        self.ipynb_file = os.path.join(
            os.path.dirname(nb_working_file), notebook_name
        )
        subflow_type, subflow_id = get_subflow_type_and_id(nb_working_file)
        self.subflow_id = subflow_id
        self.subflow_type = subflow_type
        self.cell_id = ""

    def _get_log_dir(self, nb_working_file):
        root_folder = Path(
            path_config.get_abs_root_form_working_dg_file_path(nb_working_file)
        )
        log_dir = os.environ['JUPYTERHUB_SERVER_NAME']
        log_dir = (root_folder / path_config.DG_LOG_FOLDER / log_dir)
        os.makedirs(log_dir, exist_ok=True)
        return str(log_dir)

    def _get_format(self):
        return '%(levelname)s\t%(asctime)s\t%(username)s\t%(subflow_id)s\t%(subflow_type)s\t%(ipynb_name)s\t%(cell_id)s\t%(message)s'

    def info(self, message):
        self.reset_file(self._get_format())
        self.logger.info(message, extra=self.record())

    def warning(self, message):
        self.reset_file(self._get_format())
        self.logger.warning(message, extra=self.record())

    def error(self, message):
        self.reset_file(self._get_format())
        self.logger.error(message, extra=self.record())

    def start_cell(self, message=''):
        self.info("-- 処理開始 --" + message)

    def finish_cell(self, message=''):
        self.info("-- 処理終了 --" + message)

    def record(self):

        return {
            'username': self.username,
            'subflow_id': self.subflow_id,
            'subflow_type':self.subflow_type,
            'ipynb_name': self.ipynb_file,
            'cell_id': self.cell_id
        }

