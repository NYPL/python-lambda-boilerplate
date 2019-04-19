import unittest
from yaml import YAMLError
from unittest.mock import patch, mock_open, call
from collections import ChainMap

from helpers.configHelpers import loadEnvFile, setEnvVars, loadEnvVars


class TestConfig(unittest.TestCase):

    @patch('yaml.load', return_value={'testing': True})
    def test_load_env_success(self, mock_yaml):
        resDict = loadEnvFile('development', None)
        self.assertTrue(resDict['testing'])

    @patch('yaml.load', return_value={'testing': True})
    def test_load_env_config_success(self, mock_yaml):
        resDict = loadEnvFile('development', 'config/{}.yaml')
        self.assertTrue(resDict['testing'])

    @patch('yaml.load', side_effect={'testing': True})
    def test_load_env_failure(self, mock_yaml):
        try:
            loadEnvFile('development', 'missing/{}.yaml')
        except FileNotFoundError:
            pass
        self.assertRaises(FileNotFoundError)

    @patch('yaml.load', return_value=None)
    def test_load_empty_env(self, mock_yaml):
        resDict = loadEnvFile('development', None)
        self.assertEqual(resDict, {})

    @patch('yaml.load', side_effect=YAMLError)
    def test_read_env_failure(self, mock_yaml):
        try:
            loadEnvFile('development', 'config/{}.yaml')
        except YAMLError:
            pass
        self.assertRaises(YAMLError)

    mockReturns = ChainMap(
        {
            'environment_variables': {
                'test': 'world'
            }
        },
        {}
    )

    @patch('helpers.configHelpers.loadEnvFile', side_effect=[
        {'test1': 'hello'},
        {'test2': 'world'}
    ])
    def test_load_env(self, mock_load):
        testChain = loadEnvVars('test')
        self.assertIsInstance(testChain, ChainMap)
        self.assertEqual(testChain['test1'], 'hello')

    @patch('helpers.configHelpers.loadEnvVars', return_value=mockReturns)
    @patch('builtins.open', new_callable=mock_open, read_data='data')
    def test_envVar_success(self, mock_file, mock_env):
        setEnvVars('development')
        mock_env.assert_has_calls([call('development')])

    mockLoadReturn = ChainMap({
            'environment_variables': {
                'test': 'world'
            }
        }, {
            'environment_variables': {
                'jerry': 'hello'
            }
        })

    @patch('helpers.configHelpers.loadEnvVars', return_value=mockLoadReturn)
    def test_envVar_parsing(self, mock_env):
        m = mock_open()
        with patch('builtins.open', m, create=True):
            setEnvVars('development')
            mock_env.assert_called_once()
            confHandle = m()
            confHandle.write.assert_called()

    @patch('helpers.configHelpers.loadEnvVars', return_value=mockLoadReturn)
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
