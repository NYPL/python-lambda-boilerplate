import json
import boto3

from helpers.logHelpers import createLog
from helpers.configHelpers import loadEnvVars, loadEnvFile

logger = createLog('clientHelpers')


def createAWSClient(service, configDict=None):
    """Creates a boto3 client object for communicating with a specific AWS
    service. This is always invoked by the lambda run/deployment scripts to
    create a client to the Lambda service, but can also be invoked within the
    Lambda function to connect to other AWS services.

    Arguments:
        service {string} -- The AWS service to create a connection to.

    Keyword Arguments:
        configDict {string} -- AWS Configuration details. If None/not provided
        details will be loaded from default config.yaml file (default: {None})

    Returns:
        [boto3.client] -- A client object that can be used to invoke various
        services from the associated AWS service.
    """
    if configDict is None:
        configDict = loadEnvFile(None, None)

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
    """Creates an event mapping that connects the deployed Lambda function to
    one or more event sources/triggers. This is optional but most functions
    should have at least one event source. Different environments can have
    different event sources configured.

    Arguments:
        runType {string} -- The environment the Lambda function is currently
        being deployed in.

    Raises:
        JSONDecodeError: If the event source JSON file is malformed, this
        will raise a JSON error as the script must be able to properly
        read this file for deployment.
        IOError: If the even source JSON file cannot be read because it is
        missing or the script lacks permissions to open it.
    """
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
            key: item for key, item in mapping.items()
        }
        createKwargs['FunctionName'] = configDict['function_name']

        try:
            lambdaClient.create_event_source_mapping(**createKwargs)
        except lambdaClient.exceptions.ResourceConflictException as err:
            logger.info('Event Mapping already exists, update')
            logger.debug(err)
            updateEventMapping(lambdaClient, mapping, configDict)


def updateEventMapping(client, mapping, configDict):
    """When the Lambda function exists with an event source in place, a
    different boto3 service must be invoked to update the existing source.

    Arguments:
        client {boto3.client} -- A boto3 lambda client object.
        mapping {dict} -- A dictionary containing the event source details.
        configDict {dict} -- A dictionary containing the function's config
        details.
    """
    listSourceKwargs = {
        'EventSourceArn': mapping.pop('EventSourceArn'),
        'FunctionName': configDict['function_name'],
        'MaxItems': 1
    }
    sourceMappings = client.list_event_source_mappings(**listSourceKwargs)
    mappingMeta = sourceMappings['EventSourceMappings'][0]

    updateKwargs = {
        key: item for key, item in mapping.items()
    }
    updateKwargs['UUID'] = mappingMeta['UUID']
    updateKwargs['FunctionName'] = configDict['function_name']

    client.update_event_source_mapping(**updateKwargs)
