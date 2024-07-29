"""このパッケージはmain.pyとapi.pyファイルの関数をimportします。
    main.py
        get_project_id:プロジェクトIDを取得する関数です。
        check_authorization:URLの権限のチェックをする関数です。
        check_permission:アクセス許可のチェックを行う関数です。
        get_projects_list:プロジェクトの一覧を取得する関数です。
        sync:GRDMにアップロードする関数です。
        download_text_file:テキストファイルの中身を取得する関数です。
        download_json_file:jsonファイルの中身を取得する関数です。
        get_project_metadata:プロジェクトメタデータを取得する関数です。
        get_collaborator_list:共同管理者の取得する関数です。
        build_collaborator_url:プロジェクトのメンバー一覧のURLを返す関数です。
    api.py
        build_api_url:API用のURLを作成する関数です。
        build_oauth_url:OAuthのAPI用のURLを作成する関数です。
        get_token_profile:トークンプロファイルを取得する関数です。
        get_user_info:tokenで指定したユーザーの情報を取得する関数です。
        get_projects:プロジェクトの情報を取得する関数です。
        get_project_registrations:プロジェクトメタデータを取得する関数です。
        get_project_collaborators:プロジェクトメンバーの情報を取得する関数です。

 """
from .main import *
from .api import *

BASE_URL = 'https://rdm.nii.ac.jp/'

# TODO: BASE_URLに統一したい
SCHEME = 'https'
DOMAIN = 'rdm.nii.ac.jp'

API_V2_BASE_URL = 'https://api.rdm.nii.ac.jp/v2/'
API_DOMAIN = 'api.rdm.nii.ac.jp'
