import unittest
import os
import sys
import tempfile
import shutil
import atexit

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Create a temporary directory for testing so test state doesn't intermix with production
original_cwd = os.getcwd()
test_dir = tempfile.mkdtemp()
os.chdir(test_dir)
os.makedirs('data', exist_ok=True)
os.makedirs('logs', exist_ok=True)

def cleanup():
    os.chdir(original_cwd)
    shutil.rmtree(test_dir)

atexit.register(cleanup)

from modules import bbstools
from modules.bbstools import *

# Mock the bbs_ban_list and bbs_admin_list
bbs_ban_list = []
bbs_admin_list = ['1234567890']

class TestBbstools(unittest.TestCase):
    def setUp(self):
        bbstools.bbs_messages.clear()
        bbstools.bbs_dm.clear()

        bbstools.bbs_messages.extend([
            [1, "Test Subject 1", "Test Message 1", 12345],
            [2, "Test Subject 2", "Test Message 2", 67890]
        ])
        bbstools.bbs_dm.extend([
            [12345, "Test DM 1", 67890],
            [67890, "Test DM 2", 12345]
        ])
        save_bbsdb()
        save_bbsdm()

    def test_bbs_help(self):
        self.assertEqual(bbs_help(), "BBS Commands:\n'bbslist'\n'bbspost message...'\n'bbspost $subject #message'\n'bbsread #'\n'bbsdelete #'")

    def test_bbs_list_messages(self):
        self.assertEqual(bbs_list_messages(), "Msg #1 Test Subject 1\nMsg #2 Test Subject 2")

    def test_bbs_post_message(self):
        bbs_post_message("New Subject", "New Message", 54321)
        self.assertEqual(len(bbstools.bbs_messages), 3)
        self.assertEqual(bbstools.bbs_messages[2][1], "New Subject")

    def test_bbs_read_message(self):
        self.assertEqual(bbs_read_message(1), "Msg #1\nMsg Body: Test Message 1")
        self.assertEqual(bbs_read_message(3), "Message not found.")

    def test_bbs_delete_message(self):
        bbs_delete_message(1, 12345)
        self.assertEqual(len(bbstools.bbs_messages), 1)
        self.assertEqual(bbs_delete_message(1, 99999), "You are not authorized to delete this message.")

    def test_bbs_automatic_subject_from_body(self):
        body = "This is a long message body that should be truncated to a shorter subject."
        self.assertEqual(bbs_automatic_subject_from_body(body), "This is a long message bo...")
        body = "Short body"
        self.assertEqual(bbs_automatic_subject_from_body(body), "Short body")

    def test_bbs_post_dm(self):
        bbs_post_dm(98765, "New DM", 54321)
        self.assertEqual(len(bbstools.bbs_dm), 3)
        self.assertEqual(bbstools.bbs_dm[2][1], "New DM")

    def test_get_bbs_stats(self):
        self.assertEqual(get_bbs_stats(), "📡BBSdb has 2 messages.\nDirect ✉️ Messages waiting: 1")

    def test_bbs_check_dm(self):
        self.assertEqual(bbs_check_dm(12345), [12345, "Test DM 1", 67890])
        self.assertFalse(bbs_check_dm(99999))

    def test_bbs_delete_dm(self):
        bbs_delete_dm(12345, "Test DM 1")
        self.assertEqual(len(bbstools.bbs_dm), 1)
        self.assertEqual(bbs_delete_dm(99999, "Test DM 1"), "System: No DM found for node 99999")

    def test_save_and_load_bbsdb(self):
        # Modify the data
        bbstools.bbs_messages.append([3, "New Message", "New Body", 123])
        save_bbsdb()

        # Clear the current messages and reload
        load_bbsdb()

        self.assertEqual(len(bbstools.bbs_messages), 3)
        self.assertEqual(bbstools.bbs_messages[2][1], "New Message")

        # Test loading a non-existent file
        if os.path.exists('data/bbsdb.pkl'):
            os.remove('data/bbsdb.pkl')
        load_bbsdb()
        self.assertEqual(len(bbstools.bbs_messages), 1)
        self.assertEqual(bbstools.bbs_messages[0][1], "Welcome to meshBBS")

    def test_save_and_load_bbsdm(self):
        # Modify the data
        bbstools.bbs_dm.append([3, "New DM", 123])
        save_bbsdm()

        # Clear the current messages and reload
        load_bbsdm()

        self.assertEqual(len(bbstools.bbs_dm), 3)
        self.assertEqual(bbstools.bbs_dm[2][1], "New DM")

        # Test loading a non-existent file
        if os.path.exists('data/bbsdm.pkl'):
            os.remove('data/bbsdm.pkl')
        load_bbsdm()
        self.assertEqual(len(bbstools.bbs_dm), 1)
        self.assertEqual(bbstools.bbs_dm[0][1], "Message")

    def test_bbsdb_disk_format(self):
        save_bbsdb()
        with open('data/bbsdb.pkl', 'rb') as f:
            serialized_messages = pickle.load(f)
            self.assertEqual(len(serialized_messages), 2)
            self.assertEqual(serialized_messages[0], [1, "Test Subject 1", "Test Message 1", 12345])

    def test_bbsdm_disk_format(self):
        save_bbsdm()
        with open('data/bbsdm.pkl', 'rb') as f:
            serialized_dms = pickle.load(f)
            self.assertEqual(len(serialized_dms), 2)
            self.assertEqual(serialized_dms[0], [12345, "Test DM 1", 67890])

if __name__ == '__main__':
    unittest.main()
