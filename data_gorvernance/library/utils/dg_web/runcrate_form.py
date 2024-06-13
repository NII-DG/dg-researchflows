import panel as pn

from library.utils.widgets import MessageBox
from .form import Checkbox, Title, Description


class RunCrateForm:

    key = "runCrate"

    def __init__(self):
        pn.extension()
        self.form_box = pn.WidgetBox()
        self.msg_output = MessageBox()
        # jsonschemaの定義部分。property value
        self.definition = {}
        # runcrateのファイルの情報 {filename: link}
        self.files = {}
        # 表示するwidget群を保持する。値の取得に使用する
        self.widgets = {}

    def pop_schema(self, schema):
        """schemaのRunCrate選択部分を取得し、schemaから取り除く"""
        properties = schema.get('properties', {})
        self.definition = properties.pop(self.key, {})
        return schema

    def create_widget(self, files:dict, data:dict):
        """RunCrate選択の入力欄を生成する"""
        if not files:
            return
        self.files = files
        title = self.definition.get("title", self.key)
        self.form_box.append(Title(title))
        description = self.definition.get("description")
        if description is not None:
            self.form_box.append(Description(description))
        column = pn.Column(margin=(5, 10, 5, 10))
        for filename, filelink in files.items():
            widget = None
            links = data.get(self.key, [])
            if filelink in links:
                widget = Checkbox(name=filename, value=True)
            else:
                widget = Checkbox(name=filename, value=False)
            column.append(widget)
        self.form_box.append(column)
        self.widgets[self.key] = column

    def get_data(self):
        """RunCrate選択の入力値からデータを生成する"""
        data = {}
        for key, contents in self.widgets.items():
            value = []
            for widget in contents:
                if widget.value:
                    value.append(self.files[widget.name])
            data[key] = value
        return data