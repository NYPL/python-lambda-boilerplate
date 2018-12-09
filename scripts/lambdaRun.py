import subprocess
import sys
import os
import shutil
import re
import yaml
import json

import boto3

from helpers.logHelpers import createLog
from helpers.errorHelpers import InvalidExecutionType

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

    if re.match(r'^(?:development|qa|production)', runType):
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
        env = 'development'
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
    except FileNotFoundError as err:
        logger.info('No Event Source mapping provided')
        return
    except IOError as err:
        logger.error('Unable to open JSON file')
        raise err

    if len(eventMappings['EventSourceMappings']) < 1:
        logger.info('No event sources defined')
        return

    configDict, configLines = loadEnvFile(runType, None)

    lambdaClient = createAWSClient(configDict)

    for mapping in eventMappings['EventSourceMappings']:
        logger.debug('Adding event source mapping for function')

        createKwargs = {
            'EventSourceArn': mapping['EventSourceArn'],
            'FunctionName': configDict['function_name'],
            'Enabled': mapping['Enabled'],
            'BatchSize': mapping['BatchSize'],
            'StartingPosition': mapping['StartingPosition']
        }

        if mapping['StartingPosition'] == 'AT_TIMESTAMP':
            createKwargs['StartingPositionTimestamp'] = mapping['StartingPositionTimestamp']  # noqa: E501

        lambdaClient.create_event_source_mapping(**createKwargs)


def createAWSClient(configDict):

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
        'lambda',
        **clientKwargs
    )

    return lambdaClient


def loadEnvFile(runType, fileString):

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
        logger.error('Missing config YAML file! Check directory')
        raise err

    if envDict is None:
        envDict = {}
    return envDict, fileLines


if __name__ == '__main__':
    main()
