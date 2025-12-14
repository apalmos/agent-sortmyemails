import sys
import os
import unittest
from unittest.mock import MagicMock
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../agent-sortmyemails')))

from helper_scripts.gmail_labels import create_filter_for_sender

class TestGmailUtils(unittest.TestCase):
    def test_create_filter_for_sender(self):
        mock_service = MagicMock()
        mock_users = mock_service.users.return_value
        mock_settings = mock_users.settings.return_value
        mock_filters = mock_settings.filters.return_value
        mock_create = mock_filters.create.return_value
        mock_execute = mock_create.execute.return_value
        
        create_filter_for_sender(mock_service, "test@example.com", "LabelID123")
        
        # Verify call arguments
        mock_filters.create.assert_called_once()
        args, kwargs = mock_filters.create.call_args
        body = kwargs['body']
        
        self.assertEqual(body['criteria']['from'], "test@example.com")
        self.assertEqual(body['action']['addLabelIds'], ["LabelID123"])
        self.assertEqual(body['action']['removeLabelIds'], ["INBOX"])

if __name__ == '__main__':
    unittest.main()
