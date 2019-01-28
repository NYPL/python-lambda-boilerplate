import unittest
from unittest.mock import patch

from helpers.clientHelpers import createAWSClient


class TestClient(unittest.TestCase):

    @patch('boto3.client', return_value=True)
    def test_create_client(self, mock_boto):
        result = createAWSClient('fakeService', {
            'region': 'test'
        })
        mock_boto.assert_called_once_with('fakeService', region_name='test')
        self.assertTrue(result)

    @patch('boto3.client', return_value=True)
    def test_create_with_access(self, mock_boto):
        result = createAWSClient('fakeService', {
            'region': 'test',
            'aws_access_key_id': 1,
            'aws_secret_access_key': 'secret'
        })
        mock_boto.assert_called_once_with(
            'fakeService',
            region_name='test',
            aws_access_key_id=1,
            aws_secret_access_key='secret'
        )
        self.assertTrue(result)

    @patch('helpers.clientHelpers.loadEnvFile', return_value=({'region': 'test'}, None))  # noqa E501
    @patch('boto3.client', return_value=True)
    def test_create_with_load_env(self, mock_boto, mock_env):
        result = createAWSClient('fakeService', None)
        mock_env.assert_called_once_with(None, None)
        mock_boto.assert_called_once_with('fakeService', region_name='test')
        self.assertTrue(result)
