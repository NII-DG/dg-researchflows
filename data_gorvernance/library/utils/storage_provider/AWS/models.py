"""AWS S3バケットからディレクトリまたはファイルをダウンロードする関数が記載されています。"""
import os


def download_file(s3_client, bucket_name:str, aws_path:str, local_path:str):
    """AWS S3バケットからファイルをダウンロードする関数です。

    指定されたAWS S3バケットにアクセスし、ファイルをダウンロードしてローカルに保存します。

    Args:
        s3_client (Any):AWS S3にアクセスするためのクライアント
        bucket_name (str):バケット名
        aws_path (str):ダウンロードするファイルへのパス
        local_path (str):ダウンロードしたファイルの保存先を指定するパス

    Raises:
        FileNotFoundError:指定したパスのファイルが存在しない
        FileExistsError:ダウンロード先のローカルパスが既に存在している

    """
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=aws_path)
    try:
        # キーの確認
        contents = response['Contents']
    except KeyError:
        # 転送元が存在しない
        raise FileNotFoundError
    if os.path.exists(local_path):
        raise FileExistsError
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    s3_client.download_file(bucket_name, aws_path, local_path)


def download_dir(s3_client, bucket_name:str, aws_dir:str, local_dir:str):
    """AWS S3バケットからディレクトリをダウンロードする関数です。

    指定されたAWS S3バケットにアクセスし、ディレクトリをダウンロードしてローカルに保存します。

    Args:
        s3_client(Any):AWS S3にアクセスするためのクライアント
        bucket_name(str):バケット名
        aws_dir(str):ダウンロードするディレクトリへのパス
        local_dir(str):ダウンロードしたディレクトリの保存先を指定するパス

    Raises:
        FileNotFoundError:指定したパスのファイルが存在しない
        FileExistsError:ダウンロード先のローカルパスが既に存在している

    """
    paths = {}
    next_token = None
    while True:
        if next_token is None:
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=aws_dir)
        else:
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=aws_dir, ContinuationToken=next_token)

        try:
            contents = response['Contents']
        except KeyError:
            # 転送元が存在しない
            raise FileNotFoundError

        for s3_object_response in contents:
            # S3オブジェクト側のファイルパスを取得する
            s3_file_path = s3_object_response['Key']

            if s3_file_path.endswith("/"):
                continue

            relative_path = os.path.relpath(s3_file_path, aws_dir)
            local_object_file_path = os.path.join(local_dir, relative_path)

            # ローカル側にディレクトリパスが存在するか確認する
            if os.path.exists(local_object_file_path):
                raise FileExistsError
            paths[s3_file_path] = local_object_file_path

        if 'NextContinuationToken' in response:
            next_token = response['NextContinuationToken']
        else:
            next_token = None
            break

    for aws_file, local_file in paths.items():
        os.makedirs(os.path.dirname(local_file), exist_ok=True)
        s3_client.download_file(bucket_name, aws_file, local_file)