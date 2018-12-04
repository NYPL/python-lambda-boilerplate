import logging
import os

levels = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}


def createLog(module):

    logger = logging.getLogger(module)

    if 'LOG_LEVEL' in os.environ:
        checkLevel = os.environ['LOG_LEVEL'].lower()
    else:
        checkLevel = 'warning'

    consoleLog = logging.StreamHandler()

    if checkLevel in levels:
        logger.setLevel(levels[checkLevel])
        consoleLog.setLevel(levels[checkLevel])
    else:
        logger.setLevel(levels['warning'])
        consoleLog.setLevel(levels['warning'])

    formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s: %(message)s')  # noqa: E501
    consoleLog.setFormatter(formatter)

    logger.addHandler(consoleLog)
    return logger
