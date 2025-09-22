import pytest
import nbimporter
import importlib
import nbformat
from pathlib import Path
import sys

# #読み込むノートブックに一時的に"kernelspec"を書き加える。
# _original_load_module = nbimporter.NotebookLoader.load_module

# def _patched_load_module(self, fullname):

#     #self.path = ["/home/yutaikeda/DG/data_governance/base/task/writing"]
#     print("self.path:", self.path, type(self.path))
#     print(f"Looking for notebook {fullname} in path: {self.path}")
#     path = nbimporter.find_notebook(fullname, self.path)
#     nb = nbformat.read(path, as_version=4)

#     ks = nb.metadata.get('kernelspec', {})
#     language = ks.get('language', '') if isinstance(ks, dict) else ''

#     if 'python' not in language:
#         nb.metadata.kernelspec = {
#             "display_name": "Python 3",
#             "language": "python",
#             "name": "python3"
#         }

#     return _original_load_module(self, fullname)

# # 上書き
# nbimporter.NotebookLoader.load_module = _patched_load_module


# Notebookのクラスを読み込むための関数
@pytest.fixture
def notebook_class():
    def _load(notebook_module: str, class_name: str):
        module = importlib.import_module(notebook_module)
        return getattr(module, class_name)
    return _load