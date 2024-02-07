import boto3

from .models import download_dir, download_file

def download(access_key:str, secret_key:str, bucket_name:str, aws_path:str, local_path:str):

    s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )

    if aws_path.endswith("/"):
        download_dir(s3_client, bucket_name, aws_path, local_path)
    else:
        download_file(s3_client, bucket_name, aws_path, local_path)