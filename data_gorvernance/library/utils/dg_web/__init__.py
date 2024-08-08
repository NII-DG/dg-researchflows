""" dg-webと接続するためのパッケージです。"""
from .dgform import *
from .dgweb import *

SCHEME = 'http'
DOMAIN = 'dg02.dg.rcos.nii.ac.jp'


GOVSHEET_PATH = '.dg/gov-sheet.json'
METADATA_PATH = '.dg/metadata.json'

# governed run
GOVRUN_INDEX_PATH = '.crates/index.json'