"""GINを用いた通信に関連する関数を記載しています。
"""
import re
import shutil
import subprocess
import traceback
import os
import json
from urllib import parse
from pathlib import Path
from http import HTTPStatus
from ..gin import api as gin_api, git
from ....utils.config.param import ParamConfig
from ...error import UnauthorizedError, RepositoryNotExist, UrlUpdateError, NoValueInDgFileError
from ...config import path_config, message as msg_config
from ....utils.cmd import Cmd
from datalad import api as datalad_api
from datalad.api import Dataset
import requests
import hashlib
import magic
from IPython.display import clear_output, display
from IPython.core.display import HTML
clear_output()

SIBLING = 'gin'

# param.jsonのファイルパス
script_dir_path = os.path.dirname(__file__)
srp_path = Path(script_dir_path)
PARAM_FILE_PATH = srp_path.joinpath('../../../..', 'researchflow/params.json').resolve()

# .repository_idのファイルパス
srp_path = Path(script_dir_path)
REPOSITORY_ID_FILE_PATH = srp_path.joinpath('../../../../..', '.repository_id').resolve()

# token.jsonのファイルパス
srp_path = Path(script_dir_path)
TOKEN_FILE_PATH = srp_path.joinpath('../../../../..', path_config.TOKEN_JSON_PAHT).resolve()

# user_info.jsonのファイルパス
srp_path = Path(script_dir_path)
USER_INFO_PATH = srp_path.joinpath('../../../../..', path_config.USER_INFO_PATH).resolve()

SSH_DIR_PATH = ".ssh"
__SSH_KEY_PATH = os.path.join(SSH_DIR_PATH, "id_ed25519")
__SSH_PUB_KEY_PATH = os.path.join(SSH_DIR_PATH, "id_ed25519.pub")
__SSH_CONFIG = os.path.join(SSH_DIR_PATH, "config")

# orig_gitignoreのファイルパス
srp_path = Path(script_dir_path)
ORIG_GITIGNORE_PATH  = srp_path.joinpath('../../..', 'data/original_gitignore').resolve()


def extract_url_and_auth_info_from_git_url(git_url):
    """指定されたGitのURLからプロトコル、ユーザ名、パスワード、ドメインを抜き出すメソッドです。

    引数として受け取ったgit_urlからパターンと一致するものを抽出し、変換したものを戻り値として返します。

    Args:
        git_url (Any):指定されたGitのURL

    Returns:
        str:抽出した文字列から新たに作成したurl
        str:ユーザー名
        str:パスワード

        Any:元のurl
        str:空のユーザー名
        str:空のパスワード

    """
    pattern = r"(http[s]?://)([^:]+):([^@]+)@(.+)"
    match = re.search(pattern, git_url)
    if match:
        protocol = match.group(1)
        username = match.group(2)
        password = match.group(3)
        domain = match.group(4)

        # Generate URL without username and password
        # domain includes paths
        new_url = f"{protocol}{domain}"
        return new_url, username, password

    return git_url, "", "" # Returns the original URL if it cannot be converted

def get_gin_base_url_from_git_config()->str:
    """GINのベースurlを作成するメソッドです。

    git.get_remote_url()メソッドを用いてリモートurlを取得し、それを用いて作成したベースurlを戻り値として返します。

    Returns:
        str:ベースurl

    """
    git_url = git.get_remote_url()
    url, username, password = extract_url_and_auth_info_from_git_url(git_url)
    pr = parse.urlparse(url)
    gin_base_url = parse.urlunparse((pr.scheme, pr.netloc, "", "", "", ""))
    return gin_base_url

def get_gin_base_url_and_auth_info_from_git_config():
    """GINのベースurlを作成と認証情報の取得を行うメソッドです。

    git.get_remote_url()メソッドを用いてリモートurlを取得し、
    それを用いて作成したベースurlと認証情報を戻り値として返します。

    Returns:
        str:ベースurl
        str:ユーザー名
        str:パスワード

    """
    git_url = git.get_remote_url()
    url, username, password = extract_url_and_auth_info_from_git_url(git_url)
    pr = parse.urlparse(url)
    gin_base_url = parse.urlunparse((pr.scheme, pr.netloc, "", "", "", ""))
    return gin_base_url, username, password

def init_param_url():
    """パラメーター設定の初期化を行うメソッドです。

    新たにベースurlを取得し、それを用いてparam.jsonのsiblings.ginHttpとsiblings.ginSshの更新を行います。

    Raises:
        Exception: GIN-Forkサーバーの情報が見つからない

    Note:
        EXCEPTION
        ---------------
        requests.exceptions.RequestException :
        Description : 接続の確立不良。
        From : 下位モジュール

    """
    gin_base_url = get_gin_base_url_from_git_config()


    pr = parse.urlparse(gin_base_url)
    retry_num = 6
    flg = True
    while flg:
        response = gin_api.get_server_info(pr.scheme, pr.netloc)
        if response.status_code == HTTPStatus.OK:
            flg = False

            pc = ParamConfig.get_param_data()


            response_data = response.json()
            http_url = response_data["http"]
            if http_url[-1] == '/':
                http_url = http_url.rstrip('/')

            pc._siblings._ginHttp = http_url
            pc._siblings._ginSsh = response_data["ssh"]


            with open(REPOSITORY_ID_FILE_PATH, 'r') as file:
                repo_id = file.read()

            pc._repository._id = repo_id

            pc.update()

        elif response.status_code == HTTPStatus.NOT_FOUND:
            retry_num -= 1
            if retry_num == 0:
                flg = False
                raise Exception('Not Found GIN-Fork Server Info')

def setup_local(user_name, password):
    """ローカル環境の設定を行うメソッドです。

    引数として受け取った認証情報を用いてアクセストークンを取得し、それを用いてローカル環境の設定を行います。

    Args:
        user_name (Any):ユーザー名
        password (Any):パスワード

    Raises:
        UnauthorizedError:認証情報が無効である

    """
    pr = parse.urlparse(ParamConfig.get_siblings_ginHttp())
    response = gin_api.get_token_for_auth(pr.scheme, pr.netloc, user_name, password)

    ## Unauthorized
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        raise UnauthorizedError
    response.raise_for_status()

    ## Check to see if there is an existing token
    access_token = dict()
    tokens = response.json()
    if len(tokens) >= 1:
        access_token = response.json()[-1]
    elif len(tokens) < 1:
        response = gin_api.create_token_for_auth(pr.scheme, pr.netloc, user_name, password)
        if response.status_code == HTTPStatus.CREATED:
            access_token = response.json()
        response.raise_for_status()

    # Write out the GIN-fork access token
    set_ginfork_token(access_token['sha1'])

    # Get user info
    response = gin_api.get_user_info(pr.scheme, pr.netloc, access_token['sha1'])
    response.raise_for_status()

    # Set user info
    res_data = response.json()
    set_user_info(user_id=res_data['id'])
    Cmd.exec_subprocess(cmd='git config --global user.name {}'.format(res_data['username']))
    Cmd.exec_subprocess(cmd='git config --global user.email {}'.format(res_data['email']))

def set_ginfork_token(token:str):
    """トークンをファイルに保存するためのメソッドです。

    引数として受け取ったトークンを辞書型のデータに変換した後、トークンファイルに書き込むことで保存します。

    Args:
        token (str): 保存するトークン

    """
    token_dict = {"ginfork_token": token}
    os.makedirs(os.path.dirname(TOKEN_FILE_PATH), exist_ok=True)
    with TOKEN_FILE_PATH.open('w') as f:
        json.dump(token_dict, f, indent=4)

def get_ginfork_token():
    """保存されたトークンを取得するためのメソッドです。

    トークンファイルを読み出し、'ginfork_token'キーの値を戻り値として返します。

    Returns:
        Any:取得したトークン

    """
    with TOKEN_FILE_PATH.open('r') as f:
        data = json.loads(f.read())
    return data['ginfork_token']

def set_user_info(user_id):
    """ユーザーIDを保存するためのメソッドです。

    引数として受け取ったuser_idを辞書型のデータに変換した後、ユーザー情報のファイルに書き込むことで保存します。

    Args:
        user_id (Any):ユーザーID

    """
    user_info = {"user_id":user_id}
    os.makedirs(os.path.dirname(USER_INFO_PATH), exist_ok=True)
    with USER_INFO_PATH.open( 'w') as f:
        json.dump(user_info, f, indent=4)

def get_user_id_from_user_info():
    """保存されたユーザーIDを取得するメソッドです。

    ユーザー情報のファイルを読み出し、'user_id'キーの値を戻り値として返します。

    Returns:
        Any: 取得したユーザーID

    """
    with USER_INFO_PATH.open('r') as f:
        data = json.loads(f.read())
    return data['user_id']

def exist_user_info()->bool:
    """ユーザー情報が存在しているかを確認するメソッドです。

    ユーザー情報が保存されているファイルが存在しているかを確認し、その結果を戻り値として返します。

    Returns:
        bool: ユーザー情報が保存されているファイルが存在しているかの結果

    """
    return os.path.exists(USER_INFO_PATH)

def del_build_token():
    """トークンの削除を行うメソッドです。

    get_gin_base_url_and_auth_info_from_git_config()を呼び出してトークンを取得し、削除を行います。

    Returns:
        bool:トークンが存在しているかの判定
        str:トークンの削除処理がどのように行われたかのメッセージ

    """
    gin_base_url, username, token = get_gin_base_url_and_auth_info_from_git_config()
    if len(token) > 0:
        # プライベート
        pr = parse.urlparse(gin_base_url)
        response = gin_api.delete_access_token(pr.scheme, pr.netloc, token=token)
        if response.status_code == HTTPStatus.OK:
            return True , ''
        elif response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
            return True , msg_config.get('build_token', 'already_delete')
        elif response.status_code == HTTPStatus.UNAUTHORIZED:
            return True, msg_config.get('build_token', 'already_delete')
        else:
            return False, msg_config.get('build_token', 'error') + 'Code[{}]'.format(response.status_code)
    else:
        return True , None

def datalad_create(dir_path:str):
    """指定したディレクトリをdataladのデータセット化するメソッドです。

    引数として受け取ったパスのディレクトリをdataladのデータセットに変換します。

    Args:
        path (str): データセット化するディレクトリのパス

    Returns:
        bool:既にdataladのデータセットであるかの判定を行う

    """
    if not os.path.isdir(os.path.join(dir_path, ".datalad")):
        datalad_api.create(path=dir_path, force=True) # type: ignore
        return True
    else:
        return False

def create_key(root_path):
    """SSHキーを作成するメソッドです。

    引数として受け取ったroot_pathディレクトリにSSHキーが存在しない場合のみ新たにSSHキーを作成します。

    Args:
        root_path (Any):SSHキーを作成するディレクトリのルートパス

    Returns:
        bool:SSHキーを作成したかの判定を行う

    """
    ssh_key_path = os.path.join(root_path, __SSH_KEY_PATH)
    if not os.path.isfile(ssh_key_path):
        Cmd.exec_subprocess(f'ssh-keygen -t ed25519 -N "" -f {ssh_key_path}')
        return True
    else:
        return False

def upload_ssh_key(root_path):
    """GIN-forkへ公開鍵をアップロードするメソッドです。

    引数として受け取ったroot_pathを用いて公開鍵を読み込み、GIN-forkへアップロードし、処理に対応したメッセージを返します。

    Args:
        root_path (Any):公開鍵の存在するディレクトリのルートパス

    Raises:
        Exception:公開鍵のアップロードに失敗した

    Returns:
        str:実行した処理に対応したメッセージ

    """
    ssh_pub_key_path = os.path.join(root_path, __SSH_PUB_KEY_PATH)

    with open(ssh_pub_key_path, mode='r') as f:
        ssh_key = f.read()

    pr = parse.urlparse(ParamConfig.get_siblings_ginHttp())
    response = gin_api.upload_key(pr.scheme, pr.netloc, get_ginfork_token(), ssh_key)
    msg = response.json()

    if response.status_code == HTTPStatus.CREATED:
        return msg_config.get('setup', 'ssh_upload_success')
    elif msg['message'] == 'Key content has been used as non-deploy key':
        return msg_config.get('setup', 'ssh_already_upload')
    else:
        raise Exception(f'Fial Upload pub-SSH key. Response Code [{response.status_code}]')

def trust_gin(root_path):
    """GINの信頼設定を行うメソッドです。

    引数として受け取ったroot_pathと取得したGINのurlを用いて信頼設定を行います。

    Args:
        root_path (Any):設定ファイルの保存されているディレクトリのルートパス

    """
    ginHttp = ParamConfig.get_siblings_ginHttp()
    config_GIN(root_path, ginHttp)

def config_GIN(root_path, ginHttp):
    """ドメインを信頼するための設定を行うメソッドです。

    引数として受け取ったリポジトリホスティングサーバのURL(ginHttp)からドメイン名を抽出し、コンテナに対してSHH通信を信頼させます。
    この時、/home/jovyan/.ssh/configファイルに設定値を出力します。

    Args:
        root_path(Any):設定値を出力するファイルのルートパス
        ginHttp(Any):リポジトリホスティングサーバのURL  ex : http://dg01.dg.rcos.nii.ac.jp

    """
    # SSHホスト（＝GIN）を信頼する設定
    ssh_config_path = os.path.join(root_path, __SSH_CONFIG)
    s = ''
    pr = parse.urlparse(ginHttp)
    ginDomain = pr.netloc
    if os.path.exists(ssh_config_path):
        with open(ssh_config_path, 'r') as f:
            s = f.read()
        if s.find('host ' + ginDomain + '\n\tStrictHostKeyChecking no\n\tUserKnownHostsFile=/dev/null') == -1:
            # 設定が無い場合は追記する
            with open(ssh_config_path, mode='a') as f:
                write_GIN_config(mode='a', ginDomain=ginDomain, ssh_config_path=ssh_config_path)
        else:
            # すでにGINを信頼する設定があれば何もしない
            pass
    else:
        # 設定ファイルが無い場合は新規作成して設定を書きこむ
        with open(ssh_config_path, mode='w') as f:
            write_GIN_config(mode='w', ginDomain=ginDomain, ssh_config_path=ssh_config_path)

def write_GIN_config(mode, ginDomain, ssh_config_path):
    """SSH設定ファイルに特定のドメインを信頼する設定を書き込むメソッドです。

    SSH設定ファイルを引数指定されたで形式で開き、信頼させるドメインを書き込みます。

    Args:
        mode (Any):ファイルを開くモード
        ginDomain (Any):信頼させるドメイン
        ssh_config_path (Any):SSH設定ファイルへのパス

    """
    with open(ssh_config_path, mode) as f:
        f.write('\nhost ' + ginDomain + '\n')
        f.write('\tStrictHostKeyChecking no\n')
        f.write('\tUserKnownHostsFile=/dev/null\n')

def prepare_sync(root):
    """同期するコンテンツの調整を行うメソッドです。

    引数として受け取ったルートパスを用いて同期の制限とコピーの作成を行います。

    Args:
        root(Any):ルートパス

    """
    # S3にあるデータをGIN-forkに同期しないための設定
    git.git_annex_untrust(root)
    git.git_annex_trust(root)

    # 元ファイルからコピーして.gitignoreを作成
    file_path = os.path.join(root, '.gitignore')
    orig_file_path = os.path.join(root, ORIG_GITIGNORE_PATH)
    if not os.path.isfile(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        shutil.copyfile(orig_file_path, file_path)

def setup_sibling_to_local():
    """リポジトリをローカルのデータセットに設定するためのメソッドです。

    GIN API を使用してリポジトリを取得し、それをローカルのデータセットに設定します。

    Raises:
        RepositoryNotExist: リポジトリが存在しない

    """
    ginfork_token = get_ginfork_token()
    repo_id = ParamConfig.get_repo_id()
    user_id =get_user_id_from_user_info()
    ginHttp = ParamConfig.get_siblings_ginHttp()
    pr = parse.urlparse(ginHttp)
    response = gin_api.search_repo(pr.scheme, pr.netloc, repo_id, user_id, ginfork_token)
    response.raise_for_status() # ステータスコードが200番台でない場合はraise HTTPError
    res_data = response.json()
    if len(res_data['data']) == 0:
            raise RepositoryNotExist
    ssh_url = res_data['data'][0]['ssh_url']
    http_url = res_data['data'][0]['html_url'] + '.git'
    # Note:
    #   action='add'では既に存在する場合にIncompleteResultsErrorになる
    #   action='config'では無ければ追加、あれば上書き
    #   refs: https://docs.datalad.org/en/stable/generated/datalad.api.siblings.html
    datalad_api.siblings(action='configure', name='origin', url=http_url)
    datalad_api.siblings(action='configure', name=SIBLING, url=ssh_url)

def push_annex_branch(cwd):
    """git-annexブランチをプッシュするメソッドです。

    引数で指定した現在の作業ディレクトリ(cwd)でプルした後、git-annexブランチがリモートに存在しない場合のみプッシュします。

    Args:
        cwd(Any):現在の作業ディレクトリ

    """
    git.git_pull(cwd)
    if git.is_annex_branch_in_repote(cwd):
        pass
    else:
        Cmd.exec_subprocess(cmd=f'git push {SIBLING} git-annex:git-annex', cwd=cwd)

def syncs_with_repo(cwd:str, git_path:list[str], gitannex_path:list[str], gitannex_files :list[str], message:str, get_paths:list[str],):
    """Git Annexリポジトリの同期を行うメソッドです。

    Args:
        cwd (str):現在の作業ディレクトリ
        git_path (list[str]):gitで管理するディレクトリとファイルのパス
        gitannex_path (list[str]):git Annexで管理するディレクトリとファイルのパス
        gitannex_files (list[str]):メタデータ(content_size, sha256, mime_type)を追加するファイル(メタデータを追加しない場合は None を指定)
        message (str):コミットメッセージ
        get_paths (list[str]):取得するデータセットへのパス

    Returns:
        bool:同期の成功判定

    note:
        update()を最初にするとgit annex lockができない。addをする必要がある。

    """
    success_message = ''
    warm_message = ''
    error_message = ''
    datalad_error = ''
    try:

        # os.chdir(p.HOME_PATH)
        print('[INFO] Lock git-annex content')
        # os.system('git annex lock')
        git.git_annex_lock(cwd)
        print('[INFO] Save git-annex content and Register metadata')
        save_annex_and_register_metadata(cwd, gitannex_path, gitannex_files, message)
        print('[INFO] Uulock git-annex content')
        #os.system('git annex unlock')
        git.git_annex_unlock(cwd)
        print('[INFO] Save git content')
        save_git(git_path, message)
        print('[INFO] Lock git-annex content')
        #os.system('git annex lock')
        git.git_annex_lock(cwd)
        print('[INFO] Update and Merge Repository')
        update()
        if len(get_paths)>0:
            datalad_api.get(path=get_paths)
    except:
        datalad_error = traceback.format_exc()
        # if there is a connection error to the remote, try recovery
        if 'Repository does not exist' in datalad_error or 'failed with exitcode 128' in datalad_error:
            try:
                # update URLs of remote repositories
                update_repo_url()
                print('[INFO] Update repository URL')
                warm_message = msg_config.get('sync', 'resync_repo_rename')
            except RepositoryNotExist:
                # repository may not exist
                error_message = msg_config.get('sync', 'connect_repo_error')
            except requests.exceptions.RequestException:
                error_message = msg_config.get('sync', 'connection_error')
            except UrlUpdateError:
                error_message = msg_config.get('sync', 'unexpected')
        elif 'files would be overwritten by merge:' in datalad_error:
            print('[INFO] Files would be overwritten by merge')
            git_commit_msg = '{}(auto adjustment)'.format(message)
            err_key_info = extract_info_from_datalad_update_err(datalad_error)
            file_paths = list[str]()
            # os.chdir(p.HOME_PATH)
            # os.system('git annex lock')
            git.git_annex_lock(cwd)
            if 'The following untracked working tree' in err_key_info:
                file_paths = get_filepaths_from_dalalad_error(err_key_info)
                adjust_add_git_paths = list[str]()
                adjust_add_annex_paths = list[str]()
                for path in file_paths:
                    if '\\u3000' in path:
                        path = path.replace('\\u3000', '　')
                    if is_should_annex_content_path(path):
                        if not path.startswith(cwd):
                            path = os.path.join(cwd, path)
                        adjust_add_annex_paths.append(path)
                    else:
                        if not path.startswith(cwd):
                             path = os.path.join(cwd, path)
                        adjust_add_git_paths.append(path)
                print('[INFO] git add. path : {}'.format(adjust_add_git_paths))
                print('[INFO] git annex add. path : {}'.format(adjust_add_annex_paths))
                print('[INFO] Save git-annex content and Register metadata(auto adjustment)')
                save_annex_and_register_metadata(cwd, adjust_add_annex_paths, adjust_add_annex_paths, git_commit_msg)
                #os.system('git annex unlock')
                git.git_annex_unlock(cwd)
                print('[INFO] Save git content(auto adjustment)')
                save_git(adjust_add_git_paths, message)
            elif 'Your local changes to the following' in err_key_info:
                if 'Please commit your changes or stash them before you merge' in err_key_info:
                    file_paths = get_filepaths_from_dalalad_error(err_key_info)
                    adjust_add_git_paths = list[str]()
                    adjust_add_annex_paths = list[str]()
                    for path in file_paths:
                        if '\\u3000' in path:
                            path = path.replace('\\u3000', '　')
                        if is_should_annex_content_path(path):
                            if not path.startswith(cwd):
                                path = os.path.join(cwd, path)
                            adjust_add_annex_paths.append(path)
                        else:
                            if not path.startswith(cwd):
                                path = os.path.join(cwd, path)
                            adjust_add_git_paths.append(path)
                    print('[INFO] git add. path : {}'.format(adjust_add_git_paths))
                    print('[INFO] git annex add. path : {}'.format(adjust_add_annex_paths))
                    print('[INFO] Save git-annex content and Register metadata(auto adjustment)')
                    save_annex_and_register_metadata(cwd, adjust_add_annex_paths, adjust_add_annex_paths, git_commit_msg)
                    # os.system('git annex unlock')
                    git.git_annex_unlock(cwd)
                    print('[INFO] Save git content(auto adjustment)')
                    save_git(adjust_add_git_paths, message)
                else:
                    result = git.git_commmit(git_commit_msg, cwd)
                    print(result)
            warm_message = msg_config.get('sync', 'resync_by_overwrite')
        else:
            # check both modified
            if git.is_conflict(cwd):
                print('[INFO] Files is CONFLICT')
                error_message = msg_config.get('sync', 'conflict_error')
            else:
                error_message = msg_config.get('sync', 'unexpected')
    else:
        try:
            print('[INFO] Push to Remote Repository')
            push()
            print('[INFO] Unlock git-annex content')
            #os.system('git annex unlock')
            git.git_annex_unlock(cwd)
        except:
            datalad_error = traceback.format_exc()
            error_message = msg_config.get('sync', 'push_error')
        else:
            # os.chdir(p.HOME_PATH)
            success_message = msg_config.get('sync', 'success')
    finally:
        clear_output()
        if success_message:
            display_info(success_message)
            # GIN-forkの実行環境一覧の更新日時を更新する
            # patch_container()
            return True
        else:
            display_warm(warm_message)
            display_err(error_message)
            display_log(datalad_error)
            return False

def save_annex_and_register_metadata(cwd, gitannex_path :list[str], gitannex_files:list[str], message:str):
    """detaladの保存とメタデータの登録を行うメソッドです。

    引数で指定されたファイルに対してdetaladへの保存を行った後、メタデータの登録を行うメソッドです。

    Args:
        cwd (Any):現在の作業ディレクトリ
        gitannex_path (list[str]):git-annexに追加するファイルパスのリスト
        gitannex_files (list[str]):メタデータを登録するファイルパスのリスト
        message (str):コミットメッセージ

    note:
        in the unlocked state, the entity of data downloaded from outside is also synchronized, so it should be locked.

    """
    # *The git annex metadata command can only be run on files that have already had a git annex add command run on them
    if len(gitannex_path) > 0:
        datalad_api.save(message=message + ' (git-annex)', path=gitannex_path)
        # register metadata for gitannex_files
        if type(gitannex_files) == str:
            register_metadata_for_annexdata(cwd, gitannex_files)
        elif type(gitannex_files) == list:
            for file in gitannex_files:
                register_metadata_for_annexdata(cwd, file)
        else:
            # if gitannex_files is not defined as a single file path (str) or multiple file paths (list), no metadata is given.
            pass

def register_metadata_for_annexdata(cwd:str, file_path):
    """指定したファイルにメタデータの登録を行うメソッドです。

    引数で指定したファイルに対してメタデータ(content_size, sha256, mime_type)の登録を行います。

    Args:
        cwd (str):現在の作業ディレクトリ
        file_path (Any):メタデータを登録するファイルパス

    """
    if os.path.isfile(file_path):
        # generate metadata
        # os.system('git annex unlock')
        git.git_annex_unlock(cwd)
        mime_type = magic.from_file(file_path, mime=True)
        with open(file_path, 'rb') as f:
            binary_data = f.read()
            sha256 = hashlib.sha3_256(binary_data).hexdigest()
        content_size = os.path.getsize(file_path)

        # register_metadata
        #os.system(f'git annex metadata "{file_path}" -s mime_type={mime_type} -s sha256={sha256} -s content_size={content_size}')
        git.git_annex_metadata_add_minetype_sha256_contentsize(file_path, mime_type, sha256, content_size, cwd)
    else:
        pass

def save_git(git_path:list[str], message:str):
    """変更をgitに保存するためのメソッドです。

    引数として受け取ったgit_pathが空ではない場合、変更を義っとに保存し、メッセージを出力します。

    Args:
        git_path (list[str]):保存したいファイルのパス
        message (str): コミットメッセージ

    """
    if len(git_path) > 0:
        datalad_api.save(message=message + ' (git)', path=git_path, to_git=True)

def update():
    """データセットの更新を行うメソッドです。

    datalad_api.updateメソッドを呼び出し、更新を行います。

    """
    datalad_api.update(sibling=SIBLING, how='merge')

def push():
    """データセットのプッシュを行うメソッドです。

    datalad_api.pushメソッドを呼び出し、プッシュを行います。

    """
    datalad_api.push(to=SIBLING, data='auto')

def is_should_annex_content_path(file_path : str)->bool:
    """指定されたファイルパスがannexの条件を満たすかを調べるメソッドです。

    引数として受け取ったファイルパスを分割し、条件を満たすかを調べ、結果を戻り値として返します。

    Args:
        file_path (str):指定されたファイルパス

    Returns:
        bool:条件を満たしているかの結果

    """
    path_factor = file_path.split('/')
    if path_factor[0] == 'experiments':
        if len(path_factor) >= 3 and (path_factor[2]=='input_data' or path_factor[2]=='output_data'):
            if len(path_factor) >= 4 and path_factor[3] == '.gitkeep':
                return False
            else:
                return True
        elif len(path_factor) >= 3 and (path_factor[2]=='source' or path_factor[2]=='ci'):
            return False
        elif len(path_factor) >= 3:
            if len(path_factor) >= 4 and path_factor[3] == 'output_data':
                return True
            else:
                return False
        else:
            return False
    else:
        return False

def get_filepaths_from_dalalad_error(err_info: str):
    """エラー情報から特定の文字列を抽出するメソッドです。

    引数として受け取った文字列(err_info)から特定のパターンと一致する部分を抽出し、リストにして返します。

    Args:
        err_info (str):エラー情報の文字列

    Returns:
        list:抽出した文字列のリスト

    """
    pattern = r"'\\t(.+?)\\n'"
    return re.findall(pattern, err_info)

def extract_info_from_datalad_update_err(raw_msg:str)->str:
    """エラーメッセージから特定の文章を抜き出すためのメソッドです。

    引数として受け取ったエラーメッセージから一部分だけを切り出し、戻り値として返します。

    Args:
        raw_msg (str):エラーメッセージ

    Returns:
        str:切り出した文字列

    """
    start_index = raw_msg.find("[") + 1
    end_index = raw_msg.rfind("]")
    err_info = raw_msg[start_index:end_index]
    start_index = err_info.find("{")
    end_index = err_info.find("}")
    err_detail_info = err_info[start_index:end_index+1]
    start_index = err_detail_info.find("[") + 1
    end_index= err_detail_info.find("]")
    return err_detail_info[start_index:end_index]

def creat_html_msg(msg='', fore=None, back=None, tag='h1'):
    """HTMLを生成するメソッドです。

    引数として受け取った情報からHTMLタグを生成し、戻り値として返します。

    Args:
        msg (str):メッセージ
        fore (Any): 前景色
        back (Any): 背景色
        tag (str): HTMLタグ

    Returns:
        str:生成したHTMLタグ

    """
    if fore is not None and back is not None:
        style: str = 'color:' + fore + ';' + 'background-color:' + back + ";"
    elif fore is not None and back is None:
        style = 'color:' + fore
    elif fore is None and back is not None:
        style = 'background-color:' + back
    else:
        style = ""

    if style != "":
        return "<" + tag + " style='" + style + "'>" + msg + "</" + tag + ">"
    else:
        return "<" + tag + " style='" + style + "'>" + msg + "</" + tag + ">"

def creat_html_msg_info_p(msg=''):
    """情報メッセージのHTMLタグを作成するためのメソッドです。

    引数として受け取ったmsgを用いてcreat_html_msgを呼び出し、タグを生成して戻り値として返します。

    Args:
        msg (str):メッセージ

    Returns:
        str: 生成した情報メッセージのHTMLタグ

    """
    return creat_html_msg(msg=msg, back='#9eff9e', tag='p')

def creat_html_msg_err_p(msg=''):
    """エラーメッセージのHTMLタグを作成するためのメソッドです。

    引数として受け取ったmsgを用いてcreat_html_msgを呼び出し、タグを生成して戻り値として返します。

    Args:
        msg (str):メッセージ

    Returns:
        str: 生成したエラーメッセージのHTMLタグ

    """
    return creat_html_msg(msg=msg, back='#ffa8a8', tag='p')


def display_html_msg(msg='', fore=None, back=None, tag='h1'):
    """メッセージを出力するメソッドです。

    引数として受け取った値を用いてcreat_html_msgを呼び出し、 display()で出力します。

    Args:
        msg (str): メッセージ
        fore (Any):前背景
        back (Any):背背景
        tag (str):タグ

    """
    html_text = creat_html_msg(msg, fore, back, tag)
    display(HTML(html_text))

def display_log(msg='', tag='p'):
    """赤文字でメッセージを出力するメソッド(文字色(#ff0000))です。

    引数として受け取った値を用いて赤文字でメッセージを出力します。

    Args:
        msg (str): メッセージ
        tag (str):タグ

    """
    fore = "#ff0000"
    display_html_msg(msg, fore, None, tag)

default_tag = "p"
"""メソッド : display_msg()、display_info()、display_err()、display_warm()のデフォルトのHTMLタグ種
"""


def display_msg(msg='', back=None):
    """標準メッセージ出力メソッド(pタグ)です。

    引数として受け取った値を用いて標準メッセージの出力を行います。

    Args:
        msg (str): メッセージ
        back (Any):背背景

    """
    display_html_msg(msg, None, back, default_tag)

def display_info(msg=''):
    """正常メッセージ出力メソッド(pタグの背景色(#9eff9e))です。

    引数として受け取ったmsgを用いて正常メッセージの出力を行います。

    Args:
        msg (str): メッセージ

    """
    back = "#9eff9e"
    display_html_msg(msg, None, back, default_tag)

def display_err(msg=''):
    """異常メッセージ出力メソッド(pタグの背景色(#ffa8a8))です。

    引数として受け取ったmsgを用いて異常メッセージの出力を行います。

    Args:
        msg (str): メッセージ

    """
    back = "#ffa8a8"
    display_html_msg(msg, None, back, default_tag)

def display_warm(msg=''):
    """警告メッセージ出力メソッド(pタグの背景色(#ffff93))です。

    引数として受け取ったmsgを用いて警告メッセージの出力を行います。

    Args:
        msg (str): メッセージ

    """
    back = "#ffff93"
    display_html_msg(msg, None, back, default_tag)

def display_debug(msg=''):
    """デバッグ用出力メソッド(pタグの背景色(#dcdcdc))です。

    引数として受け取ったmsgを用いてデバック用メッセージの出力を行います。

    Args:
        msg (str): メッセージ

    """
    back = "#dcdcdc"
    display_html_msg(msg, None, back, default_tag)

def update_repo_url():
    """HTTPとSSHのリモートURLを最新化するメソッドです。

    APIからリポジトリの最新のSSHのリモートURLを取得し、リモート設定を更新します。

    Returns:
        Any: プライベートリポジトリかどうかの判定を行う

    Raises:
        requests.exceptions.RequestException: 接続の確立不良
        RepositoryNotExist: リモートリポジトリの情報が取得できない
        UrlUpdateError: 想定外のエラーにより最新化に失敗した
    """

    try:
        # APIリクエストに必要な情報を取得する
        gin_http_url = ParamConfig.get_siblings_ginHttp()
        pr = parse.urlparse(gin_http_url)
        repo_id = ParamConfig.get_repo_id()

        # APIからリポジトリの最新のSSHのリモートURLを取得し、リモート設定を更新する
        res = gin_api.search_public_repo(pr.scheme, pr.netloc, repo_id)
        res_data = res.json()
        if len(res_data['data']) == 0:
            # 初期設定前の場合は取れない
            ginfork_token = get_ginfork_token()
            uid = get_user_id_from_user_info()
            res = gin_api.search_repo(pr.scheme, pr.netloc, repo_id, uid, ginfork_token)
            res_data = res.json()

        res.raise_for_status()
        if len(res_data['data']) == 0:
            raise RepositoryNotExist

        ssh_url = res_data['data'][0]['ssh_url']
        http_url = res_data['data'][0]['html_url'] + '.git'
        update_list = [[SIBLING, ssh_url],['origin', http_url]]
        for update_target in update_list:
            result = subprocess.run('git remote set-url ' + update_target[0] + ' ' + update_target[1], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if 'No such remote' in result.stderr:
                subprocess.run('git remote add ' + update_target[0] + ' ' + update_target[1], shell=True)
    except requests.exceptions.RequestException:
        raise
    except RepositoryNotExist:
        raise
    except NoValueInDgFileError:
        raise
    except Exception as e:
        raise UrlUpdateError from e

    is_private = res_data['data'][0]['private']
    return is_private
