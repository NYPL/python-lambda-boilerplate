import unittest
from base64 import b64encode
from botocore.exceptions import ClientError
import os
from yaml import YAMLError
from unittest.mock import patch, mock_open, call

from helpers.configHelpers import (
    loadEnvFile,
    setEnvVars,
    loadEnvVars,
    decryptEnvVar
)


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

    mockReturns = {
        **{},
        **{'environment_variables': {'test': 'world'}}
    }

    @patch('helpers.configHelpers.loadEnvFile', side_effect=[
        {'test1': 'hello', 'test2': 'jerry'},
        {'test2': 'world'}
    ])
    def test_load_env(self, mock_load):
        testDict = loadEnvVars('test')
        self.assertIsInstance(testDict, dict)
        self.assertEqual(testDict['test1'], 'hello')
        self.assertEqual(testDict['test2'], 'world')

    @patch('helpers.configHelpers.loadEnvVars', return_value=mockReturns)
    @patch('builtins.open', new_callable=mock_open, read_data='data')
    def test_envVar_success(self, mock_file, mock_env):
        setEnvVars('development')
        mock_env.assert_has_calls([call('development')])

    mockLoadReturn = {
            **{'environment_variables': {'jerry': 'hello'}},
            **{'environment_variables': {'test': 'world'}}
        }

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

    @patch.dict(
        os.environ,
        {'testing': b64encode('testing'.encode('utf-8')).decode('utf-8')}
    )
    @patch('helpers.configHelpers.boto3')
    def test_env_decryptor_success(self, mock_boto):
        mock_boto.client().decrypt.return_value = {
            'Plaintext': 'testing'.encode('utf-8')
        }
        outEnv = decryptEnvVar('testing')
        self.assertEqual(outEnv, 'testing')

    @patch.dict(os.environ, {'testing': 'testing'})
    @patch('helpers.configHelpers.boto3')
    def test_env_decryptor_non_encoded(self, mock_boto):
        mock_boto.client().decrypt.return_value = {'Plaintext': 'testing'}
        outEnv = decryptEnvVar('testing')
        self.assertEqual(outEnv, 'testing')

    @patch.dict(
        os.environ,
        {'testing': b64encode('testing'.encode('utf-8')).decode('utf-8')}
    )
    @patch('helpers.configHelpers.boto3')
    def test_env_decryptor_boto_error(self, mock_boto):
        mock_boto.client().decrypt.side_effect = ClientError
        outEnv = decryptEnvVar('testing')
        self.assertEqual(
            outEnv,
            b64encode('testing'.encode('utf-8')).decode('utf-8')
        )
