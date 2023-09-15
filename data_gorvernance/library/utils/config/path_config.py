"""
リサーチフローで利用するパスを一括管理する
"""

import os
# Folder
## 同期対象外フォルダ
DOT_DATA_GOVERNANCE = '.data_gorvernance'
## 同期対象フォルダ
DATA_GOVERNANCE = 'data_gorvernance'


# File

# Path
SETUP_COMPLETED_TEXT_PATH = os.path.join(DOT_DATA_GOVERNANCE, 'setup_completed.txt')


def getResearchFlowStatusFilePath(abs_root)->str:
    return os.path.join(abs_root, DATA_GOVERNANCE, 'researchflow/research_flow_status.json')