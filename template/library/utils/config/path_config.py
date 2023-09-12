"""
リサーチフローで利用するパスを一括管理する
"""

import os

# Folder
## 同期対象外フォルダ
DOT_DATA_GOVERNANCE = '.data-governance'
## 同期対象フォルダ
DATA_GOVERNANCE = 'data-governance'


# File

# Path
SETUP_COMPLETED_TEXT_PATH = os.path.join(DOT_DATA_GOVERNANCE, 'setup_completed.txt')