from base64 import b64decode
from binascii import Error as base64Error
import boto3
from botocore.exceptions import ClientError
import os
import yaml

from helpers.logHelpers import createLog

logger = createLog('configHelpers')


def loadEnvFile(runType, fileString):
    """Loads configuration details from a specific yaml file.

    Arguments:
        runType {string} -- The environment to load configuration details for.
        fileString {string} -- The file string format indicating where to load
        the configuration file from.

    Raises:
        YAMLError: Indicates malformed yaml markup in the configuration file

    Returns:
        dict -- A dictionary containing the configuration details parsed from
        the specificied yaml file.
    """
    envDict = None

    if fileString:
        openFile = fileString.format(runType)
    else:
        openFile = 'config.yaml'

    try:
        with open(openFile) as envStream:
            try:
                envDict = yaml.full_load(envStream)
            except yaml.YAMLError as err:
                logger.error('{} Invalid! Please review'.format(openFile))
                raise err

    except FileNotFoundError as err:
        logger.info('Missing config YAML file! Check directory')
        logger.debug(err)

    if envDict is None:
        return {}

    return envDict


def loadEnvVars(runType):
    """Loads a full set of configuration details from the both the default
    configuration file and any environment specific settings.

    Arguments:
        runType {string} -- The current environment.

    Returns:
        dict -- A dictionary combining the values from the default config.yaml
        file (required) and an environment-specific file (optional). The
        environment-specific details will override any settings in the default
        file.
    """
    # Load base config settings/variables from the root config.yaml file
    baseConfigDict = loadEnvFile(runType, None)

    # Load additional settings from env-specific file. These will overwrite
    # any matching settings/variables from the config.yaml file
    currentEnvDict = loadEnvFile(runType, 'config/{}.yaml')

    # Merge the loaded dicts, overwriting any matching settings with the values
    # from the env-specific file.
    combinedConfig = {**baseConfigDict, **currentEnvDict}

    return combinedConfig


def setEnvVars(runType):
    """Produces a yaml file that can be read by the Lambda deployment process
    from the combined arguments from loadEnvVars

    Arguments:
        runType {string} -- The current environment.

    Raises:
        IOError: Raised when the method is unable to produce a yaml file due
        to file/directory permission issues.
    """
    envVars = loadEnvVars(runType)

    try:
        with open('run_config.yaml', 'w') as newConfig:
            yaml.dump(
                envVars,
                newConfig,
                default_flow_style=False
            )
    except IOError as err:
        logger.error(('Script lacks necessary permissions, '
                      'ensure user has permission to write to directory'))
        raise err


def decryptEnvVar(envVar):
    """This helper method takes a KMS encoded environment variable and decrypts
    it into a usable value. Sensitive variables should be so encoded so that
    they can be stored in git and used in a CI/CD environment.

    Arguments:
        envVar {string} -- a string, either plaintext or a base64, encrypted
        value
    """
    encrypted = os.environ.get(envVar, None)

    try:
        decoded = b64decode(encrypted)
        # If region is not set, assume us-east-1
        regionName = os.environ.get('AWS_REGION', 'us-east-1')
        return boto3.client('kms', region_name=regionName)\
            .decrypt(CiphertextBlob=decoded)['Plaintext'].decode('utf-8')
    except (ClientError, base64Error, TypeError):
        return encrypted
