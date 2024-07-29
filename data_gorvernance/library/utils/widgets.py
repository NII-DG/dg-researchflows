import panel as pn

from .config import message as msg_config


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


class Alert(pn.pane.Alert):

    @classmethod
    def info(cls, msg=""):
        return cls(msg, sizing_mode="stretch_width", alert_type='info')

    @classmethod
    def success(cls, msg=""):
        return cls(msg, sizing_mode="stretch_width", alert_type='success')

    @classmethod
    def warning(cls, msg=""):
        return cls(msg, sizing_mode="stretch_width", alert_type='warning')

    @classmethod
    def error(cls, msg=""):
        return cls(msg, sizing_mode="stretch_width", alert_type='danger')


class MessageBox(pn.WidgetBox):

    def has_message(self):
        if self.objects:
            return True
        else:
            return False

    def update_info(self, msg=""):
        self.clear()
        alert = Alert.info(msg)
        self.append(alert)
        return alert

    def update_success(self, msg=""):
        self.clear()
        alert = Alert.success(msg)
        self.append(alert)
        return alert

    def update_warning(self, msg=""):
        self.clear()
        alert = Alert.warning(msg)
        self.append(alert)
        return alert

    def update_error(self, msg=""):
        self.clear()
        alert = Alert.error(msg)
        self.append(alert)
        return alert

    def add_info(self, msg=""):
        alert = Alert.info(msg)
        self.append(alert)
        return alert

    def add_success(self, msg=""):
        alert = Alert.success(msg)
        self.append(alert)
        return alert

    def add_warning(self, msg=""):
        alert = Alert.warning(msg)
        self.append(alert)
        return alert

    def add_error(self, msg=""):
        alert = Alert.error(msg)
        self.append(alert)
        return alert
