from helpers.errorHelpers import NoRecordsRecieved
from helpers.logHelpers import createLog

# Logger can be passed name of current module
# Can also be instantiated on a class/method basis using dot notation
logger = createLog('handler')


def handler(event, context):

    logger.debug('Starting Lambda Execution')

    records = event.get('Records')

    if records is None:
        logger.error('Records block is missing in Kinesis Event')
        raise NoRecordsRecieved('Records block missing', event)
    elif len(records) < 1:
        logger.error('Records block contains no records')
        raise NoRecordsRecieved('Records block empty', event)

    # Method to be invoked goes here
    # TODO Implement oauth checking
    logger.info('Successfully invoked lambda')

    # This return will be reflected in the CloudWatch logs
    # but doesn't actually do anything
    return 'Hello, World'
