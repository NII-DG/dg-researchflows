from unittest import TestCase

from data_gorvernance.library.utils.config import message

class TestMessageConfig(TestCase):
    # test exec : python -m unittest tests.utils.config.test_message

    def test_get(self):
        research_preparation = message.get('research_flow_phase_display_name', 'plan')
        self.assertEqual('研究準備', research_preparation)
