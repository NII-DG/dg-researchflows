import traceback

import panel as pn

from .config import path_config, message as msg_config

class Button(pn.widgets.Button):

    def set_looks_init(self, name=""):
        if name:
            self.name = name
        else:
            self.name = msg_config.get('form', 'submit_select')
        self.button_type = 'primary'
        self.button_style = 'solid'

    def set_looks_processing(self, name=""):
        if name:
            self.name = name
        else:
            self.name = msg_config.get('form', 'processing')
        self.button_type = 'primary'
        self.button_style = 'outline'

    def set_looks_success(self, name):
        self.name = name
        self.button_type = 'success'
        self.button_style = 'solid'

    def set_looks_warning(self, name):
        self.name = name
        self.button_type = 'warning'
        self.button_style = 'solid'

    def set_looks_error(self, name):
        self.name = name
        self.button_type = 'danger'
        self.button_style = 'solid'


class Alert:

    @classmethod
    def info(cls, msg):
        return pn.pane.Alert(msg, sizing_mode="stretch_width",alert_type='info')

    @classmethod
    def success(cls, msg):
        return pn.pane.Alert(msg, sizing_mode="stretch_width",alert_type='success')

    @classmethod
    def warning(cls, msg):
        return pn.pane.Alert(msg, sizing_mode="stretch_width",alert_type='warning')

    @classmethod
    def error(cls, msg):
        return pn.pane.Alert(msg, sizing_mode="stretch_width",alert_type='danger')

    @classmethod
    def exception(cls):
        return pn.pane.Alert(f'## [INTERNAL ERROR] : {traceback.format_exc()}',sizing_mode="stretch_width",alert_type='danger')
