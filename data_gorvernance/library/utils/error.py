
class ExistSubflowDirError(Exception):
    pass

class PrepareNewSubflowDataError(Exception):
    pass

class NotFoundSubflowDataError(Exception):
    pass

class InputWarning(Exception):
    """入力値に問題があった場合の例外"""
    pass

class MetadataNotExist(Exception):
    """取得したプロジェクトメタデータが空である場合のエラー"""
    pass


"""通信系のエラー"""


class RepositoryNotExist(Exception):
    """リモートリポジトリの情報が取得できない時のエラー"""
    pass


class UrlUpdateError(Exception):
    """HTTPとSSHのリモートURLが最新化できなかった時のエラー"""
    pass


class UnauthorizedError(Exception):
    """認証が通らなかった時のエラー(HTTPStatus.UNAUTHORIZED)"""
    pass

class NotFoundURLError(Exception):
    """存在しないURLのエラー(HTTPStatus.NOT_FOUND)"""
    pass

class ExecCmdError(Exception):
    '''コマンド実行エラー'''
    pass

class NoValueInDgFileError(Exception):
    '''タスクNotebookのコードセルで例外で処理停止しなければならないエラーが発生した場合'''
    pass