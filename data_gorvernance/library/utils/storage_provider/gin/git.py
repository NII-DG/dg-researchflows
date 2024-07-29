from ...cmd import Cmd

def get_remote_url():
    """gitリポジトリのリモートurlを取得するためのメソッドです。

    現在のgitリポジトリのリモートurlを取得し、それを文字列として返します。

    Returns:
        str:gitリポジトリのリモートurl

    """
    stdout, stderr, rt = Cmd.decode_exec_subprocess('git config --get remote.origin.url')
    return stdout.replace('\n', '')

def git_annex_untrust(cwd):
    """現在の作業ディレクトリを信頼できない設定にするメソッドです。

    引数で指定されたディレクトリ(cwd)内のgitリポジトリ内でgit annex untrust hereコマンドを実行します。

    Args:
        cwd (Any):現在の作業ディレクトリ

    Returns:
        str:コマンドの実行結果

    """
    stdout, stderr, rt = Cmd.exec_subprocess(cmd='git annex untrust here', cwd=cwd)
    result = stdout.decode('utf-8')
    return result

def git_annex_trust(cwd):
    """現在の作業ディレクトリをwebリモートを信頼する設定にするメソッドです。

    引数で指定されたディレクトリ(cwd)内のgitリポジトリ内でgit annex --force trust webコマンドを実行します。

    Args:
        cwd (Any):現在の作業ディレクトリ

    """
    stdout, stderr, rt = Cmd.exec_subprocess(cmd='git annex --force trust web', cwd=cwd)
    result = stdout.decode('utf-8')

def git_annex_lock(path:str):
    """ファイルを編集不可能にするメソッドです。

    引数で指定されたパスのファイルに対してgit annex lockコマンドを実行し、ロック状態にします。

    Args:
        path (str):git annex lockコマンドを実行する対処のファイルパス

    Returns:
        str:コマンドの実行結果

    """
    stdout, stderr, rt = Cmd.exec_subprocess(f'git annex lock {path}', raise_error=False)
    result = stdout.decode('utf-8')
    return result

def git_annex_unlock(path:str):
    """ファイルを編集可能にするメソッドです。

    引数で指定されたパスのファイルに対してgit annex unlockコマンドを実行し、ロック状態を解除します。

    Args:
        path (str):git annex unlockコマンドを実行する対処のファイルパス

    Returns:
        str:コマンドの実行結果

    """
    stdout, stderr, rt = Cmd.exec_subprocess(f'git annex unlock {path}',raise_error=False)
    result = stdout.decode('utf-8')
    return result

def git_annex_metadata_add_minetype_sha256_contentsize(file_path, mime_type, sha256, content_size, exec_path):
    """指定したファイルにGit Annexのメタデータを追加するメソッドです。

    引数で指定したファイルに対してCmd.exec_subprocess()を実行してメタデータを追加します。

    Args:
        file_path (Any):メタデータを追加する対象のファイル
        mime_type (Any):MIMEタイプ
        sha256 (Any):SHA256ハッシュ値
        content_size (Any):コンテンツサイズ
        exec_path (Any):対象のディレクトリ

    """
    Cmd.exec_subprocess(f'git annex metadata "{file_path}" -s mime_type={mime_type} -s sha256={sha256} -s content_size={content_size}', cwd=exec_path)

def git_annex_metadata_add_sd_date_published(file_path, sd_date_published, exec_path):
    """指定したファイルにGit Annexのメタデータを追加するメソッドです。

    引数で指定したファイルに対してCmd.exec_subprocess()を実行してメタデータを追加します。

    Args:
        file_path (Any):メタデータを追加する対象のファイル
        sd_date_published (Any):データが生成/公開された日付を示すメタデータ
        exec_path (Any):対象のディレクトリ

    """
    Cmd.exec_subprocess(f'git annex metadata "{file_path}" -s sd_date_published={sd_date_published}', cwd=exec_path)

def git_commmit(msg:str, cwd):
    """コミットを作成するためのメソッドです。

    引数で指定されたディレクトリ内のgitリポジトリでコミットを作成します。

    Args:
        msg (str):コミットメッセージ
        cwd (_type_):現在の作業ディレクトリ

    Returns:
        str:コマンドの実行結果

    """
    stdout, stderr, rt = Cmd.exec_subprocess('git commit -m "{}"'.format(msg), cwd=cwd,raise_error=False)
    result = stdout.decode('utf-8')
    return result

def git_pull(cwd):
    """指定したディレクトリでプルを行うメソッドです。

    引数で指定されたディレクトリ内でgit pullコマンドを実行します。

    Args:
        cwd (_type_):現在の作業ディレクトリ

    Returns:
        str:コマンドの実行結果

    """
    stdout, stderr, rt = Cmd.exec_subprocess('git pull', cwd=cwd, raise_error=False)
    result = stdout.decode('utf-8')
    return result


def git_branch(cwd, option=''):
    """指定したディレクトリでブランチを操作するメソッドです。

    引数で指定されたディレクトリ内でgit branchコマンドを実行します。

    Args:
        cwd (_type_):現在の作業ディレクトリ
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

def git_branch_for_remote(cwd):
    """指定したディレクトリ内のGitリポジトリでリモートブランチの一覧を取得するためのメソッドです。

    git_branch()を現在の作業ディレクトリと'-r'を引数に呼び出します。

    Args:
        cwd (_type_):現在の作業ディレクトリ

    Returns:
        str:コマンドの実行結果

    """
    return git_branch(cwd, '-r')

def is_annex_branch_in_repote(cwd):
    """origin/git-annexのリモートブランチが存在するか確認するメソッドです。。

    リモートブランチの一覧にorigin/git-annexが存在するか調べ、結果をbool型で返します。

    Args:
        cwd (_type_):現在の作業ディレクトリ

    Returns:
        bool:origin/git-annexが存在するかの判定結果

    """
    result = git_branch_for_remote(cwd)
    if 'origin/git-annex' in result:
        return True
    else:
        return False


def exec_git_status(cwd):
    """現在のgitリポジトリの状態を表示するメソッドです。

     引数で指定されたディレクトリ内でgit statusコマンドを実行します。

    Args:
        cwd (_type_):現在の作業ディレクトリ

    Returns:
        str:コマンドの実行結果
    """
    stdout, stderr, rt = Cmd.exec_subprocess('git status', cwd)
    result = stdout.decode('utf-8')
    return result

def is_conflict(cwd) -> bool:
    """現在のgitリポジトリに衝突しているものがないか確かめるメソッドです。

    gitリポジトリの状態を取得し、衝突しているものがないかをbool型で返します。

    Args:
        cwd (_type_):現在の作業ディレクトリ

    Returns:
        bool:衝突しているものがないかの判定
    """
    result = exec_git_status(cwd)
    lines = result.split('\n')
    for l in lines:
        if 'both modified:' in l or 'both added:' in l:
            return True
    return False
