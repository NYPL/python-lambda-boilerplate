import unittest
from unittest.mock import patch, mock_open, call, MagicMock
import json

from helpers.clientHelpers import (
    createAWSClient,
    createEventMapping,
    updateEventMapping
)


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

    @patch(
        'helpers.clientHelpers.loadEnvFile',
        return_value=({'region': 'test'}, None)
    )
    @patch('boto3.client', return_value=True)
    def test_create_with_load_env(self, mock_boto, mock_env):
        result = createAWSClient('fakeService', None)
        mock_env.assert_called_once_with(None, None)
        mock_boto.assert_called_once_with('fakeService', region_name='test')
        self.assertTrue(result)

    @patch('helpers.clientHelpers.createAWSClient')
    @patch(
        'helpers.clientHelpers.loadEnvVars',
        return_value={'function_name': 'tester'}
    )
    def test_create_event_mapping(self, mock_env, mock_client):
        jsonD = ('{"EventSourceMappings": [{"EventSourceArn": "test",'
                 '"Enabled": "test", "BatchSize": "test",'
                 '"StartingPosition": "test"}]}')

        with patch('builtins.open', mock_open(read_data=jsonD), create=True):
            createEventMapping('development')

        mock_env.assert_called_once_with('development')
        mock_client.assert_called_once()
        mock_client().create_event_source_mapping.assert_has_calls([
            call(
                BatchSize='test',
                Enabled='test',
                EventSourceArn='test',
                FunctionName='tester',
                StartingPosition='test'
            )
        ])

    @patch('helpers.clientHelpers.createAWSClient')
    @patch(
        'helpers.clientHelpers.loadEnvVars',
        return_value={'function_name': 'tester'}
    )
    def test_at_lastest_position_event(self, mock_env, mock_client):
        jsonD = ('{"EventSourceMappings": [{"EventSourceArn": "test",'
                 '"Enabled": "test", "BatchSize": "test",'
                 '"StartingPosition": "AT_TIMESTAMP",'
                 ' "StartingPositionTimestamp": "test"}]}')
        with patch('builtins.open', mock_open(read_data=jsonD), create=True):
            createEventMapping('development')

        mock_env.assert_called_once_with('development')
        mock_client.assert_called_once()
        mock_client().create_event_source_mapping.assert_has_calls([
            call(
                BatchSize='test',
                Enabled='test',
                EventSourceArn='test',
                FunctionName='tester',
                StartingPosition='AT_TIMESTAMP',
                StartingPositionTimestamp='test'
            )
        ])

    def test_event_mapping_json_err(self):
        jsonD = ('{"EventSourceMappings": [{"EventSourceArn": "test",'
                 '"Enabled": "test", "BatchSize": "test",'
                 '"StartingPosition": "test"}}')

        with patch('builtins.open', mock_open(read_data=jsonD), create=True):
            try:
                createEventMapping('development')
            except json.decoder.JSONDecodeError:
                pass

        self.assertRaises(json.decoder.JSONDecodeError)

    @patch('builtins.open', side_effect=IOError)
    def test_event_permissions_err(self, mock_file):
        try:
            createEventMapping('development')
        except IOError:
            pass
        self.assertRaises(IOError)

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_event_missing_err(self, mock_file):
        try:
            createEventMapping('development')
        except FileNotFoundError:
            pass
        self.assertRaises(FileNotFoundError)

    @patch('helpers.clientHelpers.loadEnvFile')
    def test_empty_mapping_json_err(self, mock_env):
        jsonD = '{"EventSourceMappings": []}'

        with patch('builtins.open', mock_open(read_data=jsonD), create=True):
            createEventMapping('development')

        mock_env.assert_not_called()

    def test_update_mapping(self):
        mock_client = MagicMock()
        mock_client().list_event_source_mappings.return_value = {
            'EventSourceMappings': [
                {
                    'UUID': 'XXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX',
                }
            ]
        }
        updateEventMapping(
            mock_client,
            {
                'EventSourceArn': 'test:arn:000000000000',
                'Enabled': True,
                'BatchSize': 0
            },
            {
                'function_name': 'test_function'
            }
        )
