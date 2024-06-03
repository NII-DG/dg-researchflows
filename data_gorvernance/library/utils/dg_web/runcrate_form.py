import traceback

import panel as pn

from library.utils.widgets import MessageBox, Button


class RunCrateForm:

    def __init__(self):

        pn.extension()
        self.form_box = pn.WidgetBox()
        self.msg_output = MessageBox()


    def pop_schema(self, schema):
        properties = schema.get('properties', {})
        self.schema = properties.pop("runCrate", None)
        return schema

    def create_widget(self, data):
        pass

    def get_data(self):
        return {}