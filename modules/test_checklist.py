# modules/test_checklist.py
import os
import sys

# Add the parent directory to sys.path to allow module imports
parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_path)

import unittest
from unittest.mock import patch
from checklist import process_checklist_command, initialize_checklist_database
import time

class TestProcessChecklistCommand(unittest.TestCase):
    def setUp(self):
        # Always start with a fresh DB
        initialize_checklist_database()
        # Patch settings for consistent test behavior
        patcher1 = patch('modules.checklist.reverse_in_out', False)
        patcher2 = patch('modules.checklist.bbs_ban_list', [])
        patcher3 = patch('modules.checklist.bbs_admin_list', ['999'])
        self.mock_reverse = patcher1.start()
        self.mock_ban = patcher2.start()
        self.mock_admin = patcher3.start()
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        self.addCleanup(patcher3.stop)

    def test_checkin_command(self):
        result = process_checklist_command(1, "checkin test note", name="TESTUSER", location=["loc"])
        self.assertIn("Checked✅In: TESTUSER", result)

    def test_checkout_command(self):
        # First checkin
        process_checklist_command(1, "checkin test note", name="TESTUSER", location=["loc"])
        # Then checkout
        result = process_checklist_command(1, "checkout", name="TESTUSER", location=["loc"])
        self.assertIn("Checked⌛️Out: TESTUSER", result)

    def test_checkin_with_interval(self):
        result = process_checklist_command(1, "checkin 15 hiking", name="TESTUSER", location=["loc"])
        self.assertIn("monitoring every 15min", result)

    def test_checkout_all(self):
        # Multiple checkins
        process_checklist_command(1, "checkin note1", name="TESTUSER", location=["loc"])
        process_checklist_command(1, "checkin note2", name="TESTUSER", location=["loc"])
        result = process_checklist_command(1, "checkout all", name="TESTUSER", location=["loc"])
        self.assertIn("Checked out", result)
        self.assertIn("check-ins for TESTUSER", result)


    def test_checklistapprove_nonadmin(self):
        process_checklist_command(1, "checkin foo", name="FOO", location=["loc"])
        result = process_checklist_command(2, "checklistapprove 1", name="NOTADMIN", location=["loc"])
        self.assertNotIn("approved", result)

    def test_checklistdeny_nonadmin(self):
        process_checklist_command(1, "checkin foo", name="FOO", location=["loc"])
        result = process_checklist_command(2, "checklistdeny 1", name="NOTADMIN", location=["loc"])
        self.assertNotIn("denied", result)

    def test_help_command(self):
        result = process_checklist_command(1, "checklist ?", name="TESTUSER", location=["loc"])
        self.assertIn("Command: checklist", result)

    def test_checklist_listing(self):
        process_checklist_command(1, "checkin foo", name="FOO", location=["loc"])
        result = process_checklist_command(1, "checklist", name="FOO", location=["loc"])
        self.assertIsInstance(result, str)
        self.assertIn("checked-In", result)

    def test_invalid_command(self):
        result = process_checklist_command(1, "foobar", name="FOO", location=["loc"])
        self.assertEqual(result, "Invalid command.")

if __name__ == "__main__":
    unittest.main()