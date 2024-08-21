"""Gakunin RDMとやり取りをするパッケージです。

プロジェクトメタデータをアップロードしたり、APIに接続してプロジェクトメタデータとプロジェクトメンバーの情報を取得するためです
"""

from external import *
from main import *

BASE_URL = 'https://rdm.nii.ac.jp/'

# TODO: BASE_URLに統一したい
SCHEME = 'https'
DOMAIN = 'rdm.nii.ac.jp'

API_V2_BASE_URL = 'https://api.rdm.nii.ac.jp/v2/'
API_DOMAIN = 'api.rdm.nii.ac.jp'
