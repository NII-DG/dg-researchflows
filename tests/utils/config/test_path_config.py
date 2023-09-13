from unittest import TestCase
from template.library.utils.config import path_config
import os

class TestPathConfig(TestCase):
    # test exec : python -m unittest tests.utils.config.test_path_config

    def test_root(self):
        self.assertEqual(os.getcwd(), path_config.ROOT)
