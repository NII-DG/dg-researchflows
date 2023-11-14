import logging
from logging import FileHandler
import os
from pathlib import Path
import datetime

from .config import path_config
from ..subflow.subflow import get_subflow_type_and_id


class BaseLogger:

    def __init__(self, log_file: str):
        self.logger = logging.getLogger(__name__)
        self.date = datetime.datetime.now().strftime('%Y%m%d')
        self.file_name = log_file
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
        log_file = self.file_name + "." + self.date
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
        # set log config
        log_file = self._get_log_file_path(nb_working_file)
        super().__init__(str(log_file))
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

    def _get_log_file_path(self, nb_working_file):
        root_folder = Path(
            path_config.get_abs_root_form_working_dg_file_path(nb_working_file)
        )
        log_dir = os.environ['JUPYTERHUB_SERVER_NAME']
        log_file_name = 'log'
        log_file_path = (root_folder / path_config.DG_LOG_FOLDER / log_dir / log_file_name)
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        return log_file_path

    def _get_format(self):
        fmt = '%(levelname)s\t%(asctime)s\t%(username)s\t'
        if self.subflow_id:
            fmt += '%(subflow_id)s\t'
        fmt += '%(subflow_type)s\t%(ipynb_name)s\t'
        if self.cell_id:
            fmt += '%(cell_id)s\t'
        fmt += '%(message)s'
        return fmt

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

