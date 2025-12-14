import sys
import os
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../agent-sortmyemails')))

from helper_scripts.categorize import parse_categorization_output

class TestCategorization(unittest.TestCase):
    def test_parse_categorization_output(self):
        output = """
Category: Work
Description: Job related stuff
Emails: 1, 2, 5

Category: Personal
Description: Friends and family
Emails: 3, 4
"""
        expected = {
            "Work": [0, 1, 4],  # 0-indexed
            "Personal": [2, 3]  # 0-indexed
        }
        
        result = parse_categorization_output(output)
        self.assertEqual(result, expected)

    def test_parse_empty(self):
        output = ""
        result = parse_categorization_output(output)
        self.assertEqual(result, {})

if __name__ == '__main__':
    unittest.main()
