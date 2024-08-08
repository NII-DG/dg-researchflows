""" Notebookで使用するwidgetのモジュールです。

Panel.Widgetsを拡張したクラスが記載されています。

"""
import panel as pn

from .config import message as msg_config


class Button(pn.widgets.Button):
    """ pn.widgets.Buttonクラスを拡張したクラスです。

    Attributes:
        instance:
            name(str): ウィジェットのタイトル。
            button_type(str): ボタンのテーマ。
            button_style(str): ボタンのスタイル。'solid'または'outline'のいずれか。

    """

    def set_looks_init(self, name: str="") -> None:
        """ ボタンの見た目を設定するメソッドです。

        Args:
            name (str): ボタンのタイトルを設定します。

        """
        if name:
            self.name = name
        else:
            self.name = msg_config.get('form', 'submit_select')
        self.button_type = 'primary'
        self.button_style = 'solid'

    def set_looks_processing(self, name: str="") -> None:
        """ ボタンの見た目を設定するメソッドです。

        Args:
            name (str): ボタンのタイトルを設定します。

        """
        if name:
            self.name = name
        else:
            self.name = msg_config.get('form', 'processing')
        self.button_type = 'primary'
        self.button_style = 'outline'

    def set_looks_success(self, name: str) -> None:
        """ ボタンの見た目を設定するメソッドです。

        Args:
            name (str): ボタンのタイトルを設定します。

        """
        self.name = name
        self.button_type = 'success'
        self.button_style = 'solid'

    def set_looks_warning(self, name: str) -> None:
        """ ボタンの見た目を設定するメソッドです。

        Args:
            name (str): ボタンのタイトルを設定します。

        """
        self.name = name
        self.button_type = 'warning'
        self.button_style = 'solid'

    def set_looks_error(self, name: str) -> None:
        """ ボタンの見た目を設定するメソッドです。

        Args:
            name (str): ボタンのタイトルを設定します。

        """
        self.name = name
        self.button_type = 'danger'
        self.button_style = 'solid'


class Alert(pn.pane.Alert):
    """ pn.pane.Alertを拡張して特定のアラートを簡単に作成できるようにしたクラスです。"""

    @classmethod
    def info(cls, msg: str="") -> 'Alert':
        """ infoタイプのアラートを作成するメソッドです。

        Args:
            msg (str): アラートに表示するメッセージを設定します。

        Returns:
            Alert: infoタイプのAlertのインスタンスを返す。

        """
        return cls(msg, sizing_mode="stretch_width", alert_type='info')

    @classmethod
    def success(cls, msg: str="") -> 'Alert':
        """ successタイプのアラートを作成するメソッドです。

        Args:
            msg (str): アラートに表示するメッセージを設定します。

        Returns:
            Alert: successタイプのAlertのインスタンスを返す。

        """
        return cls(msg, sizing_mode="stretch_width", alert_type='success')

    @classmethod
    def warning(cls, msg: str="") -> 'Alert':
        """ warningタイプのアラートを作成するメソッドです。

        Args:
            msg (str): アラートに表示するメッセージを設定します。

        Returns:
            Alert: warningタイプのAlertのインスタンスを返す。

        """
        return cls(msg, sizing_mode="stretch_width", alert_type='warning')

    @classmethod
    def error(cls, msg: str="") -> 'Alert':
        """ dangerタイプのアラートを作成するメソッドです。

        Args:
            msg (str): アラートに表示するメッセージを設定します。

        Returns:
            Alert: dangerタイプのAlertのインスタンスを返す。

        """
        return cls(msg, sizing_mode="stretch_width", alert_type='danger')


class MessageBox(pn.WidgetBox):
    """ メッセージを表示するためのwidgetBoxのクラスです。"""

    def has_message(self)->bool:
        """ MessageBoxにメッセージが存在するかを判定するメソッドです。

        Returns:
            bool: MessageBoxにメッセージが存在するかを返す。

        """
        if self.objects:
            return True
        else:
            return False

    def update_info(self, msg: str="")->Alert:
        """ infoアラートに更新するメソッドです。

        Args:
            msg (str): アラートに表示するメッセージを設定します。

        Returns:
            Alert: infoタイプのAlertのインスタンスを返す。

        """
        self.clear()
        alert = Alert.info(msg)
        self.append(alert)
        return alert

    def update_success(self, msg: str="")->Alert:
        """ successアラートに更新するメソッドです。

        Args:
            msg (str): アラートに表示するメッセージを設定します。

        Returns:
            Alert: successタイプのAlertのインスタンスを返す。

        """
        self.clear()
        alert = Alert.success(msg)
        self.append(alert)
        return alert

    def update_warning(self, msg: str="")->Alert:
        """ warningアラートに更新するメソッドです。

        Args:
            msg (str): アラートに表示するメッセージを設定します。

        Returns:
            Alert: warningタイプのAlertのインスタンスを返す。

        """
        self.clear()
        alert = Alert.warning(msg)
        self.append(alert)
        return alert

    def update_error(self, msg: str="")->Alert:
        """ errorアラートに更新するメソッドです。

        Args:
            msg (str): アラートに表示するメッセージを設定します。

        Returns:
            Alert: dangerタイプのAlertのインスタンスを返す。

        """
        self.clear()
        alert = Alert.error(msg)
        self.append(alert)
        return alert

    def add_info(self, msg: str="")->Alert:
        """ infoアラートを追加するメソッドです。

        Args:
            msg (str): アラートに表示するメッセージを設定します。

        Returns:
            Alert: infoタイプのAlertのインスタンスを返す。

        """
        alert = Alert.info(msg)
        self.append(alert)
        return alert

    def add_success(self, msg: str="")->Alert:
        """ successアラートを追加するメソッドです。

        Args:
            msg (str): アラートに表示するメッセージを設定します。

        Returns:
            Alert: successタイプのAlertのインスタンスを返す。

        """
        alert = Alert.success(msg)
        self.append(alert)
        return alert

    def add_warning(self, msg: str="")->Alert:
        """ warningアラートを追加するメソッドです。

        Args:
            msg (str): アラートに表示するメッセージを設定します。

        Returns:
            Alert: warningタイプのAlertのインスタンスを返す。

        """
        alert = Alert.warning(msg)
        self.append(alert)
        return alert

    def add_error(self, msg: str="")->Alert:
        """ errorアラートを追加するメソッドです。

        Args:
            msg (str): アラートに表示するメッセージを設定します。

        Returns:
            Alert: dangerタイプのAlertのインスタンスを返す。

        """
        alert = Alert.error(msg)
        self.append(alert)
        return alert
