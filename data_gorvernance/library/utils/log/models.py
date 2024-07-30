"""ログの生成に関するクラスや関数が記載されています。
"""
import logging
from logging import FileHandler
import os
from pathlib import Path
import datetime

from ..config import path_config
from ..setting import get_subflow_type_and_id


class BaseLogger:
    """ロギング機能の基本となるメソッドを記載したクラスです。

    ハンドラーやフォーマッターの設定などロガーに関する基本的な処理を行うメソッドを記載しています。

    Attributes:
        instance:
            logger(logging.Logger):ロガー
            date(str):ログが生成された時刻
            log_dir(str):ログファイルの出力ディレクトリ
            handler(FileHandler):ログを特定のファイルに出力するためのハンドラー

    """
    def __init__(self, output_dir="."):
        """クラスのインスタンスの初期化を行うメソッドです。コンストラクタ

        ロガーの生成や時刻の記録などロギング機能における基本の処理を行います。

        Args:
            output_dir(str, optional):ログファイルの出力ディレクトリ。デフォルトはカレントディレクトリ。

        """
        self.logger = logging.getLogger(__name__)
        self.date = datetime.datetime.now().strftime('%Y%m%d')
        self.log_dir = output_dir
        self._update_handler()
        self.logger.propagate = False

    def reset_file(self, fmt):
        """ファイルのリセットを行うメソッドです。

       フォーマッターの設定を行う他、 日付が変わっていた場合のみ日付とログハンドラーの更新を行います。

        Args:
            fmt(Any):フォーマッターを設定

        """
        now_date = datetime.datetime.now().strftime('%Y%m%d')
        if self.date != now_date:
            self.date = now_date
            self._update_handler()
        self.set_formatter(fmt)

    def _update_handler(self):
        """ロガーのハンドラーを更新するメソッドです。

        ロガーに既にハンドラーが存在している場合、全てのハンドラーを取り除きます。
        その後、新たにハンドラーを生成し、ロガーに加えます。

        """
        if self.logger.hasHandlers():
            handlers = self.logger.handlers
            for handler in handlers:
                self.logger.removeHandler(handler)
        log_file = self.date + ".log"
        log_file = os.path.join(self.log_dir, log_file)
        self.handler = FileHandler(log_file)
        self.logger.addHandler(self.handler)

    def set_formatter(self, fmt:str):
        """フォーマッターを設定するためのメソッドです。

        引数として受け取ったフォーマットからフォーマッターを生成し、それをハンドラーに設定します。

        Args:
            fmt(str):フォーマッターを生成

        """
        formatter = logging.Formatter(fmt)
        self.handler.setFormatter(formatter)

    def set_log_level(self, level):
        """ロガーのログレベルを設定するためのメソッドです。

        引数として渡されたものと対応したログレベルをロガーに設定します。

        Args:
            level(Any):ログレベルを設定

        """
        if level == 'debug':
            self.logger.setLevel(logging.DEBUG)
        elif level == 'info':
            self.logger.setLevel(logging.INFO)
        elif level == 'warning':
            self.logger.setLevel(logging.WARNING)
        elif level == 'error':
            self.logger.setLevel(logging.ERROR)
        elif level == 'critical':
            self.logger.setLevel(logging.CRITICAL)

class UserActivityLog(BaseLogger):
    """BaseLoggerクラスを継承し、実際にユーザーがロギング機能を用いることができるよう実装したクラスです。

    パスやメッセージを受け取り、それに対応したログを出力するためのメソッドを記載したクラスです。
    BaseLoggerクラスのメソッドを呼び出すことでロガーやフォーマッターの設定を行います。

    Attributes:
        instance:
            username(str):ユーザー名
            ipynb_file(Any):ノートブックファイルへのパス
            subflow_id(str):サブフローのID
            subflow_type(str):サブフローの種別
            cell_id(str):ノートブックのセルID

    """

    def __init__(self, nb_working_file, notebook_name):
        """ クラスのインスタンスを初期化するメソッドです。コンストラクタ

        引数としてパスとノートブック名を受け取り,対応したログを生成し、インスタンスに保存します。

        Args:
            nb_working_file (Any): ノートブック名を含む絶対パス
            notebook_name(Any):ノートブック名

        """
        # set log config
        log_dir = self._get_log_dir(nb_working_file)
        super().__init__(log_dir)
        self.set_log_level('info')
        # set items
        self.username = os.environ['JUPYTERHUB_USER']
        self.ipynb_file = os.path.join(
            os.path.dirname(nb_working_file), notebook_name
        )
        subflow_type, subflow_id = get_subflow_type_and_id(nb_working_file)
        self.subflow_id = subflow_id
        self.subflow_type = subflow_type
        self.cell_id = ""

    def _get_log_dir(self, nb_working_file):
        """ログファイルを保存するディレクトリを生成するためのメソッドです。

        引数として受け取ったパスに対応したログファイルを保存するためのディレクトリを生成し、そこへのパスを返します。

        Args:
            nb_working_file (Any): ノートブック名を含む絶対パス

        Returns:
            str:ログファイルを保存するディレクトリへのパス

        """
        root_folder = Path(
            path_config.get_abs_root_form_working_dg_file_path(nb_working_file)
        )
        log_dir = os.environ['JUPYTERHUB_SERVER_NAME']
        log_dir = (root_folder / path_config.DG_LOG_FOLDER / log_dir)
        os.makedirs(log_dir, exist_ok=True)
        return str(log_dir)

    def _get_format(self):
        """フォーマットを定義するためのメソッドです。

        フォーマッターを設定する際に基となるフォーマットを定義しています。

        Returns:
           str:フォーマットの定義

        """
        return '%(levelname)s\t%(asctime)s\t%(username)s\t%(subflow_id)s\t%(subflow_type)s\t%(ipynb_name)s\t%(cell_id)s\t%(message)s'

    def info(self, message):
        """ログレベルがINFOのログを出力するするためのメソッドです。

        ファイルのリセットを行った後、引数として受け取ったメッセージとコンストラクタの値を引数にINFOレベルのログを出力します。

        Args:
            message(Any):ログメッセージを設定

        """
        self.reset_file(self._get_format())
        self.logger.info(message, extra=self.record())

    def warning(self, message):
        """ログレベルがWARNINGのログを出力するするためのメソッドです。

        ファイルのリセットを行った後、引数として受け取ったメッセージとコンストラクタの値を引数にWARNINGレベルのログを出力します。

        Args:
            message(Any):ログメッセージを設定

        """
        self.reset_file(self._get_format())
        self.logger.warning(message, extra=self.record())

    def error(self, message):
        """ログレベルがERRORのログを出力するするためのメソッドです。

        ファイルのリセットを行った後、引数として受け取ったメッセージとコンストラクタの値を引数にERRORレベルのログを出力します。

        Args:
            message(Any):ログメッセージを設定

        """
        self.reset_file(self._get_format())
        self.logger.error(message, extra=self.record())

    def start(self, detail='', note=''):
        """処理の開始をログに記録するためのメソッドです。

        引数として処理内容の詳細と注記を受け取り、それを基にINFOレベルのログを出力します。

        Args:
            detail(str, optional):処理の詳細。デフォルトは空文字
            note(str, optional):処理の注記。デフォルトは空文字

        """
        self.info("-- " + detail + "処理開始 --" + note)

    def finish(self, detail='', note=''):
        """処理の終了をログに記録するためのメソッドです。

        引数として処理内容の詳細と注記を受け取り、それを基にINFOレベルのログを出力します。

        Args:
            detail(str, optional):処理の詳細。デフォルトは空文字
            note(str, optional):処理の注記。デフォルトは空文字

        """
        self.info("-- " + detail + "処理終了 --" + note)

    def record(self):
        """コンストラクタの情報を整理するためのメソッドです。

        コンストラクタに保存されている情報を辞書形式に変換して返します。

        Returns:
            dict[str, any]:ログデータを辞書形式で返す

        """
        return {
            'username': self.username,
            'subflow_id': self.subflow_id,
            'subflow_type':self.subflow_type,
            'ipynb_name': self.ipynb_file,
            'cell_id': self.cell_id
        }

