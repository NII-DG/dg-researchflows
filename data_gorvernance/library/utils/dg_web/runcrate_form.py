import traceback

import panel as pn

from library.utils.widgets import MessageBox, Button


class RunCrateForm:

    def __init__(self):

        pn.extension()
        self.form_box = pn.WidgetBox()
        self.msg_output = MessageBox()

        self.schema = None

    def pop_schema(self, schema):
        """schemaのRunCrate選択部分を取得し、schemaから取り除く"""
        properties = schema.get('properties', {})
        self.schema = properties.pop("runCrate", None)
        return schema

    def create_widget(self, data):
        """RunCrate選択の入力欄を生成する"""
        pass

    def get_data(self):
        """RunCrate選択の入力値からデータを生成する"""
        return {}