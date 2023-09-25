import re
import git
import os
import json
from urllib import parse
from pathlib import Path
from http import HTTPStatus
import api as gin_api
from ....utils.config.param import ParamConfig
from ...error import Unauthorized
from ...config import path_config, message as msg_config
from ....utils.cmd import Cmd
from datalad import api as datalad_api
import requests

# param.jsonのファイルパス
script_dir_path = os.path.dirname(__file__)
srp_path = Path(script_dir_path)
PARAM_FILE_PATH = srp_path.joinpath('../../../..', 'researchflow/params.json').resolve()

# .repository_idのファイルパス
srp_path = Path(script_dir_path)
REPOSITORY_ID_FILE_PATH = srp_path.joinpath('../../../../..', '.repository_id').resolve()

# token.jsonのファイルパス
srp_path = Path(script_dir_path)
TOKEN_FILE_PATH = srp_path.joinpath('../../../..', path_config.TOKEN_JSON_PAHT).resolve()

# user_info.jsonのファイルパス
srp_path = Path(script_dir_path)
TOKEN_FILE_PATH = srp_path.joinpath('../../../..', path_config.USER_INFO_PATH).resolve()

SSH_DIR_PATH = ".ssh"
__SSH_KEY_PATH = os.path.join(SSH_DIR_PATH, "id_ed25519")
__SSH_PUB_KEY_PATH = os.path.join(SSH_DIR_PATH, "id_ed25519.pub")
__SSH_CONFIG = os.path.join(SSH_DIR_PATH, "config")


def extract_url_and_auth_info_from_git_url(git_url):
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
    git_url = git.get_remote_url()
    url, username, password = extract_url_and_auth_info_from_git_url(git_url)
    pr = parse.urlparse(url)
    gin_base_url = parse.urlunparse((pr.scheme, pr.scheme))
    return gin_base_url

def get_gin_base_url_and_auth_info_from_git_config():
    git_url = git.get_remote_url()
    url, username, password = extract_url_and_auth_info_from_git_url(git_url)
    pr = parse.urlparse(url)
    gin_base_url = parse.urlunparse((pr.scheme, pr.scheme))
    return gin_base_url, username, password



def init_param_url():
    """param.jsonのsiblings.ginHttpとsiblings.ginSshを更新する。

    ARG
    ---------------
    remote_origin_url : str
        Description : git config remote.origin.urlの値

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

            # with open(PARAM_FILE_PATH, 'r') as file:
            #     df = json.load(file)

            pc = ParamConfig.get_param_data()


            response_data = response.json()
            http_url = response_data["http"]
            if http_url[-1] == '/':
                http_url = http_url.rstrip('/')

            pc._siblings._ginHttp = http_url
            pc._siblings._ginSsh = response_data["ssh"]

            # df["siblings"]["ginHttp"] = http_url
            # df["siblings"]["ginSsh"] = response_data["ssh"]

            with open(REPOSITORY_ID_FILE_PATH, 'r') as file:
                repo_id = file.read()

            # df["repository"]["id"] = repo_id
            pc._repository._id = repo_id


            # with open(PARAM_FILE_PATH, 'w') as f:
            #     json.dump(df, f, indent=4)

            pc.update()

        elif response.status_code == HTTPStatus.NOT_FOUND:
            retry_num -= 1
            if retry_num == 0:
                flg = False
                raise Exception('Not Found GIN-Fork Server Info')

def setup_local(user_name, password):
    pr = parse.urlparse(ParamConfig.get_siblings_ginHttp())
    response = gin_api.get_token_for_auth(pr.scheme, pr.netloc, user_name, password)

    ## Unauthorized
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        raise Unauthorized
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
    token_dict = {"ginfork_token": token}
    os.makedirs(os.path.dirname(TOKEN_FILE_PATH), exist_ok=True)
    with TOKEN_FILE_PATH.open('w') as f:
        json.dump(token_dict, f, indent=4)

def get_ginfork_token():
    with TOKEN_FILE_PATH.open('r') as f:
        data = json.loads(f.read())
    return data['ginfork_token']

def set_user_info(user_id):
    user_info = {"user_id":user_id}
    os.makedirs(os.path.dirname(TOKEN_FILE_PATH), exist_ok=True)
    with TOKEN_FILE_PATH.open( 'w') as f:
        json.dump(user_info, f, indent=4)

def exist_user_info()->bool:
    return os.path.exists(TOKEN_FILE_PATH)

def del_build_token():
    gin_base_url, username, token = get_gin_base_url_and_auth_info_from_git_config()
    if len(token) >= 0:
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
    """dataladのデータセット化する

    Args:
        path (str): データセット化するディレクトリのパス
    """
    if not os.path.isdir(os.path.join(dir_path, ".datalad")):
        datalad_api.create(path=dir_path, force=True) # type: ignore
        return True
    else:
        return False

def create_key(root_path):
    """SSHキーを作成"""
    ssh_key_path = os.path.join(root_path, __SSH_KEY_PATH)
    if not os.path.isfile(ssh_key_path):
        Cmd.exec_subprocess(f'ssh-keygen -t ed25519 -N "" -f {__SSH_KEY_PATH}')
        return True
    else:
        return False

def upload_ssh_key(root_path):
    """GIN-forkへ公開鍵を登録"""
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
    ginHttp = ParamConfig.get_siblings_ginHttp()
    config_GIN(root_path, ginHttp)

def config_GIN(root_path, ginHttp):
    """リポジトリホスティングサーバのURLからドメイン名を抽出してコンテナに対してSHH通信を信頼させるメソッド
        この時、/home/jovyan/.ssh/configファイルに設定値を出力する。
    ARG
    ---------------------------
    ginHttp : str
        Description : リポジトリホスティングサーバのURL ex : http://dg01.dg.rcos.nii.ac.jp
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
    with open(ssh_config_path, mode) as f:
        f.write('\nhost ' + ginDomain + '\n')
        f.write('\tStrictHostKeyChecking no\n')
        f.write('\tUserKnownHostsFile=/dev/null\n')
