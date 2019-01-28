import subprocess
import sys
import os
import shutil
import re
import yaml
import json

from helpers.logHelpers import createLog
from helpers.errorHelpers import InvalidExecutionType
from helpers.configHelpers import loadEnvFile
from helpers.clientHelpers import createAWSClient

logger = createLog('runScripts')

# This script is invoked by the Makefile in root to execute various
# commands around a python lambda. This includes deployment, local invocations,
# and tests/test coverage. It attempts to replicate some of the functionality
# provided through node/package.json
# H/T to Paul Beaudoin for the inspiration


def main():

    if len(sys.argv) != 2:
        logger.warning('This script takes one, and only one, argument!')
        sys.exit(1)
    runType = sys.argv[1]

    if re.match(r'^(?:local|development|qa|production)', runType):
        logger.info('Deploying lambda to {} environment'.format(runType))
        setEnvVars(runType)
        subprocess.run([
            'lambda',
            'deploy',
            '--config-file',
            'run_config.yaml',
            '--requirements',
            'requirements.txt'
        ])
        os.remove('run_config.yaml')
        createEventMapping(runType)

    elif re.match(r'^run-local', runType):
        logger.info('Running test locally with development environment')
        env = 'local'
        setEnvVars(env)
        subprocess.run([
            'lambda',
            'invoke',
            '-v',
            '--config-file',
            'run_config.yaml'
        ])
        os.remove('run_config.yaml')

    elif re.match(r'^build-(?:development|qa|production)', runType):
        env = runType.replace('build-', '')
        logger.info('Building package for {} environment, will be in dist/'.format(env))  # noqa: E501
        setEnvVars(env)
        subprocess.run([
            'lambda',
            'build',
            '--requirements',
            'requirements.txt',
            '--config-file',
            'run_config.yaml'
        ])
        os.remove('run_config.yaml')

    else:
        logger.error('Execution type not recognized! {}'.format(runType))
        raise InvalidExecutionType('{} is not a valid command'.format(runType))


def setEnvVars(runType):

    # Load env variables from relevant .yaml file
    envDict, envLines = loadEnvFile(runType, 'config/{}.yaml')

    # If no environemnt variables are set, do nothing to config
    if 'environment_variables' not in envDict:
        shutil.copyfile('config.yaml', 'run_config.yaml')
        return

    # Overwrite/add any vars in the core config.yaml file
    configDict, configLines = loadEnvFile(runType, None)

    envVars = configDict['environment_variables']
    for key, value in envDict['environment_variables'].items():
        envVars[key] = value

    newEnvVars = yaml.dump({
        'environment_variables': envVars
    }, default_flow_style=False)
    try:
        with open('run_config.yaml', 'w') as newConfig:
            write = True
            written = False
            for line in configLines:
                if line.strip() == '# === END_ENV_VARIABLES ===':
                    write = True

                if write is False and written is False:
                    newConfig.write(newEnvVars)
                    written = True
                elif write is True:
                    newConfig.write(line)

                if line.strip() == '# === START_ENV_VARIABLES ===':
                    write = False

    except IOError as err:
        logger.error(('Script lacks necessary permissions, '
                      'ensure user has permission to write to directory'))
        raise err


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

    configDict, configLines = loadEnvFile(runType, None)

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
                createKwargs['StartingPositionTimestamp'] = mapping['StartingPositionTimestamp']  # noqa: E50

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


if __name__ == '__main__':
    main()
