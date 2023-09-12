from unittest import TestCase
from template.library.utils.config import message
import os

class MessageConfig(TestCase):
    # test exec : python -m unittest tests.utils.config.test_message

    def test_get(self):
        research_preparation = message.get('research_flow_phase_display_name', 'research_preparation')
        self.assertEqual('研究準備', research_preparation)