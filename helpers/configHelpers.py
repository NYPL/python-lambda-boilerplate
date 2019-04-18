import yaml
from collections import ChainMap


from helpers.logHelpers import createLog

logger = createLog('configHelpers')


def loadEnvFile(runType, fileString):

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
    # Load env variables from relevant .yaml file
    envDict = loadEnvFile(runType, 'config/{}.yaml')

    # Overwrite/add any vars in the core config.yaml file
    configDict = loadEnvFile(runType, None)

    combinedConfig = ChainMap(envDict, configDict)

    return combinedConfig


def setEnvVars(runType):

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