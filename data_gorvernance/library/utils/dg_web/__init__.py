from .form import Form
from .runcrate_form import RunCrateForm
from .api import (
    get_govsheet_schema,
    get_metadata_schema,
    get_validations,
    get_validations_validationId
)

SCHEME = 'http'
DOMAIN = 'dg02.dg.rcos.nii.ac.jp'


GOVSHEET_PATH = '.dg/gov-sheet.json'
METADATA_PATH = '.dg/metadata.json'