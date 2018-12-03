import unittest

from service import handler
from helpers.errorHelpers import NoRecordsReceived


class TestHandler(unittest.TestCase):

    def test_handler_clean(self):
        testRec = {
            'source': 'Kinesis',
            'Records': [
                {
                    'kinesis': {
                        'data': 'data'
                    }
                }
            ]
        }
        resp = handler(testRec, None)
        self.assertEqual(resp, 'Hello, World')

    def test_handler_error(self):
        testRec = {
            'source': 'Kinesis',
            'Records': []
        }
        try:
            handler(testRec, None)
        except NoRecordsReceived:
            pass
        self.assertRaises(NoRecordsReceived)

    def test_records_none(self):
        testRec = {
            'source': 'Kinesis'
        }
        try:
            handler(testRec, None)
        except NoRecordsReceived:
            pass
        self.assertRaises(NoRecordsReceived)


if __name__ == '__main__':
    unittest.main()
