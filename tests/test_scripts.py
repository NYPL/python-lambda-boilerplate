import unittest
from unittest.mock import patch, mock_open, call
import os
from yaml import YAMLError
from botocore.stub import Stubber

from scripts.lambdaRun import main, setEnvVars, createEventMapping, loadEnvFile
from helpers.errorHelpers import InvalidExecutionType

class TestScripts(unittest.TestCase):

    @patch('scripts.lambdaRun.setEnvVars')
    @patch('scripts.lambdaRun.createEventMapping')
    @patch('subprocess.run')
    @patch('os.remove')
    def test_run_deploy(self, mock_rm, mock_run, mock_envMapping, mock_envVars):
        main('development')
        mock_envVars.assert_called_once()
        mock_envMapping.assert_called_once()
        mock_run.assert_called_once()
        mock_rm.assert_called_once()

    @patch('scripts.lambdaRun.setEnvVars')
    @patch('subprocess.run')
    @patch('os.remove')
    def test_run_local(self, mock_rm, mock_run, mock_envVars):
        main('run-local')
        mock_envVars.assert_called_once_with('development')
        mock_run.assert_called_once()
        mock_rm.assert_called_once_with('run_config.yaml')

    @patch('scripts.lambdaRun.setEnvVars')
    @patch('subprocess.run')
    @patch('os.remove')
    def test_run_build(self, mock_rm, mock_run, mock_envVars):
        main('build-development')
        mock_envVars.assert_called_once_with('development')
        mock_run.assert_called_once()
        mock_rm.assert_called_once_with('run_config.yaml')

    def test_run_invalid(self):
        try:
            main('bad-command')
        except InvalidExecutionType:
            pass
        self.assertRaises(InvalidExecutionType)


    mockReturns = [
        {
            'environment_variables': {
                'test': 'world'
            }
        }, {
            'environment_variables': {
                'test': 'hello',
                'static': 'static'
            }
        }
    ]
    @patch('scripts.lambdaRun.loadEnvFile', side_effect=mockReturns)
    @patch('builtins.open', new_callable=mock_open, read_data='data')
    def test_envVar_success(self, mock_file, mock_env):
        setEnvVars('development')
        envCalls = [
            call('development', 'config/{}.yaml'),
            call('development', None)
        ]
        mock_env.assert_has_calls(envCalls)

    @patch('scripts.lambdaRun.loadEnvFile', return_value={})
    @patch('shutil.copyfile')
    def test_missing_block(self, mock_copy, mock_env):
        setEnvVars('development')
        mock_env.assert_called_once()
        mock_copy.assert_called_once_with('config.yaml', 'run_config.yaml')

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
            resDict = loadEnvFile('development', 'missing/{}.yaml')
        except FileNotFoundError:
            pass
        self.assertRaises(FileNotFoundError)

    @patch('yaml.load', side_effect=YAMLError)
    def test_read_env_failure(self, mock_yaml):
        try:
            resDict = loadEnvFile('development', 'config/{}.yaml')
        except YAMLError:
            pass
        self.assertRaises(YAMLError)


if __name__ == '__main__':
    unittest.main()
