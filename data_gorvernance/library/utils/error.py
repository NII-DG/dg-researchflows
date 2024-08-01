class NotFoundSubflowDataError(Exception):
    """サブフローのデータが取得できなかった"""


class InputWarning(Exception):
    """入力値に問題があった"""


class ExecCmdError(Exception):
    '''コマンド実行エラー'''


# vault
class UnusableVault(Exception):
    """vaultが利用できない"""


# For GRDM
class ProjectNotExist(Exception):
    """指定したプロジェクトが存在しない"""


class PermissionError(Exception):
    """リポジトリのアクセス権限が足りない"""


# 通信系のエラー
class UnauthorizedError(Exception):
    """認証が通らなかった(HTTPStatus.UNAUTHORIZED)"""


class NotFoundContentsError(Exception):
    """取得したいコンテンツが存在しなかった"""


# GINに対してのみのエラー
class RepositoryNotExist(Exception):
    """リモートリポジトリの情報が取得できない時のエラー"""


class UrlUpdateError(Exception):
    """HTTPとSSHのリモートURLが最新化できなかった時のエラー"""


class NoValueInDgFileError(Exception):
    '''タスクNotebookのコードセルで例外で処理停止しなければならないエラーが発生した場合'''
