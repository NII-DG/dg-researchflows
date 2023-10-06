import logging
from logging.handlers import TimedRotatingFileHandler
import os
from pathlib import Path

from .config import path_config
from ..subflow.subflow import get_subflow_type_and_id


class BaseLogger:

    def __init__(self, log_file, backupCount=0, when='midnight'):
        self.logger = logging.getLogger(__name__)
        self.handler = TimedRotatingFileHandler(log_file, when=when, backupCount=backupCount)
        self.logger.addHandler(self.handler)

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

    def set_formatter(self, fmt):
        formatter = logging.Formatter(fmt)
        self.handler.setFormatter(formatter)


class UserActivityLog(BaseLogger):

    def __init__(self, nb_working_file, notebook_name):
        # set log config
        log_file = self._get_log_file_path(nb_working_file)
        super().__init__(log_file)
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
        # set format
        fmt = '%(levelname)s\t%(asctime)s\t%(username)s\t'
        if self.subflow_id:
            fmt += '%(subflow_id)s\t'
        fmt += '%(subflow_type)s\t%(ipynb_name)s\t%(cell_id)s\t%(message)s'
        self.set_formatter(fmt)

    def _get_log_file_path(self, nb_working_file):
        root_folder = Path(
            path_config.get_abs_root_form_working_dg_file_path(nb_working_file)
        )
        log_dir = os.environ['JUPYTERHUB_SERVER_NAME']
        log_file_name = 'log'
        log_file_path = (root_folder / path_config.DG_LOG_FOLDER / log_dir / log_file_name)
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        return log_file_path

    def info(self, message):
        self.logger.info(message, extra=self.record())

    def warning(self, message):
        self.logger.warning(message, extra=self.record())

    def error(self, message):
        self.logger.error(message, extra=self.record())

    def record(self):
        return {
            'username': self.username,
            'subflow_id': self.subflow_id,
            'subflow_type':self.subflow_type,
            'ipynb_name': self.ipynb_file,
            'cell_id': self.cell_id
        }

