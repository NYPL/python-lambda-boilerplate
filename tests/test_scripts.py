import unittest
from unittest.mock import patch
import logging
import sys

from scripts.lambdaRun import (
    main,
    deployFunc,
    buildFunc,
    runFunc,
    errFunc,
    runProcess
)
from helpers.errorHelpers import InvalidExecutionType

# Disable logging while we are running tests
logging.disable(logging.CRITICAL)


class TestScripts(unittest.TestCase):

    @patch.object(sys, 'argv', ['make', 'development'])
    @patch('scripts.lambdaRun.deployFunc')
    @patch('os.remove')
    def test_run_main(self, mock_remove, mock_deploy):
        main()
        mock_deploy.assert_called_once_with('development')
        mock_remove.assert_called_once_with('run_config.yaml')

    @patch.object(sys, 'argv', ['make', 'hello', 'jerry'])
    def test_run_surplus_argv(self):
        try:
            main()
        except SystemExit:
            pass
        self.assertRaises(SystemExit)

    @patch.object(sys, 'argv', ['make', 'bad_function'])
    @patch('scripts.lambdaRun.errFunc')
    @patch('os.remove')
    def test_run_bad_function(self, mock_remove, mock_err):
        main()
        mock_err.assert_called_once_with('bad_function')
        mock_remove.assert_called_once_with('run_config.yaml')

    @patch('scripts.lambdaRun.runProcess')
    @patch('scripts.lambdaRun.createEventMapping')
    def test_deploy_function(self, mock_create, mock_run):
        deployFunc('test')
        mock_run.assert_called_once()
        mock_create.assert_called_once_with('test')

    @patch('scripts.lambdaRun.runProcess')
    def test_build_function(self, mock_run):
        buildFunc('test')
        mock_run.assert_called_once_with(
            'test',
            [
                'build',
                '--requirements',
                'requirements.txt',
                '--config-file',
                'run_config.yaml'
            ]
        )

    @patch('scripts.lambdaRun.runProcess')
    def test_run_function(self, mock_run):
        runFunc('test')
        mock_run.assert_called_once_with(
            'local',
            ['invoke', '-v', '--config-file', 'run_config.yaml']
        )

    def test_err_function(self):
        try:
            errFunc('bad_command')
        except InvalidExecutionType:
            pass
        self.assertRaises(InvalidExecutionType)

    @patch('scripts.lambdaRun.setEnvVars')
    @patch('subprocess.run')
    def test_run_process(self, mock_run, mock_envVars):
        runProcess('test', ['run', 'test'])
        mock_envVars.assert_called_once_with('test')
        mock_run.assert_called_once_with(
            ['lambda', 'run', 'test']
        )


if __name__ == '__main__':
    unittest.main()
