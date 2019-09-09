from helpers.logHelpers import createLog

# Logger can be passed name of current module
# Can also be instantiated on a class/method basis using dot notation
logger = createLog('handler')


def handler(event, context):
    """The central handler function called when the Lambda function is invoked.

    Arguments:
        event {dict} -- Dictionary containing contents of the event that
        invoked the function, primarily the payload of data to be processed.
        context {LambdaContext} -- An object containing metadata describing
        the event source and client details.

    Returns:
        [string|dict] -- An output object that does not impact the effect of
        the function but which is reflected in CloudWatch
    """
    logger.info('Starting Lambda Execution')

    logger.debug(event)

    # Method to be invoked goes here
    logger.info('Successfully invoked lambda')

    # This return will be reflected in the CloudWatch logs
    # but doesn't actually do anything
    return 'Hello, World'
