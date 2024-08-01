""" エラーのモジュールです。"""
class NotFoundSubflowDataError(Exception):
    """サブフローのデータが取得できなかったエラーのクラスです。"""
    pass


class InputWarning(Exception):
    """入力値に問題があったエラーのクラスです。"""
    pass


class ExecCmdError(Exception):
    """コマンド実行エラーのクラスです。"""
    pass

# vault
class UnusableVault(Exception):
    """vaultが利用できないエラーのクラスです。"""
    pass


# For GRDM
class ProjectNotExist(Exception):
    """指定したプロジェクトが存在しないエラーのクラスです。"""
    pass


class PermissionError(Exception):
    """リポジトリのアクセス権限が足りないエラーのクラスです。"""


# 通信系のエラー
class UnauthorizedError(Exception):
    """認証が通らなかった(HTTPStatus.UNAUTHORIZED)エラーのクラスです。"""
    pass


class NotFoundContentsError(Exception):
    """取得したいコンテンツが存在しなかったエラーのクラスです。"""
    pass


# GINに対してのみのエラー
class RepositoryNotExist(Exception):
    """リモートリポジトリの情報が取得できない時のエラーのクラスです。"""
    pass


class UrlUpdateError(Exception):
    """HTTPとSSHのリモートURLが最新化できなかった時のエラーのクラスです。"""
    pass


class NoValueInDgFileError(Exception):
    """タスクNotebookのコードセルで例外で処理停止しなければならないエラーが発生した場合のクラスです。"""
    pass