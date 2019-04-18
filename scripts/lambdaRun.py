import subprocess
import sys
import os
import re

from helpers.logHelpers import createLog
from helpers.errorHelpers import InvalidExecutionType
from helpers.clientHelpers import createEventMapping
from helpers.configHelpers import setEnvVars

logger = createLog('runScripts')


def main():
    """Invoked by the makefile's arguments, controls the overall execution of
    the Lambda function. h/t to nonword for inspiration to use a makefile.

    Raises:
        InvalidExecutionType: If the args do not contain a valid execution type
        raise an error.
    """
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
        logger.info(
            'Building package for {} environment, will be in dist/'.format(env)
        )
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


if __name__ == '__main__':
    main()
