import subprocess
import sys
import os

from helpers.logHelpers import createLog
from helpers.errorHelpers import InvalidExecutionType
from helpers.clientHelpers import createEventMapping
from helpers.configHelpers import setEnvVars

logger = createLog('runScripts')


def main():
    """Invoked by the makefile's arguments, controls the overall execution of
    the Lambda function. h/t to nonword for inspiration to use a makefile."""

    if len(sys.argv) != 2:
        logger.warning('This script takes one, and only one, argument!')
        sys.exit(1)

    runType = sys.argv[1]

    # Map the possible valid execution commands.
    runTypeFuncs = {
        'local': deployFunc,
        'development': deployFunc,
        'qa': deployFunc,
        'production': deployFunc,
        'run-local': runFunc,
        'build-development': buildFunc,
        'build-qa': buildFunc,
        'build-production': buildFunc
    }

    # Execute desired function. If not found, raise an error.
    runTypeFuncs.get(runType, errFunc)(runType)

    # Remove computed configuration file. This is only used during runtime.
    os.remove('run_config.yaml')


def deployFunc(runType):
    """Deploys the current Lambda function to the environment specificied
    in the current configuration file.

    Arguments:
        runType {string} -- The environment to deploy the function to. Should
        be one of [local|development|qa|production]
    """
    logger.info('Deploying lambda to {} environment'.format(runType))
    runProcess(runType, [
        'deploy',
        '--config-file',
        'run_config.yaml',
        '--requirements',
        'requirements.txt'
    ])
    createEventMapping(runType)


def buildFunc(runType):
    """Builds a deployment package that can be uploaded to AWS or a testing
    environment.

    Arguments:
        runType {string} -- The environment to build the function for. Should
        be one of [development|qa|production]. (Local builds are unnecessary as
        the code can be executed from the development directory.)
    """
    buildEnv = runType.replace('build-', '')
    logger.info(
        'Building package for {}, will be in dist/'.format(buildEnv)
    )
    runProcess(buildEnv, [
        'build',
        '--requirements',
        'requirements.txt',
        '--config-file',
        'run_config.yaml'
    ])


def runFunc(runType):
    """Invokes the lambda function with currently configured local settings.

    Arguments:
        runType {string} -- The environment variables to execute the function
        with, should always be local.
    """
    logger.info('Running test locally with development environment')
    runProcess('local', ['invoke', '-v', '--config-file', 'run_config.yaml'])


def errFunc(runType):
    """Raises an error when an unknown command is received.

    Arguments:
        runType {string} -- The unknown command received by this function,

    Raises:
        InvalidExecutionType: Indicates that this module cannot execute the
        requested command.
    """
    logger.error('Execution type not recognized! {}'.format(runType))
    raise InvalidExecutionType('{} is not a valid command'.format(runType))


def runProcess(runType, argList):
    """Executes the requested command through a subprocess call to the CLI.

    Arguments:
        runType {string} -- The current environment to load settings for.
        argList {array} -- An array of command line arguments that dictate
        the specific type of invocation being made to `python-lambda`
    """
    setEnvVars(runType)  # Creates the run_config.yaml file
    processArgs = ['lambda']
    processArgs.extend(argList)
    subprocess.run(processArgs)  # Executes the actual command


if __name__ == '__main__':
    main()
