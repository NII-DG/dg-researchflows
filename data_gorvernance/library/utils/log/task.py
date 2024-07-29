"""タスクログ関するモジュールです。
タスク処理の前後でログを出力する機能に関するクラスが記載されています。
"""
import functools

from .models import UserActivityLog


class TaskLog:
    """タスクログのクラスです。

    タスク処理の前後でログを出力する機能に関するメソッドを記載しています。

     Attributes:
            instance:
                log(UserActivityLog):UserActivityLogクラスのインスタンス

    """
    def __init__(self, nb_working_file_path, notebook_name) -> None:
        """クラスのインスタンスの初期化を行うメソッドです。コンストラクタ

        引数として受け取ったパスとノートブックからUserActivityLogクラスのインスタンスを生成し、保存します。

        Args:
            nb_working_file (Any): ノートブック名を含む絶対パス
            notebook_name(Any):ノートブック名
        
        Example:
            >>> TaskLog.__init__(self, nb_working_file_path, notebook_name)

        Note:
            特にありません。

        """
        self.log = UserActivityLog(nb_working_file_path, notebook_name)

    ###################################
    # 継承したクラスで呼ぶ為のデコレータ #
    ###################################
    @staticmethod
    def task_cell(cell_id: str, start_message="", finish_message=""):
        """タスクセルに必須の処理を行うメソッドです。

        静的なメソッドとして機能し、引数としてセル番号とメッセージを受け取ります。

        Args:
            cell_id(str):ノートブックのセル番号
            start_message(str):タスクの開始時に出力するメッセージ。デフォルトは空文字。
            finish_message(str):タスクの終了時に出力するメッセージ。デフォルトは空文字。

        Return:
           戻り値の型の書き方がわかりませんでした。

         Example:
            >>> TaskLog.task_cell(cell_id)

        Note:
            特にありません。
        
        """
        def wrapper(func):
            """デコレータ内部で使用するラッパー関数です。

            引数としてデコレートする関数を受け取り、decorate関数を返します。

            Args:   
                func:デコレーターで修飾する関数
            
            Return:
                 戻り値の型の書き方がわかりませんでした。
            
            Note:
            特にありません。
            
            """
            @functools.wraps(func)
            def decorate(self, *args, **kwargs):
                """デコレートされた関数です。
                
                このメソッドではfuncメソッドを実行する前後にログが出力されます。

                Args:
                    *args(tuple):メソッドの位置引数
                    **kwargs(dict[str, Any]):メソッドのキーワード引数
                
                Returns:
                    Any:タスクの実行結果
                
                Note:
                     特にありません。
                 
                """
                self.log.cell_id = cell_id
                self.log.start(note=start_message)
                result = func(self, *args, **kwargs)
                self.log.finish(note=finish_message)
                return result
            return decorate
        return wrapper

    @staticmethod
    def callback_form(event_name):
        """フォームの処理に必須の処理を行うメソッドです。

         静的なメソッドとして機能し、引数としてイベント名を受け取ります。

        Args:
            event_name (Any): 処理が行われるイベントの名前
        
        Return:
             戻り値の型の書き方がわかりませんでした。

        Note:
            特にありません。

        """
        def wrapper(func):
            """デコレータ内部で使用するラッパー関数です。

            引数としてデコレートする関数を受け取り、decorate関数を返します。

            Args:   
                func:デコレーターで修飾する関数
            
            Return:
                 戻り値の型の書き方がわかりませんでした。
            
            Note:
            特にありません。

            """
            @functools.wraps(func)
            def decorate(self, *args, **kwargs):
                """デコレートされた関数です。
                
                このメソッドではfuncメソッドを実行する前後にログが出力されます。

                Args:
                    *args(tuple):メソッドの位置引数
                    **kwargs(dict[str, Any]):メソッドのキーワード引数
                
                Returns:
                    Any:タスクの実行結果
                
                Note:
                     特にありません。
                 
                """
                self.log.start(detail=event_name)
                result = func(self, *args, **kwargs)
                self.log.finish(detail=event_name)
                return result
            return decorate
        return wrapper