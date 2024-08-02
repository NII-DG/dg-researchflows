"""Vaultサーバーへの接続

このモジュールはVaultサーバーに接続するために必要な値の設定とチェックを行い、キーやポリシーを作成してサーバーを起動させ、接続確認を行うメソッドがあります。
"""
import hvac
import os
import requests
import subprocess
import threading
import time

from .error import UnusableVault

VAULT_ADDR = 'http://127.0.0.1:8200'
TOKEN_PATH = '/home/jovyan/.vault/token'
DG_ENGINE_NAME = 'dg-kv'
DG_POLICY_NAME = 'dg-policy'
DG_POLICY = '''\
path "dg-kv/*" {
  capabilities = [ "create", "read", "update", "delete", "list" ]
}
'''
TOKEN_TTL = '1m'
MAX_RETRY_COUNT = 5


def start_server():
    """サーバーを起動するメソッドです。"""
    config_path = os.path.join(
        os.environ['HOME'], 'data_gorvernance/library/data/vault-config.hcl')
    subprocess.Popen(
        ['vault', 'server', '-config', config_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


class Vault():
    """Vault Server操作クラスです"""

    def initialize(self):
        """Vault初期化を行うメソッドです"""
        try:
            self.__read_token()
            return
        except UnusableVault:
            pass

        self.__start_server()

        self.__create_dg_engine()
        self.__create_dg_policy()

    def set_value(self, key:str, value:str):
        """値の設定をするメソッドです

        Args:
            key(str):トークンをvaultで保存するときのキー
            value(str):パーソナルトークン
        """
        client = self.__get_client()
        client.secrets.kv.v1.create_or_update_secret(
            path=key,
            secret=dict(secret=value),
            mount_point=DG_ENGINE_NAME,
        )

    def has_value(self, key:str) -> bool:
        """値の存在チェックをするメソッドです

        Args:
            key(str):トークンをvaultで保存するときのキー

        Returns:
            bool:キーが存在した場合は秘密鍵のTrueの値を返し、存在しない場合はFalseの値を返す。
        """
        client = self.__get_client()
        try:
            secrets = client.secrets.kv.v1.list_secrets(
                path='',
                mount_point=DG_ENGINE_NAME,
            )
        except hvac.exceptions.InvalidPath:
            # キーが1つも存在しない場合
            return False
        return key in secrets['data']['keys']

    def get_value(self, key:str) -> dict:
        """値の取得をするメソッドです

        Args:
            key(str):トークンをvaultで保存するときのキー

        Returns:
            dict:取得した値を返す。値がない場合はNoneを返す。
        """
        if not self.has_value(key):
            return None

        client = self.__get_client()
        read_res = client.secrets.kv.v1.read_secret(
            path=key,
            mount_point=DG_ENGINE_NAME,
        )
        return read_res['data']['secret']

    def __start_server(self):
        """Vaultサーバー起動するメソッドです。

        Raises:
            UnusableVault:値が利用できないエラー
        """

        # vaultサーバー起動
        thread = threading.Thread(target=start_server)
        thread.start()
        # 起動処理が終わるまで少し待機
        time.sleep(1)

        shares = 5
        threshold = 3
        client = hvac.Client(url=VAULT_ADDR)

        # サーバー初期化
        retry_count = 0
        while True:
            try:
                result = client.sys.initialize(shares, threshold)
                break
            except requests.ConnectionError:
                retry_count = retry_count + 1
            if retry_count >= MAX_RETRY_COUNT:
                # 規定回数以上失敗した場合はエラーとする
                raise UnusableVault
            # 起動がまだ完了していない可能性があるので少し待機
            time.sleep(1)

        # unseal
        unseal_keys = result['keys']
        for index in range(threshold):
            client.sys.submit_unseal_key(unseal_keys[index])

        # root token保存
        root_token = result['root_token']
        self.__write_token(root_token)

    def __create_dg_engine(self):
        """シークレットエンジン(kv)作成をするメソッドです"""
        token = self.__read_token()
        client = hvac.Client(url=VAULT_ADDR, token=token)

        secrets_engines = client.sys.list_mounted_secrets_engines()['data']
        if f'{DG_ENGINE_NAME}/' not in secrets_engines:
            client.sys.enable_secrets_engine(
                backend_type='kv',
                path=DG_ENGINE_NAME,
                description='kv for data governance'
            )

    def __create_dg_policy(self):
        """ポリシー作成をするメソッドです"""
        token = self.__read_token()
        client = hvac.Client(url=VAULT_ADDR, token=token)

        policies = client.sys.list_policies()['data']['policies']
        if DG_POLICY_NAME not in policies:
            client.sys.create_or_update_policy(
                name=DG_POLICY_NAME,
                policy=DG_POLICY,
            )

    def __write_token(self, token:str):
        """ルートトークン保存のメソッドです

        Args:
            token(str):パーソナルアクセストークン
        """
        with open(TOKEN_PATH, 'w') as f:
            f.write(token)

    def __read_token(self) -> str:
        """ルートトークン取得のメソッドです

        Raises:
            UnusableVault:値が利用できないエラー

        Returns:
            str:ルートトークンの値を返す。
        """
        if not os.path.isfile(TOKEN_PATH):
            raise UnusableVault

        with open(TOKEN_PATH, 'r') as f:
            root_token = f.read()
        return root_token

    def __get_client(self) -> hvac.Client:
        """接続の確認を行うメソッドです

        Returns:
            hvac.Client:接続先のページを表示する。
        """
        root_token = self.__read_token()
        client = hvac.Client(url=VAULT_ADDR, token=root_token)
        token_res = client.auth.token.create(
            policies=[DG_POLICY_NAME],
            ttl=TOKEN_TTL,
        )
        token = token_res['auth']['client_token']
        return hvac.Client(url=VAULT_ADDR, token=token)
