import traceback

import panel as pn

from library.utils.widgets import MessageBox, Button


margin = (10, 10, 5, 10)


class TextInput(pn.widgets.TextInput):

    def __init__(self, **params):
        if 'schema_key' in params:
            self.schema_key = params.pop('schema_key')
        super().__init__(**params)


class Select(pn.widgets.Select):

    def __init__(self, **params):
        if 'schema_key' in params:
            self.schema_key = params.pop('schema_key')
        super().__init__(**params)


class Checkbox(pn.widgets.Checkbox):

    def __init__(self, **params):
        if 'schema_key' in params:
            self.schema_key = params.pop('schema_key')
        super().__init__(**params)


class IntInput(pn.widgets.IntInput):

    def __init__(self, **params):
        if 'schema_key' in params:
            self.schema_key = params.pop('schema_key')
        super().__init__(**params)


class Markdown(pn.pane.Markdown):

    def __init__(self, object=None, **params):
        if 'schema_key' in params:
            self.schema_key = params.pop('schema_key')
        super().__init__(object=object, **params)


class ArrayBox(pn.WidgetBox):

    def __init__(self, **params):
        if 'schema_key' in params:
            self.schema_key = params.pop('schema_key')
        super().__init__(**params)

class ObjectBox(pn.WidgetBox):

    def __init__(self, **params):
        if 'schema_key' in params:
            self.schema_key = params.pop('schema_key')
        super().__init__(**params)

class Form:

    def __init__(self):

        pn.extension()
        self.form_box = pn.WidgetBox()
        self.msg_output = MessageBox()

    def create_widgets(self, schema:dict, data: dict):
        """jsonchemaの形式にそった入力欄をpanelで作成する

        Args:
            schema (dict): jsonschema
            data (dict): jsonschemaの形式に沿った初期値
        """
        self.schema = schema
        for key, properties in schema["properties"].items():
            value = data.get(key)
            self.form_box.append(self._create_input_widget(properties, key, value))

    def _create_input_widget(self, schema:dict, key:str, value=None):
        """jsonschemaの設定値からpanelのwidgetを作成する

        Args:
            schema (dict): jsonschemaにおけるkeyの値
            key (str): schemaのkey
            value (Any, optional): keyに対する初期値. Defaults to None.

        Returns:
            PanelのWidget
        """
        title = schema.get("title", key)
        if value is None:
            value = schema.get("default")

        if "enum" in schema and "string" in schema.get("type", ""):
            options = [""] + schema["enum"]
            if isinstance(value, str):
                return Select(name=title, schema_key=key, value=value, options=options, margin=margin)
            else:
                return Select(name=title, schema_key=key, options=options, margin=margin)
        elif schema.get("type") == "array":
            return self._genetate_array_widget(
                    schema=schema, title=title, key=key, values=value
                )
        elif schema.get("type") == "object":
            return self._generate_object_widget(
                    schema=schema, title=title, key=key, values=value
                )
        elif schema.get("type") == "number":
            if isinstance(value, int):
                return IntInput(name=title, schema_key=key, value=value, margin=margin)
            else:
                return IntInput(name=title, schema_key=key, margin=margin)
        elif schema.get("type") == "boolean":
            if isinstance(value, bool):
                return Checkbox(name=title, schema_key=key, value=value, margin=margin)
            else:
                return Checkbox(name=title, schema_key=key, margin=margin)
        elif "string" in schema.get("type", ""):
            if isinstance(value, str):
                return TextInput(name=title, schema_key=key, value=value, value_input=value, margin=margin)
            else:
                return TextInput(name=title, schema_key=key, margin=margin)
        else:
            self.msg_output.add_warning(f'name: {title}\ntype: {schema.get("type")}')

    def _generate_object_widget(self, schema:dict, title:str, key:str, values):
        """type: objectをwidgetbox化する

        Args:
            schema (dict): jsonschemaにおけるkeyの値
            title (str): keyに対応する表示名
            key (str): schemaのkey
            value (Any): keyに対する初期値

        Returns:
            ObjectBox
        """
        obj_box = ObjectBox(schema_key=key)
        obj_box.append(Markdown(title, schema_key=key))
        for i_key, properties in schema["properties"].items():
            if isinstance(values, dict):
                value = values.get(i_key)
            else:
                value = None
            obj_box.append(self._create_input_widget(properties, i_key, value))
        return obj_box

    def _genetate_array_widget(self, schema:dict, title:str, key:str, values):
        """type: arrayをwidgetbox化する

        Args:
            schema (dict): jsonschemaにおけるkeyの値
            title (str): keyに対応する表示名
            key (str): schemaのkey
            value (Any): keyに対する初期値

        Returns:
            ArrayBox
        """
        box = ArrayBox(margin=margin, schema_key=key)
        box.append(Markdown(title, schema_key=key))

        column = pn.Column(margin=margin)

        def create_items(value=None):
            """arrayのひとつの要素を作成する"""
            column_list = column.objects
            title_num = title + str(len(column_list) + 1)
            items = schema["items"]
            items["title"] = title_num
            widget = self._create_input_widget(items, key, value)
            if items.get("type") == "object":
                return pn.Row(widget, create_remove_button(widget))
            else:
                # TODO: ボタンの位置真ん中にしたい
                return pn.Row(widget, create_remove_button(widget))

        def create_remove_button(widget):
            """arrayの選択した要素を削除するボタンを生成する"""
            remove_button = Button(name='Remove', button_type='danger', button_style='outline')
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
                    for i, obj in enumerate(objects):
                        title_num = title + str(i + 1)
                        w = obj[0]
                        if isinstance(w, pn.WidgetBox):
                            wb_list = w.objects
                            wb_list[0].object = title_num
                            w.clear()
                            w.extend(wb_list)
                        else:
                            w.name = title_num
                        column.append(obj)
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
        if isinstance(widget, Markdown):
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
            data.update(self._get_value(widget, schema))
        return data

    def _get_value(self, widget, schema:dict):
        """各widgetからデータを取得する

        Args:
            widget (Any): データを取得したいwidget
            schema (dict): widgetに対応する部分のschema
        """
        try:
            key = widget.schema_key
            value = ""
            if isinstance(widget, ArrayBox):
                value = self._get_array_value(widget, schema)
            elif isinstance(widget, ObjectBox):
                value = self._get_object_value(widget, schema)
            elif isinstance(widget, TextInput):
                value = widget.value_input
            elif isinstance(widget, pn.widgets.Widget):
                value = widget.value
            else:
                raise Exception(f'widget: {widget}')

        except Exception as e:
            message = f'{str(e)}\nkey: {key}\nvalue: {value}'
            raise Exception(message)

        if not value:
            try:
                value = schema[key]["default"]
            except KeyError:
                # デフォルト値がなく、値が空の場合はデータを取得しない
                return {}

        return {key: value}

    def _get_array_value(self, widget: ArrayBox, schema: dict):
        """ArrayBox内のwidgetの値を取得する

        Args:
            widget (ArrayBox): jsonschemaのtype: arrayの部分のwidget
            schema (dict): widgetに対応する部分のschema

        Returns:
            list: arrayのvalue群
        """
        objects = widget.objects
        key = widget.schema_key
        value = []
        items = {key: schema[key]["items"]}
        for w in objects:
            if not isinstance(w, pn.Column):
                # タイトルやボタンは取得しない
                continue
            # Columnがあったら値を取得する
            for row in w.objects:
                target = row[0]
                data = self._get_value(target, items)
                for v in data.values():
                    value.append(v)
            # Columnの値が取得できたら終わる
            break
        return value

    def _get_object_value(self, widget: ObjectBox, schema):
        """ObjectBox内のwidgetの値を取得する

        Args:
            widget (ObjectBox): jsonschemaのtype: objectの部分のwidget
            schema (dict): widgetに対応する部分のschema

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
            value.update(self._get_value(w, properties))
        return value
