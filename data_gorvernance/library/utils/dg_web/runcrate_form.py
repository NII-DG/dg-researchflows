import panel as pn

from library.utils.widgets import MessageBox
from .form import Checkbox, Title, Description


class RunCrateForm:
    """RunCrateの入力フォームの操作

    Attributes:
        key (str): クラス属性。metadataのRunCrateの情報をもつ部分のキー値
        definition (dict): jsonschemaの定義部分。property value
        files (dict): runcrateのファイルの情報。{filename: link}
        widgets (dict): 表示するwidget群を保持する。値の取得に使用する。
        form_box (pn.WidgetBox): フォームを格納する。
        msg_output (MessageBox): ユーザーに提示するメッセージを格納する。

    Methods:
        pop_schema(schema): jsonschemaから該当する部分を取得する
        create_widgets(crates, data): 入力フォームの作成
        get_data(): 入力されたデータの取得
    """

    key = "runCrate"

    def __init__(self):
        self.definition = {}
        self.files = {}
        self.widgets = {}

        pn.extension()
        self.form_box = pn.WidgetBox()
        self.msg_output = MessageBox()

    def pop_schema(self, schema):
        """schemaのRunCrate選択部分を取得し、schemaから取り除く"""
        properties = schema.get('properties', {})
        self.definition = properties.pop(self.key, {})
        return schema

    def create_widget(self, crates: list, data: dict):
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
