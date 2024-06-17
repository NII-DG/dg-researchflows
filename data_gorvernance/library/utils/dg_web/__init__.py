from .form import Form
from .runcrate_form import RunCrateForm
from .api import (
    get_govsheet_schema,
    get_metadata_schema
)

SCHEME = 'http'
DOMAIN = 'dg02.dg.rcos.nii.ac.jp'


GOVSHEET_PATH = '.dg/gov-sheet.json'
METADATA_PATH = '.dg/metadata.json'

# governed run
GOVRUN_INDEX_PATH = '.crates/index.json'