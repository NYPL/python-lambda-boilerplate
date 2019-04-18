import json
import boto3

from helpers.logHelpers import createLog
from helpers.configHelpers import loadEnvVars, loadEnvFile

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


def createEventMapping(runType):
    logger.info('Creating event Source mappings for Lambda')
    try:
        with open('config/event_sources_{}.json'.format(runType)) as sources:
            try:
                eventMappings = json.load(sources)
            except json.decoder.JSONDecodeError as err:
                logger.error('Unable to parse JSON file')
                raise err
    except FileNotFoundError:
        logger.info('No Event Source mapping provided')
        return
    except IOError as err:
        logger.error('Unable to open JSON file')
        raise err

    if len(eventMappings['EventSourceMappings']) < 1:
        logger.info('No event sources defined')
        return

    configDict = loadEnvVars(runType)

    lambdaClient = createAWSClient('lambda', configDict)

    for mapping in eventMappings['EventSourceMappings']:
        logger.debug('Adding event source mapping for function')

        createKwargs = {
            'EventSourceArn': mapping['EventSourceArn'],
            'FunctionName': configDict['function_name'],
            'Enabled': mapping['Enabled'],
            'BatchSize': mapping['BatchSize'],
        }

        if 'StartingPosition' in mapping:
            createKwargs['StartingPosition'] = mapping['StartingPosition']
            if mapping['StartingPosition'] == 'AT_TIMESTAMP':
                createKwargs['StartingPositionTimestamp'] = mapping['StartingPositionTimestamp']  # noqa: E501

        try:
            lambdaClient.create_event_source_mapping(**createKwargs)
        except lambdaClient.exceptions.ResourceConflictException as err:
            logger.info('Event Mapping already exists, update')
            logger.debug(err)
            updateEventMapping(lambdaClient, mapping, configDict)


def updateEventMapping(client, mapping, configDict):

    listSourceKwargs = {
        'EventSourceArn': mapping['EventSourceArn'],
        'FunctionName': configDict['function_name'],
        'MaxItems': 1
    }
    sourceMappings = client.list_event_source_mappings(**listSourceKwargs)
    mappingMeta = sourceMappings['EventSourceMappings'][0]

    updateKwargs = {
        'UUID': mappingMeta['UUID'],
        'FunctionName': configDict['function_name'],
        'Enabled': mapping['Enabled'],
        'BatchSize': mapping['BatchSize'],
    }
    client.update_event_source_mapping(**updateKwargs)