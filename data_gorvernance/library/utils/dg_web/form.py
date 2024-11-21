""" 入力フォーム用のモジュールです。

入力フォーム生成や操作のためのクラスが記載されています。

"""
import json
import traceback
from typing import Any, Optional, Union

import panel as pn

from library.utils.widgets import MessageBox, Button


# (vertical, horizontal)
# (top, right, bottom, and left)
margin = (0, 15, 5, 10)

p_style = """
p {
    margin-block-start: 0.5em;
    margin-block-end: 0.5em;
}
"""

class TextInput(pn.widgets.TextInput):
    """ テキスト入力ウィジェットのクラスです。

    Attributes:
        instance:
            schema_key(dict): JSONスキーマのproperty key

    """

    def __init__(self, **params: Any) -> None:
        """ クラスのインスタンス初期化処理を実行するメソッドです。

        Args:
            **params(dict[str, Any): pn.widgets.TextInputのその他のパラメータを設定します。

        """
        if 'schema_key' in params:
            self.schema_key = params.pop('schema_key')
        if "margin" not in params:
            params["margin"] = margin
        super().__init__(**params)


class Select(pn.widgets.Select):
    """ 選択ウィジェットのクラスです。

    Attributes:
        instance:
            schema_key: JSONスキーマのproperty key

    """

    def __init__(self, **params: Any) -> None:
        """ クラスのインスタンス初期化処理を実行するメソッドです。

        Args:
            **params(dict[str, Any]): pn.widgets.Selectのその他のパラメータを設定します。

        """
        if 'schema_key' in params:
            self.schema_key = params.pop('schema_key')
        if "margin" not in params:
            params["margin"] = margin
        super().__init__(**params)


class IntInput(pn.widgets.IntInput):
    """ 整数入力ウィジェットのクラスです。

    Attributes:
        instance:
            schema_key: JSONスキーマのproperty key

    """

    def __init__(self, **params: Any) -> None:
        """ クラスのインスタンス初期化処理を実行するメソッドです。

        Args:
            **params(dict[str, Any]): pn.widgets.IntInputのその他のパラメータを設定します。

        """
        if 'schema_key' in params:
            self.schema_key = params.pop('schema_key')
        if "margin" not in params:
            params["margin"] = margin
        super().__init__(**params)


class Checkbox(pn.widgets.Checkbox):
    """ チェックボックスウィジェットのクラスです。

    Attributes:
        instance:
            schema_key: JSONスキーマのproperty key

    """

    def __init__(self, **params: Any) -> None:
        """ クラスのインスタンス初期化処理を実行するメソッドです。

        Args:
            **params(dict[ste, Any]): pn.widgets.Checkboxのその他のパラメータを設定します。

        """
        if 'schema_key' in params:
            self.schema_key = params.pop('schema_key')
        if "margin" not in params:
            params["margin"] = (10, 10, 0, 10)
        super().__init__(**params)


class Title(pn.pane.Markdown):
    """ マークダウン形式のタイトルのクラスです。

    Attributes:
        instance:
            schema_key: JSONスキーマのproperty key

    """

    def __init__(self, obj: Optional[str] = None, is_root_call: bool = False, **params: Any) -> None:
        """ クラスのインスタンス初期化処理を実行するメソッドです。

        Args:
            obj(str|None): Markdownを含む文字列を設定します。
            is_root_call(bool): この呼び出し元が再帰的な呼び出しのルートであるかどうかを示します。
            **params(dict): pn.pane.Markdownのその他のパラメータを設定します。

        """
        if 'schema_key' in params:
            self.schema_key = params.pop('schema_key')
        if "margin" not in params:
            params["margin"] = (10, 10, 0, 10)
        if is_root_call:
            params["styles"] = {'font-size': "18px"}
        params["stylesheets"] = [p_style]
        super().__init__(object=obj, **params)


class Description(pn.pane.Markdown):
    """ マークダウン形式の説明のクラスです。

    Attributes:
        instance:
            schema_key: JSONスキーマのproperty key

    """

    def __init__(self, obj: Optional[str] = None, **params: Any) -> None:
        """ クラスのインスタンス初期化処理を実行するメソッドです。

        Args:
            obj(str): Markdownを含む文字列を設定する。
            **params(dict[str, Any]): pn.pane.Markdownのその他のパラメータを設定する。

        """
        if 'schema_key' in params:
            self.schema_key = params.pop('schema_key')
        if "margin" not in params:
            params["margin"] = (0, 10, 0, 10)
        params["stylesheets"] = [p_style]
        super().__init__(object=obj, **params)


class Column(pn.Column):
    """ タイトルや入力欄をまとめるクラスです。

    Attributes:
        instance:
            schema_key: JSONスキーマのproperty key

    """

    def __init__(self, **params: Any) -> None:
        """ クラスのインスタンス初期化処理を実行するメソッドです。

        Args:
            **params(dict[str, Any]: pn.Columnのその他のパラメータを設定する。

        """
        if 'schema_key' in params:
            self.schema_key = params.pop('schema_key')
        if "margin" not in params:
            params["margin"] = (5, 10, 5, 10)
        super().__init__(**params)


class ArrayBox(pn.Column):
    """ 入力欄が増減する項目をまとめたクラスです。

    Attributes:
        instance:
            schema_key: スキーマのkey

    """

    def __init__(self, **params: Any) -> None:
        """ クラスのインスタンス初期化処理を実行するメソッドです。

        Args:
            **params(dict[str, Any]): pn.WidgetBoxのその他のパラメータを設定する。

        """
        if 'schema_key' in params:
            self.schema_key = params.pop('schema_key')
        if "margin" not in params:
            params["margin"] = (0, 15, 0, 10)
        super().__init__(**params)


class ObjectBox(pn.WidgetBox):
    """ 入力欄を大項目でまとめるクラスです。

    Attributes:
        instance:
            schema_key: スキーマのkey

    """

    def __init__(self, **params: Any) -> None:
        """ クラスのインスタンス初期化処理を実行するメソッドです。

        Args:
            **params(dict[str, Any]): pn.WidgetBoxのその他のパラメータを設定する。

        """
        if 'schema_key' in params:
            self.schema_key = params.pop('schema_key')
        if "margin" not in params:
            params["margin"] = 10
        super().__init__(**params)


class Form:
    """入力フォームの操作のクラスです。

    jsonschemaから入力欄を生成し、そこからデータを取得する。

    Attributes:
        instance:
            form_box (pn.WidgetBox): フォームを格納する。
            msg_output (MessageBox): ユーザーに提示するメッセージを格納する。
            schema (dict): フォームの元となるjsonschema

    """

    def __init__(self) -> None:

        pn.extension()
        self.form_box = pn.WidgetBox()
        self.msg_output = MessageBox()

        self.schema = {}

    def create_widgets(self, schema: dict, data: Optional[dict] = None) -> None:
        """jsonchemaの形式に沿った入力欄をpanelで作成するメソッドです。

        Args:
            schema (dict): フォームの元となるjsonschemaを設定します。
            data (dict|None): jsonschemaの形式に沿った初期値を設定します。

        """
        if "properties" not in schema:
            return
        self.schema = schema
        self.form_box.clear()
        for key, properties in schema["properties"].items():
            value = None
            if isinstance(data, dict):
                value = data.get(key, {})
            self.form_box.append(self._generate_widget(properties, key, value, is_root_call=True))

    def _generate_widget(
        self, definition: dict, key: str, value: Optional[dict] = None, is_root_call: bool = False
    ) -> Union[ArrayBox, ObjectBox, Column]:
        """jsonschemaの設定値からpanelのwidgetを作成するメソッドです。

        Args:
            definition (dict): jsonschemaのkeyに対する定義部分. property value.
            key (str): jsonschemaのproperty key
            value (dict|None): keyに対する初期値を設定します。初期値が存在しない場合はNoneを指定します。
            is_root_call (bool): この呼び出し元が再帰的な呼び出しのルートであるかどうかを示します。

        Returns:
            form (ArrayBox | ObjectBox | Column): 渡されたkeyに対する入力欄を返す。

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
            return self._generate_array_widget(
                definition=definition, title=title, key=key, values=value, is_root_call=is_root_call
            )
        elif definition.get("type") == "object":
            return self._generate_object_widget(
                definition=definition, title=title, key=key, values=value, is_root_call=is_root_call
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
                form.append(pn.Row(pn.Spacer(width=17), Description(description, schema_key=key)))
            return form
        elif "string" in definition.get("type", ""):
            if isinstance(value, str):
                widget = TextInput(
                    schema_key=key, value=value, value_input=value)
            else:
                widget = TextInput(schema_key=key)
        else:
            self.msg_output.add_warning(
                f'name: {title}\ntype: {definition.get("type")}')

        title = Title(title, schema_key=key)
        form.append(title)
        description = definition.get("description")
        if description is not None:
            form.append(Description(description, schema_key=key))
        form.append(widget)

        return form

    def _generate_object_widget(self, definition: dict, title: str, key: str, values: dict, is_root_call: bool = False) -> ObjectBox:
        """type: objectをwidgetbox化するメソッドです。

        Args:
            definition (dict): jsonschemaのkeyに対する定義部分を設定します。 property value.
            title (str): keyに対応する表示名を設定します。
            key (str): schemaのkeyを設定します。
            values (dict): keyに対する初期値を設定します。
            is_root_call (bool): この呼び出し元が再帰的な呼び出しのルートであるかどうかを示します。

        Returns:
            obj_box (ObjectBox): 渡されたkeyに対する入力欄を返す。

        """
        obj_box = ObjectBox(schema_key=key)
        obj_box.append(Title(title, schema_key=key, is_root_call=is_root_call))
        description = definition.get("description")
        if description is not None:
            obj_box.append(Description(description, schema_key=key))
        for i_key, properties in definition["properties"].items():
            if values is None:
                value = None
            elif isinstance(values, dict):
                value = values.get(i_key, {})
            else:
                value = {}
            obj_box.append(self._generate_widget(properties, i_key, value))
        return obj_box

    def _generate_array_widget(self, definition: dict, title: str, key: str, values: Any, is_root_call: bool = False) -> ArrayBox:
        """type: arrayをwidgetbox化するメソッドです。

        Args:
            definition (dict): jsonschemaのkeyに対する定義部分. property value.
            title (str): keyに対応する表示名を設定します。
            key (str): schemaのkeyを設定します。
            values (Any): keyに対する初期値を設定します。
            is_root_call (bool): この呼び出し元が再帰的な呼び出しのルートであるかどうかを示します。

        Returns:
            box (ArrayBox): 渡されたkeyに対する入力欄を返す。

        """
        box = ArrayBox(schema_key=key)
        box.append(Title(title, schema_key=key, is_root_call=is_root_call))
        description = definition.get("description")
        if description is not None:
            box.append(Description(description, schema_key=key))
        column = pn.Column()

        def create_items(value: Optional[dict] = None) -> pn.Row:
            """arrayのひとつの要素を作成するメソッドです。

            Args:
                value (dict|None): 項目の初期値を設定します。

            Returns:
                pn.Row: 生成されたウィジェットと削除ボタンを含むパネルの行を返す。

            """
            column_list = column.objects
            items = definition["items"]
            title_num = f'{title}{len(column_list) + 1}'
            items["title"] = title_num
            widget = self._generate_widget(items, key, value)
            if items.get("type") == "object":
                return pn.Row(widget, create_remove_button(widget))
            else:
                row =  pn.Row(widget, create_remove_button(widget, align='end'))
            itembox = pn.WidgetBox(margin=(0, 0, 10, 20))
            itembox.append(row)
            return itembox

        def create_remove_button(widget: Union[ArrayBox, ObjectBox, Column], align: str = 'start') -> Button:
            """ arrayの選択した要素を削除するボタンを生成するメソッドです。

            Args:
                widget (ArrayBox | ObjectBox | Column): 削除するウィジェットを設定します。
                align (str): ボタンの配置を設定します。

            Returns:
                Button: 生成した削除ボタンを返す。

            """
            remove_button = Button(
                name='削除', button_type='danger', button_style='outline', align=align)

            def remove_item(event: Any) -> None:
                """ ウィジェットを削除するメソッドです。

                Args:
                    event (Any): ボタンクリックイベントを設定します。

                """
                try:
                    objects = column.objects
                    column.clear()
                    if len(objects) <= 1:
                        return
                    # 指定されたwidgetを削除
                    index = 0
                    for i, obj in enumerate(objects):
                        now = obj[0][0]
                        if now == widget:
                            index = i
                            break
                    objects.pop(index)
                    # 表示を更新
                    # TODO: value_inputが引き継げていない
                    for i, row in enumerate(objects):
                        title_num = f'{title}{i + 1}'
                        w = row[0][0]
                        if isinstance(w, pn.Column) or isinstance(w, pn.WidgetBox):
                            wb_list = w.objects
                            wb_list[0].object = title_num
                            w.clear()
                            w.extend(wb_list)
                        column.append(row)
                except Exception as e:
                    message = f'## [INTERNAL ERROR] : {traceback.format_exc()}'
                    self.msg_output.update_error(message)
            remove_button.on_click(remove_item)
            return remove_button

        def add_item(event: Any) -> None:
            """ Columnに要素を追加するメソッドです。

            Args:
                event (Any): ボタンクリックイベントを設定します。

            """
            column.append(create_items())

        if (not isinstance(values, list)) or (len(values) < 1):
            # 初期値がない場合
            column.append(create_items())
        else:
            for value in values:
                column.append(create_items(value))

        box.append(column)
        button_css ="""
        .bk-btn.bk-btn-primary {
            color: #357ebd !important;
        }
        """
        add_button = Button(name='追加', button_type='primary',
                            button_style='outline', stylesheets=[button_css])
        add_button.on_click(add_item)
        box.append(add_button)

        return box

    def is_not_input_widget(self, widget: Any) -> bool:
        """ 値を取得するwidgetでないかどうかを判定するメソッドです。

        Args:
            widget (Any): 判定対象のウィジェットを設定します。

        Returns:
            bool: 値を取得するwidgetでないかどうかを返す。

        """
        result = False
        if isinstance(widget, pn.pane.Markdown):
            result = True
        elif isinstance(widget, Button):
            result = True
        return result

    def get_data(self) -> dict:
        """ 入力欄からデータを取得するメソッドです。

        Returns:
            dict: 入力欄から取得したデータを返す。

        """
        if not self.schema or "properties" not in self.schema:
            return {}
        widgets = self.form_box.objects
        schema = self.schema["properties"]
        data = {}
        for widget in widgets:
            if self.is_not_input_widget(widget):
                continue
            data.update(self._get_property(widget, schema))
        return data

    def _get_property(self, widget: Any, schema: dict) -> dict:
        """ 各widgetからデータを取得するメソッドです。

        Args:
            widget (Any): データを取得したいwidgetを設定します。
            schema (dict): widgetに対応するプロパティ定義を設定します。

        Returns:
            dict: 取得したデータを含む辞書を返す。

        Raises:
            Exception: ウィジェットがサポートされていないタイプの場合

        """
        key = widget.schema_key
        value = ""
        definition: dict = schema[key]

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
            raise Exception(message) from e

        default = definition.get("default")
        if value or (default is not None):
            return {key: value}
        else:
            return {}

    def _get_value(self, widget: pn.Column) -> Any:
        """Column内のwidgetの値を取得するメソッドです。

        Args:
            widget (pn.Column): データを取得したいColumnを設定します。

        Returns:
            Any: widgetの値を返す。

        """
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
        """ObjectBox内のwidgetの値を取得するメソッドです。

        Args:
            widget (ObjectBox): データを取得したいObjectBoxを設定します。
            schema (dict): widgetに対応するプロパティ定義を設定します。

        Returns:
            dict: objectのvalue群を返す。

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

    def _get_array_value(self, widget: ArrayBox, schema: dict) -> list:
        """ArrayBox内のwidgetの値を取得するメソッドです。

        Args:
            widget (ArrayBox): データを取得したいArrayBoxを設定します。
            schema (dict): widgetに対応するプロパティ定義を設定します。

        Returns:
            list: arrayのvalue群を返す。

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
                if isinstance(row, pn.Row):
                    target = row[0]
                else:
                    target = row[0][0]
                data = self._get_property(target, items)
                for v in data.values():
                    value.append(v)
            # Columnの値が取得できたら終わる
            break
        return value

    def sort_order(self, schema: dict, json_path: str) -> dict:
        """jsonファイルを読み込みスキーマを並び替える処理を呼ぶメソッドです。

        Args:
            schema (dict): 元のスキーマ
            json_path (str): jsonファイルのパス

        Returns:
            dict: 並び替えたスキーマを返す。
        """
        update_schema = {}
        with open(json_path, 'r') as f:
            order = json.load(f)
        order_schema = self.sort_schema(schema['properties'], order)
        update_schema.update({'properties': order_schema})
        return update_schema

    def sort_schema(self, properties: dict, order: dict) -> dict:
        """jsonファイルのkeyに合わせてスキーマを並び替えるメソッドです。

        Args:
            properties (dict): スキーマのproperties要素を設定する。
            order (dict): jsonファイルの要素を設定する。

        Returns:
            dict: 並び替えたスキーマを返す。

        """
        new_schema = {}
        for order_key in order['ui:order']:
            if properties.get(order_key):
                if order.get(order_key) and properties[order_key].get("type") == "object":
                    schema_value = self.sort_schema(
                        properties[order_key]['properties'], order[order_key])
                    new_schema.update({order_key: properties[order_key]})
                    new_schema[order_key]['properties'] = schema_value
                elif order.get(order_key) and properties[order_key].get("type") == "array":
                    if properties[order_key]['items'].get("type") == "object":
                        schema_value = self.sort_schema(
                            properties[order_key]['items']['properties'], order[order_key]['items'])
                        new_schema.update({order_key: properties[order_key]})
                        new_schema[order_key]['items']['properties'] = schema_value
                    else:
                        new_schema[order_key] = schema_value
                else:
                    new_schema[order_key] = properties[order_key]
        return new_schema
