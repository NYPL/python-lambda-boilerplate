import yaml

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
                envDict = yaml.load(envStream)
            except yaml.YAMLError as err:
                logger.error('{} Invalid! Please review'.format(openFile))
                raise err

    except FileNotFoundError as err:
        logger.info('Missing config YAML file! Check directory')
        logger.debug(err)

    if envDict is None:
        return {}
    
    return envDict
