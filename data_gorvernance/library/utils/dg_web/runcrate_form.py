import panel as pn

from library.utils.widgets import MessageBox
from .form import Checkbox, Title, Description


class RunCrateForm:
    """RunCrateの入力フォームの操作クラス"""

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

    def create_widget(self, crates:list, data:dict):
        """RunCrate選択の入力欄を生成する

        Args:
            crates (list): index.jsonの内容
            data (dict): metadata
        """
        # データの整形
        files = {}
        try:
            for crate in crates:
                for link in crate["links"]:
                    if link["rel"] == "web":
                        files[crate["name"]] = link["href"]
                        break
        except KeyError:
            return
        if not files:
            return
        # 入力欄の生成
        self.files = files
        title = self.definition.get("title", self.key)
        self.form_box.append(Title(title))
        description = self.definition.get("description")
        if description is not None:
            self.form_box.append(Description(description))
        column = pn.Column(margin=(5, 10, 5, 10))
        for filename, filelink in self.files.items():
            links = data.get(self.key, [])
            if filelink in links:
                column.append(Checkbox(name=filename, value=True))
            else:
                column.append(Checkbox(name=filename, value=False))
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
