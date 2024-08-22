""" エラーのモジュールです。"""


class NotFoundSubflowDataError(Exception):
    """サブフローのデータが取得できなかったエラーのクラスです。"""


class InputWarning(Exception):
    """入力値に問題があったエラーのクラスです。"""


class ExecCmdError(Exception):
    """コマンド実行エラーのクラスです。"""


# vault
class UnusableVault(Exception):
    """vaultが利用できないエラーのクラスです。"""


# For GRDM
class ProjectNotExist(Exception):
    """指定したプロジェクトが存在しないエラーのクラスです。"""


class RepoPermissionError(Exception):
    """リポジトリのアクセス権限が足りないエラーのクラスです。"""


# 通信系のエラー
class UnauthorizedError(Exception):
    """認証が通らなかった(HTTPStatus.UNAUTHORIZED)エラーのクラスです。"""


class NotFoundContentsError(Exception):
    """取得したいコンテンツが存在しなかったエラーのクラスです。"""


# GINに対してのみのエラー
class RepositoryNotExist(Exception):
    """リモートリポジトリの情報が取得できない時のエラーのクラスです。"""


class UrlUpdateError(Exception):
    """HTTPとSSHのリモートURLが最新化できなかった時のエラーのクラスです。"""


class NoValueInDgFileError(Exception):
    """タスクNotebookのコードセルで例外で処理停止しなければならないエラーが発生した場合のクラスです。"""
