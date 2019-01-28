import boto3

from helpers.logHelpers import createLog
from helpers.configHelpers import loadEnvFile

logger = createLog('clientHelpers')


def createAWSClient(service, configDict=None):

    if configDict is None:
        configDict, configLines = loadEnvFile(None, None)

    clientKwargs = {
        'region_name': configDict['region']
    }

    if (
        'aws_access_key_id' in configDict
        and
        configDict['aws_access_key_id'] is not None
    ):
        clientKwargs['aws_access_key_id'] = configDict['aws_access_key_id']
        clientKwargs['aws_secret_access_key'] = configDict['aws_secret_access_key']  # noqa: E501

    lambdaClient = boto3.client(
        service,
        **clientKwargs
    )

    return lambdaClient
