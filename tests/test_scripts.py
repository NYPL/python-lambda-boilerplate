import unittest
from unittest.mock import patch, mock_open, call, MagicMock
import logging
import json
import sys
from collections import ChainMap

from scripts.lambdaRun import (
    main,
    setEnvVars,
    loadEnvVars,
    createEventMapping,
    updateEventMapping
)
from helpers.errorHelpers import InvalidExecutionType

# Disable logging while we are running tests
logging.disable(logging.CRITICAL)


class TestScripts(unittest.TestCase):

    @patch.object(sys, 'argv', ['make', 'development'])
    @patch('scripts.lambdaRun.setEnvVars')
    @patch('scripts.lambdaRun.createEventMapping')
    @patch('subprocess.run')
    @patch('os.remove')
    def test_run_deploy(self, mock_rm, mock_run, mock_env, mock_envVars):
        main()
        mock_envVars.assert_called_once()
        mock_env.assert_called_once()
        mock_run.assert_called_once()
        mock_rm.assert_called_once()

    @patch.object(sys, 'argv', ['make', 'run-local'])
    @patch('scripts.lambdaRun.setEnvVars')
    @patch('subprocess.run')
    @patch('os.remove')
    def test_run_local(self, mock_rm, mock_run, mock_envVars):
        main()
        mock_envVars.assert_called_once_with('local')
        mock_run.assert_called_once()
        mock_rm.assert_called_once_with('run_config.yaml')

    @patch.object(sys, 'argv', ['make', 'build-development'])
    @patch('scripts.lambdaRun.setEnvVars')
    @patch('subprocess.run')
    @patch('os.remove')
    def test_run_build(self, mock_rm, mock_run, mock_envVars):
        main()
        mock_envVars.assert_called_once_with('development')
        mock_run.assert_called_once()
        mock_rm.assert_called_once_with('run_config.yaml')

    @patch.object(sys, 'argv', ['make', 'bad-command'])
    def test_run_invalid(self):
        try:
            main()
        except InvalidExecutionType:
            pass
        self.assertRaises(InvalidExecutionType)

    @patch.object(sys, 'argv', ['make', 'hello', 'jerry'])
    def test_run_surplus_argv(self):
        try:
            main()
        except SystemExit:
            pass
        self.assertRaises(SystemExit)

    mockReturns = ChainMap(
        {
            'environment_variables': {
                'test': 'world'
            }
        },
        {}
    )

    @patch('scripts.lambdaRun.loadEnvFile', side_effect=[
        {'test1': 'hello'},
        {'test2': 'world'}
    ])
    def test_load_env(self, mock_load):
        testChain = loadEnvVars('test')
        self.assertIsInstance(testChain, ChainMap)
        self.assertEqual(testChain['test1'], 'hello')

    @patch('scripts.lambdaRun.loadEnvVars', return_value=mockReturns)
    @patch('builtins.open', new_callable=mock_open, read_data='data')
    def test_envVar_success(self, mock_file, mock_env):
        setEnvVars('development')
        mock_env.assert_has_calls([call('development')])

    mockLoadReturn = ChainMap({
            'environment_variables': {
                'test': 'world'
            }
        },{
            'environment_variables': {
                'jerry': 'hello'
            }
        })

    @patch('scripts.lambdaRun.loadEnvVars', return_value=mockLoadReturn)
    def test_envVar_parsing(self, mock_env):
        m = mock_open()
        with patch('builtins.open', m, create=True):
            setEnvVars('development')
            mock_env.assert_called_once()
            confHandle = m()
            confHandle.write.assert_called()

    @patch('scripts.lambdaRun.loadEnvVars', return_value=mockLoadReturn)
    @patch('builtins.open', side_effect=IOError())
    def test_envVar_permissions(self, mock_file, mock_env):
        try:
            setEnvVars('development')
        except IOError:
            pass
        self.assertRaises(IOError)

    mockReturns = ChainMap(
        {
            'function_name': 'tester',
            'environment_variables': {
                'jerry': 'hello'
            }
        },
        {}
    )

    @patch('scripts.lambdaRun.createAWSClient')
    @patch('scripts.lambdaRun.loadEnvVars', return_value={'function_name': 'tester'})
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

    @patch('scripts.lambdaRun.createAWSClient')
    @patch('scripts.lambdaRun.loadEnvVars', return_value={'function_name': 'tester'})
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

    @patch('scripts.lambdaRun.loadEnvFile')
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


if __name__ == '__main__':
    unittest.main()
