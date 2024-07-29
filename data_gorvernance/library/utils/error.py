""" エラーのモジュールです。
各種エラーのクラスが記載されています。
"""
class NotFoundSubflowDataError(Exception):
    """サブフローのデータが取得できなかった"""
    pass


class InputWarning(Exception):
    """入力値に問題があった"""
    pass


class ExecCmdError(Exception):
    """コマンド実行エラー"""
    pass

# vault
class UnusableVault(Exception):
    """vaultが利用できない"""
    pass


# For GRDM
class ProjectNotExist(Exception):
    """指定したプロジェクトが存在しない"""
    pass


class PermissionError(Exception):
    """リポジトリのアクセス権限が足りない"""


# 通信系のエラー
class UnauthorizedError(Exception):
    """認証が通らなかった(HTTPStatus.UNAUTHORIZED)"""
    pass


class NotFoundContentsError(Exception):
    """取得したいコンテンツが存在しなかった"""
    pass


# GINに対してのみのエラー
class RepositoryNotExist(Exception):
    """リモートリポジトリの情報が取得できない時のエラー"""
    pass


class UrlUpdateError(Exception):
    """HTTPとSSHのリモートURLが最新化できなかった時のエラー"""
    pass


class NoValueInDgFileError(Exception):
    """タスクNotebookのコードセルで例外で処理停止しなければならないエラーが発生した場合"""
    pass