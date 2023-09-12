

from ..utils.config import path_config
import os

class MainMenu():
    """MainMenu Class

    FUNCTION:

    1. Display the Research Flow Main Menu
    2. View Research Flow Image
    3. When the initial setup has not been performed, the user is guided to the initial setup.

    NOTE:

    Called from template\\library\\main_menu\\main.py
    """

    @classmethod
    def generate(cls):
        """Generate main menu
        """
        # Get initial setup complete status
        ## ~/.data-governance/setup_completed.txt, if present, complete, if not, not complete
        setup_completed_file_path = os.path.join('../../../..', path_config.SETUP_COMPLETED_TEXT_PATH)
        if os.path.isfile(setup_completed_file_path):
            # Initial setup is complete.
            # Display the main menu
            pass
        else:
            # Initial setup is incomplete.
            # Leads you to the initial setup
            pass
