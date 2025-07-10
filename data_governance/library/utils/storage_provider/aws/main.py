"""AWS S3バケットからディレクトリまたはファイルをダウンロードするための関数が記載されたモジュールです。"""
import boto3

from .models import download_dir, download_file


def download(access_key: str, secret_key: str, bucket_name: str, aws_path: str, local_path: str):
    """AWS S3バケットからディレクトリまたはファイルをダウンロードするための関数です。

    Args:
        access_key (str):クライアント作成に用いるアクセスキー
        secret_key (str):クライアント作成に用いるシークレットキー
        bucket_name (str):バケット名
        aws_path (str):ダウンロードするファイル、ディレクトリへのパス
        local_path (str):ダウンロードしたファイル、ディレクトリの保存先を指定するパス

    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    if aws_path.endswith("/"):
        download_dir(s3_client, bucket_name, aws_path, local_path)
    else:
        download_file(s3_client, bucket_name, aws_path, local_path)
