import yaml
from collections import ChainMap


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
        ChainMap -- A ChainMap object combining the dictionaries returned from
        the default config.yaml file (required) and an environment-specific
        file (optional). The environment-specific details will override any
        settings in the default file.
    """
    # Load env variables from relevant .yaml file
    envDict = loadEnvFile(runType, 'config/{}.yaml')

    # Overwrite/add any vars in the core config.yaml file
    configDict = loadEnvFile(runType, None)

    combinedConfig = ChainMap(envDict, configDict)

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
                dict(envVars),
                newConfig,
                default_flow_style=False
            )
    except IOError as err:
        logger.error(('Script lacks necessary permissions, '
                      'ensure user has permission to write to directory'))
        raise err
