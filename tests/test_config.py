import unittest
from yaml import YAMLError
from unittest.mock import patch

from helpers.configHelpers import loadEnvFile


class TestConfig(unittest.TestCase):

    @patch('yaml.load', return_value={'testing': True})
    def test_load_env_success(self, mock_yaml):
        resDict, resLines = loadEnvFile('development', None)
        self.assertTrue(resDict['testing'])

    @patch('yaml.load', return_value={'testing': True})
    def test_load_env_config_success(self, mock_yaml):
        resDict, resLines = loadEnvFile('development', 'config/{}.yaml')
        self.assertTrue(resDict['testing'])

    @patch('yaml.load', side_effect={'testing': True})
    def test_load_env_failure(self, mock_yaml):
        try:
            resDict, resLines = loadEnvFile('development', 'missing/{}.yaml')
        except FileNotFoundError:
            pass
        self.assertRaises(FileNotFoundError)

    @patch('yaml.load', return_value=None)
    def test_load_empty_env(self, mock_yaml):
        resDict, resLines = loadEnvFile('development', None)
        self.assertEqual(resDict, {})

    @patch('yaml.load', side_effect=YAMLError)
    def test_read_env_failure(self, mock_yaml):
        try:
            resDict, resLines = loadEnvFile('development', 'config/{}.yaml')
        except YAMLError:
            pass
        self.assertRaises(YAMLError)
