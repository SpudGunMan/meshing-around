import unittest
from unittest import mock
from modules.bbstools import *

class TestBBSListMessages(unittest.TestCase):
    def test_bbs_list_messages(self):
        # Mock the bbs_messages list
        bbs_messages = [[1, "Welcome to meshBBS", "Welcome to the BBS, please post a message!",0],
                        [2, "Test Message 1", "This is a test message 1",0],
                        [3, "Test Message 2", "This is a test message 2",0]]
        
        # Mock the return value of bbs_messages
        with mock.patch('bbstools.bbs_messages', bbs_messages):
            expected_output = "Msg #1 Welcome to meshBBS\nMsg #2 Test Message 1\nMsg #3 Test Message 2"
            self.assertEqual(bbs_list_messages(), expected_output)

    def test_bbs_post_message(self):
        subject = "Test Subject"
        message = "Test Message"
        
        
        with mock.patch('bbstools.bbs_messages', [[1, "Welcome to meshBBS", "Welcome to the BBS, please post a message!"]]):
            result = bbs_post_message(subject, message)
        
            expected_output = "Message posted. ID is: 2"  # Assuming there is already one message in the list
            self.assertEqual(result, expected_output)
            
            expected_output = "Msg #1 Welcome to meshBBS\nMsg #2 Test Subject"  # Assuming there is already one message in the list
            self.assertEqual(bbs_list_messages(), expected_output)

    def test_bbs_delete_message(self):
        # Mock the bbs_messages list
        bbs_messages = [[1, "Welcome to meshBBS", "Welcome to the BBS, please post a message!",0],
                        [2, "Test Message 1", "This is a test message 1",0],
                        [3, "Test Message 2", "This is a test message 2",0]]
        
        # Mock the return value of bbs_messages
        with mock.patch('bbstools.bbs_messages', bbs_messages):
            result = bbs_delete_message(2)        
            expected_output = "Msg #2 deleted."
            self.assertEqual(result, expected_output)
            expected_output = "Msg #1 Welcome to meshBBS\nMsg #2 Test Message 2"
            self.assertEqual(bbs_list_messages(), expected_output)

if __name__ == '__main__':
    unittest.main()