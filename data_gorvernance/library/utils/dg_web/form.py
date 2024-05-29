import traceback

import panel as pn
from IPython.display import display

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

        for key, properties in schema["properties"].items():
            value = data.get(key)
            self.form_box.append(self._create_input_widget(properties, key, value))

    def _create_input_widget(self, schema:dict, key, value):
        """jsonschemaの設定値からpanelのwidgetを作成する"""
        title = schema.get("title", key)

        if "enum" in schema and "string" in schema.get("type", ""):
            if isinstance(value, str):
                return Select(name=title, schema_key=key, value=value, options=schema["enum"], margin=margin)
            else:
                return Select(name=title, schema_key=key, options=schema["enum"], margin=margin)
        elif schema.get("type") == "array":
            if not isinstance(value, list):
                value = []
            return self._genetate_array_widget(
                    schema=schema, title=title, key=key, values=value
                )
        elif schema.get("type") == "object":
            if not isinstance(value, dict):
                value = {}
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

    def _generate_object_widget(self, schema, title, key, values: dict):
        """type: objectをwidgetbox化する"""
        obj_box = pn.WidgetBox()
        obj_box.append(Markdown(title, schema_key=key))
        for i_key, properties in schema["properties"].items():
            value = values.get(i_key)
            obj_box.append(self._create_input_widget(properties, i_key, value))
        return obj_box

    def _genetate_array_widget(self, schema, title, key, values: list):
        """type: arrayをwidgetbox化する"""
        box =  pn.WidgetBox(margin=margin)
        box.append(Markdown(title, schema_key=key))

        column = pn.Column(margin=margin)

        def create_items(data=None):
            """arrayのひとつの要素を作成する"""
            column_list = column.objects
            title_num = title + str(len(column_list) + 1)
            items = schema["items"]
            if items.get("type") == "object":
                obj_box = pn.WidgetBox()
                obj_box.append(Markdown(title_num, schema_key=key))
                for i_key, properties in items["properties"].items():
                    if isinstance(data, dict):
                        value = data.get(i_key)
                    else:
                        value = None
                    obj_box.append(self._create_input_widget(properties, i_key, value))
                return pn.Row(obj_box, create_remove_button(obj_box))
            else:
                widget = self._create_input_widget({
                    "type": items.get("type"),
                    "title": title_num
                }, key, data)
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

        if len(values) < 1:
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
        result = False
        if isinstance(widget, Markdown):
            result = True
        elif isinstance(widget, Button):
            result = True
        return result

    def get_data(self):
        """入力欄からデータを取得する"""
        widgets = self.form_box.objects
        data = {}
        for widget in widgets:
            if self.is_not_input_widget(widget):
                continue
            data.update(self.get_value(widget))
        return data

    def get_value(self, widget):
        """各widgetからデータを取得する"""
        key = ""
        value = ""
        try:
            if isinstance(widget, pn.WidgetBox):
                objects = widget.objects
                key = objects[0].schema_key
                value = self.get_widget_value(objects)

            elif isinstance(widget, TextInput):
                key = widget.schema_key
                value = widget.value_input
            elif isinstance(widget, pn.widgets.Widget):
                key = widget.schema_key
                value = widget.value
            else:
                raise Exception(f'widget: {widget}')

        except Exception:
            message = f'## [INTERNAL ERROR] : {traceback.format_exc()}\nkey: {key}\nvalue: {value}'
            self.msg_output.update_error(message)

        # 値が空の場合はデータを取得しない
        if not value:
            return {}

        return {key: value}

    def get_widget_value(self, objects):
        content = objects[1]
        value = None
        if isinstance(content, pn.Column):
            # type: array
            value = []
            for row in content:
                target = row[0]
                if isinstance(target, pn.WidgetBox):
                    data = {}
                    for w in target:
                        if self.is_not_input_widget(w):
                            continue
                        data.update(self.get_value(w))
                    if data:
                        value.append(data)
                else:
                    data = self.get_value(target)
                    for v in data.values():
                        value.append(v)
        else:
            # type: object
            value = {}
            for w in objects:
                if self.is_not_input_widget(w):
                    continue
                value.update(self.get_value(w))
        return value

