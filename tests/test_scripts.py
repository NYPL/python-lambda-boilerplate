import unittest
from unittest.mock import patch
import logging
import sys

from scripts.lambdaRun import main
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


if __name__ == '__main__':
    unittest.main()
