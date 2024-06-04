import traceback

import panel as pn

from library.utils.widgets import MessageBox, Button

# (vertical, horizontal)
# (top, right, bottom, and left)
margin = (0, 15, 5, 15)


class TextInput(pn.widgets.TextInput):

    def __init__(self, **params):
        if 'schema_key' in params:
            self.schema_key = params.pop('schema_key')
        if "margin" not in params:
            params["margin"] = margin
        super().__init__(**params)


class Select(pn.widgets.Select):

    def __init__(self, **params):
        if 'schema_key' in params:
            self.schema_key = params.pop('schema_key')
        if "margin" not in params:
            params["margin"] = margin
        super().__init__(**params)


class IntInput(pn.widgets.IntInput):

    def __init__(self, **params):
        if 'schema_key' in params:
            self.schema_key = params.pop('schema_key')
        if "margin" not in params:
            params["margin"] = margin
        super().__init__(**params)


class Checkbox(pn.widgets.Checkbox):

    def __init__(self, **params):
        if 'schema_key' in params:
            self.schema_key = params.pop('schema_key')
        if "margin" not in params:
            params["margin"] = (10, 10, 0, 10)
        super().__init__(**params)


class Title(pn.pane.Markdown):

    def __init__(self, object=None, **params):
        if 'schema_key' in params:
            self.schema_key = params.pop('schema_key')
        if "margin" not in params:
            params["margin"] = (10, 10, 0, 10)
        if object:
            object = "### " + object
        super().__init__(object=object, **params)

    def set_text(self, text):
        self.object = f"### {text}"

class Description(pn.pane.Markdown):

    def __init__(self, object=None, **params):
        if 'schema_key' in params:
            self.schema_key = params.pop('schema_key')
        if "margin" not in params:
            params["margin"] = (0, 20, 0, 10)
        super().__init__(object=object, **params)

class Column(pn.Column):
    """タイトルや入力欄をまとめる"""

    def __init__(self, **params):
        if 'schema_key' in params:
            self.schema_key = params.pop('schema_key')
        if "margin" not in params:
            params["margin"] = (5, 10, 5, 10)
        super().__init__(**params)

class ArrayBox(pn.WidgetBox):

    def __init__(self, **params):
        if 'schema_key' in params:
            self.schema_key = params.pop('schema_key')
        if "margin" not in params:
            params["margin"] = 15
        super().__init__(**params)

class ObjectBox(pn.WidgetBox):

    def __init__(self, **params):
        if 'schema_key' in params:
            self.schema_key = params.pop('schema_key')
        if "margin" not in params:
            params["margin"] = 10
        super().__init__(**params)

class Form:

    def __init__(self):

        pn.extension()
        self.form_box = pn.WidgetBox()
        self.msg_output = MessageBox()

    def create_widgets(self, schema:dict, data:dict):
        """jsonchemaの形式にそった入力欄をpanelで作成する

        Args:
            schema (dict): jsonschema
            data (dict): jsonschemaの形式に沿った初期値
        """
        self.schema = schema
        for key, properties in schema["properties"].items():
            value = data.get(key)
            self.form_box.append(self._generate_widget(properties, key, value))

    def _generate_widget(self, definition:dict, key:str, value=None):
        """jsonschemaの設定値からpanelのwidgetを作成する

        Args:
            definition (dict): jsonschemaのkeyに対する定義部分. property value.
            key (str): jsonschemaのproperty key
            value (Any, optional): keyに対する初期値. Defaults to None.

        Returns:
            PanelのWidget
        """
        title = definition.get("title", key)
        if value is None:
            value = definition.get("default")
        form = Column(schema_key=key)

        widget = None
        if "enum" in definition and "string" in definition.get("type", ""):
            options = [""] + definition["enum"]
            if isinstance(value, str):
                widget = Select(schema_key=key, value=value, options=options)
            else:
                widget = Select(schema_key=key, options=options)
        elif definition.get("type") == "array":
            return self._genetate_array_widget(
                    definition=definition, title=title, key=key, values=value
                )
        elif definition.get("type") == "object":
            return self._generate_object_widget(
                    definition=definition, title=title, key=key, values=value
                )
        elif definition.get("type") == "number":
            if isinstance(value, int):
                widget = IntInput(schema_key=key, value=value)
            else:
                widget = IntInput(schema_key=key)
        elif definition.get("type") == "boolean":
            if isinstance(value, bool):
                widget = Checkbox(name=title, schema_key=key, value=value)
            else:
                widget = Checkbox(name=title, schema_key=key)
            form.append(widget)
            description = definition.get("description")
            if description is not None:
                form.append(Description(description, schema_key=key))
            return form
        elif "string" in definition.get("type", ""):
            if isinstance(value, str):
                widget = TextInput(schema_key=key, value=value, value_input=value)
            else:
                widget = TextInput(schema_key=key)
        else:
            self.msg_output.add_warning(f'name: {title}\ntype: {definition.get("type")}')

        title = Title(title, schema_key=key)
        form.append(title)
        description = definition.get("description")
        if description is not None:
            form.append(Description(description, schema_key=key))
        form.append(widget)

        return form

    def _generate_object_widget(self, definition:dict, title:str, key:str, values):
        """type: objectをwidgetbox化する

        Args:
            definition (dict): jsonschemaのkeyに対する定義部分. property value.
            title (str): keyに対応する表示名
            key (str): schemaのkey
            value (Any): keyに対する初期値

        Returns:
            ObjectBox
        """
        obj_box = ObjectBox(schema_key=key)
        obj_box.append(Title(title, schema_key=key))
        description = definition.get("description")
        if description is not None:
            obj_box.append(Description(description, schema_key=key))
        for i_key, properties in definition["properties"].items():
            if isinstance(values, dict):
                value = values.get(i_key)
            else:
                value = None
            obj_box.append(self._generate_widget(properties, i_key, value))
        return obj_box

    def _genetate_array_widget(self, definition:dict, title:str, key:str, values):
        """type: arrayをwidgetbox化する

        Args:
            definition (dict): jsonschemaのkeyに対する定義部分. property value.
            title (str): keyに対応する表示名
            key (str): schemaのkey
            value (Any): keyに対する初期値

        Returns:
            ArrayBox
        """
        box = ArrayBox(schema_key=key)
        box.append(Title(title, schema_key=key))
        description = definition.get("description")
        if description is not None:
            box.append(Description(description, schema_key=key))
        column = pn.Column()

        def create_items(value=None):
            """arrayのひとつの要素を作成する"""
            column_list = column.objects
            items = definition["items"]
            title_num = title + str(len(column_list) + 1)
            items["title"] = title_num
            widget = self._generate_widget(items, key, value)
            if items.get("type") == "object":
                return pn.Row(widget, create_remove_button(widget))
            else:
                return pn.Row(widget, create_remove_button(widget, align='end'))

        def create_remove_button(widget, align='start'):
            """arrayの選択した要素を削除するボタンを生成する"""
            remove_button = Button(name='Remove', button_type='danger', button_style='outline', align=align)
            def remove_item(event):
                try:
                    objects = column.objects
                    column.clear()
                    if len(objects) <= 1:
                        return
                    # 指定されたwidgetを削除
                    index = 0
                    for i, obj in enumerate(objects):
                        now = obj[0]
                        if now == widget:
                            index = i
                            break
                    objects.pop(index)
                    # 表示を更新
                    # TODO: value_inputが引き継げていない
                    for i, row in enumerate(objects):
                        title_num = title + str(i + 1)
                        w = row[0]
                        if isinstance(w, pn.Column) or isinstance(w, pn.WidgetBox):
                            wb_list = w.objects
                            wb_list[0].set_text(title_num)
                            w.clear()
                            w.extend(wb_list)
                        column.append(row)
                except Exception as e:
                    message = f'## [INTERNAL ERROR] : {traceback.format_exc()}'
                    self.msg_output.update_error(message)
            remove_button.on_click(remove_item)
            return remove_button

        def add_item(event):
            column.append(create_items())

        if (not isinstance(values, list)) or (len(values) < 1):
            # 初期値がない場合
            column.append(create_items())
        else:
            for value in values:
                column.append(create_items(value))

        box.append(column)

        add_button = Button(name='Add', button_type='primary', button_style='outline')
        add_button.on_click(add_item)
        box.append(add_button)

        return box

    def is_not_input_widget(self, widget):
        """値を取得するwidgetでないかどうかを判定する"""
        result = False
        if isinstance(widget, pn.pane.Markdown):
            result = True
        elif isinstance(widget, Button):
            result = True
        return result

    def get_data(self):
        """入力欄からデータを取得する"""
        widgets = self.form_box.objects
        schema = self.schema["properties"]
        data = {}
        for widget in widgets:
            if self.is_not_input_widget(widget):
                continue
            data.update(self._get_property(widget, schema))
        return data

    def _get_property(self, widget, schema:dict):
        """各widgetからデータを取得する

        Args:
            widget (Any): データを取得したいwidget
            schema (dict): widgetに対応するプロパティ定義
        """
        key = widget.schema_key
        value = ""
        definition:dict = schema[key]

        try:
            key = widget.schema_key
            value = ""
            if isinstance(widget, ArrayBox):
                value = self._get_array_value(widget, schema)
            elif isinstance(widget, ObjectBox):
                value = self._get_object_value(widget, schema)
            elif isinstance(widget, pn.Column):
                value = self._get_value(widget)
            else:
                raise Exception(f'widget: {widget}')

        except Exception as e:
            message = f'{str(e)}\nkey: {key}\nvalue: {value}'
            raise Exception(message)

        default = definition.get("default")
        if value or (default is not None):
            return {key: value}
        else:
            return {}

    def _get_value(self, widget: pn.Column):
        objects = widget.objects
        value = None
        for w in objects:
            if self.is_not_input_widget(w):
                continue
            if isinstance(w, TextInput):
                value = w.value_input
            elif isinstance(w, pn.widgets.Widget):
                value = w.value
            break
        return value

    def _get_object_value(self, widget: ObjectBox, schema: dict):
        """ObjectBox内のwidgetの値を取得する

        Args:
            widget (ObjectBox): データを取得したいObjectBox
            schema (dict): widgetに対応するプロパティ定義

        Returns:
            list: arrayのvalue群
        """
        objects = widget.objects
        key = widget.schema_key
        value = {}
        properties = schema[key]["properties"]
        for w in objects:
            if self.is_not_input_widget(w):
                continue
            value.update(self._get_property(w, properties))
        return value

    def _get_array_value(self, widget: ArrayBox, schema: dict):
        """ArrayBox内のwidgetの値を取得する

        Args:
            widget (ArrayBox): データを取得したいArrayBox
            schema (dict): widgetに対応するプロパティ定義

        Returns:
            list: arrayのvalue群
        """
        objects = widget.objects
        key = widget.schema_key
        value = []
        items = {key: schema[key]["items"]}
        for w in objects:
            if not isinstance(w, pn.Column):
                continue
            # Columnがあったら値を取得する
            for row in w.objects:
                target = row[0]
                data = self._get_property(target, items)
                for v in data.values():
                    value.append(v)
            # Columnの値が取得できたら終わる
            break
        return value
