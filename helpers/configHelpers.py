import yaml

from helpers.logHelpers import createLog


logger = createLog('configHelpers')


def loadEnvFile(runType, fileString):

    envDict = None
    fileLines = []

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

            envStream.seek(0)
            fileLines = envStream.readlines()

    except FileNotFoundError as err:
        logger.info('Missing config YAML file! Check directory')
        logger.debug(err)

    if envDict is None:
        envDict = {}
    return envDict, fileLines
