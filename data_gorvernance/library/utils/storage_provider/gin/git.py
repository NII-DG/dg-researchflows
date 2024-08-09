"""gitの設定や操作を行う関数を記載しているモジュールです。"""
from library.utils.cmd import Cmd


def get_remote_url()->str:
    """gitリポジトリのリモートurlを取得するためのメソッドです。

    Returns:
        str:gitリポジトリのリモートurl

    """
    stdout, stderr, rt = Cmd.decode_exec_subprocess('git config --get remote.origin.url')
    return stdout.replace('\n', '')


def git_annex_untrust(cwd:str)->str:
    """ルートディレクトリを信頼できない設定にするメソッドです。

    Args:
        cwd (str):ルートディレクトリの絶対パス

    Returns:
        str:コマンドの実行結果

    """
    stdout, stderr, rt = Cmd.exec_subprocess(cmd='git annex untrust here', cwd=cwd)
    result = stdout.decode('utf-8')
    return result


def git_annex_trust(cwd:str):
    """ルートディレクトリを信頼する設定にするメソッドです。

    Args:
        cwd (str):ルートディレクトリの絶対パス

    """
    stdout, stderr, rt = Cmd.exec_subprocess(cmd='git annex --force trust web', cwd=cwd)
    result = stdout.decode('utf-8')


def git_annex_lock(path:str)->str:
    """ファイルを編集不可能にするメソッドです。

    Args:
        path (str):git annex lockコマンドを実行する対処のファイルパス

    Returns:
        str:コマンドの実行結果

    """
    stdout, stderr, rt = Cmd.exec_subprocess(f'git annex lock {path}', raise_error=False)
    result = stdout.decode('utf-8')
    return result


def git_annex_unlock(path:str)->str:
    """ファイルを編集可能にするメソッドです。

    Args:
        path (str):git annex unlockコマンドを実行する対処のファイルパス

    Returns:
        str:コマンドの実行結果

    """
    stdout, stderr, rt = Cmd.exec_subprocess(f'git annex unlock {path}',raise_error=False)
    result = stdout.decode('utf-8')
    return result


def git_annex_metadata_add_minetype_sha256_contentsize(file_path:str, mime_type:str, sha256:str, content_size:int, exec_path:str):
    """指定したファイルにGit Annexのメタデータ(mime_type, sha256, content_size) を追加するメソッドです。

    Args:
        file_path (str):メタデータを追加する対象のファイル
        mime_type (str):MIMEタイプ
        sha256 (str):SHA256ハッシュ値
        content_size (int):コンテンツサイズ
        exec_path (str):対象のディレクトリ

    """
    Cmd.exec_subprocess(f'git annex metadata "{file_path}" -s mime_type={mime_type} -s sha256={sha256} -s content_size={content_size}', cwd=exec_path)


def git_annex_metadata_add_sd_date_published(file_path:str, sd_date_published:str, exec_path:str):
    """指定したファイルにGit Annexのメタデータ(sd_date_published)を追加するメソッドです。

    Args:
        file_path (str):メタデータを追加する対象のファイル
        sd_date_published (str):データが生成/公開された日付を示すメタデータ
        exec_path (str):対象のディレクトリ

    """
    Cmd.exec_subprocess(f'git annex metadata "{file_path}" -s sd_date_published={sd_date_published}', cwd=exec_path)


def git_commmit(msg:str, cwd:str)->str:
    """コミットを作成するためのメソッドです。

    Args:
        msg (str):コミットメッセージ
        cwd (str):ルートディレクトリの絶対パス

    Returns:
        str:コマンドの実行結果

    """
    stdout, stderr, rt = Cmd.exec_subprocess('git commit -m "{}"'.format(msg), cwd=cwd,raise_error=False)
    result = stdout.decode('utf-8')
    return result


def git_pull(cwd:str)->str:
    """指定したディレクトリでプルを行うメソッドです。

    Args:
        cwd (str):ルートディレクトリの絶対パス

    Returns:
        str:コマンドの実行結果

    """
    stdout, stderr, rt = Cmd.exec_subprocess('git pull', cwd=cwd, raise_error=False)
    result = stdout.decode('utf-8')
    return result


def git_branch(cwd:str, option:str='')->str:
    """指定したディレクトリでブランチを操作するメソッドです。

    Args:
        cwd (str):ルートディレクトリの絶対パス
        option (str):git branchコマンドに追加で渡すオプション

    Returns:
        str:コマンドの実行結果

    """
    if len(option) > 0:
        stdout, stderr, rt = Cmd.exec_subprocess(f'git branch {option}', cwd=cwd,raise_error=False)
    else:
        stdout, stderr, rt = Cmd.exec_subprocess(f'git branch', cwd=cwd,raise_error=False)
    result = stdout.decode('utf-8')
    return result


def git_branch_for_remote(cwd:str)->str:
    """指定したディレクトリ内のGitリポジトリでリモートブランチの一覧を取得するためのメソッドです。

    Args:
        cwd (Any):ルートディレクトリの絶対パス

    Returns:
        str:コマンドの実行結果

    """
    return git_branch(cwd, '-r')


def is_annex_branch_in_repote(cwd:str)->bool:
    """origin/git-annexのリモートブランチが存在するか確認するメソッドです。

    Args:
        cwd (Any):ルートディレクトリの絶対パス

    Returns:
        bool:origin/git-annexが存在するかのフラグ

    """
    result = git_branch_for_remote(cwd)
    if 'origin/git-annex' in result:
        return True
    else:
        return False


def exec_git_status(cwd:str)->str:
    """現在のgitリポジトリの状態を表示するメソッドです。

    Args:
        cwd (Any):ルートディレクトリの絶対パス

    Returns:
        str:コマンドの実行結果

    """
    stdout, stderr, rt = Cmd.exec_subprocess('git status', cwd)
    result = stdout.decode('utf-8')
    return result


def is_conflict(cwd:str) -> bool:
    """現在のgitリポジトリに衝突しているものがあるかを確かめるメソッドです。

    Args:
        cwd (Any):ルートディレクトリの絶対パス

    Returns:
        bool:衝突しているものがあるかのフラグ

    """
    result = exec_git_status(cwd)
    lines = result.split('\n')
    for l in lines:
        if 'both modified:' in l or 'both added:' in l:
            return True
    return False
