from unittest import TestCase
from data_gorvernance.library.utils.nb_file import NbFile
import os
from pathlib import Path
import uuid
import shutil

abs_script_dir_path = os.path.dirname(os.path.abspath(__file__))


class TestNbFile(TestCase):
    # test exec : python -m unittest tests.utils.nb_file

    def test_embed_subflow_name_on_header(self):
        path = Path(abs_script_dir_path)
        nb_file_path = path.joinpath('..', 'test_data/embed_subflow_name_on_header.ipynb').resolve()

        id = uuid.uuid4()
        dect_path = path.joinpath('..', f'test_data/embed_subflow_name_on_header_{id}.ipynb').resolve()

        shutil.copy(nb_file_path, dect_path)



        nb_file = NbFile(str(dect_path))

        sub_flow_name = 'test A'
        nb_file.embed_subflow_name_on_header(sub_flow_name)

        notebook = nb_file.read()
        os.remove(dect_path)

        self.assertEqual('markdown', notebook.cells[0].cell_type)
        self.assertTrue('test A' in notebook.cells[0].source)
        self.assertEqual('code', notebook.cells[1].cell_type)
        self.assertFalse('test A' in notebook.cells[1].source)
