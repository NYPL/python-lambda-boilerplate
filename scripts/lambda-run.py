import subprocess
import sys
import os
import re
import yaml

# This script is used on the command line and by Travis to execute various
# commands around a python lambda. This includes deployment, local invocations,
# and tests/test coverage. It attempts to replicate some of the functionality
# provided through node/package.json
# H/T to Paul Beaudoin for the inspiration


def main(runType):

    if re.match(r'^(?:development|qa|production)', runType):
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

    elif re.match(r'^run-local', runType):
        setEnvVars('development')
        subprocess.run([
            'lambda',
            'invoke',
            '-v',
            '--config-file',
            'run_config.yaml'
        ])
        os.remove('run_config.yaml')

    elif re.match(r'^build', runType)
        subprocess.run([
            'lambda',
            'build',
            '--requirements',
            'requirements.txt'
        ])


def setEnvVars(runType):

    # Load env variables from relevant .yaml file
    with open('config/{}.yaml'.format(runType)) as envStream:
        try:
            envDict = yaml.load(envStream)
        except yaml.YAMLError:
            print('Invalid {} YAML file! Please review'.format(runType))
            sys.exit(2)

    # Overwrite/add any vars in the core config.yaml file
    with open('config.yaml') as configStream:
        try:
            configDict = yaml.load(configStream)
        except yaml.YAMLError:
            print('Invalid config.yaml file! Please review')
            sys.exit(2)
        configLines = configStream.readlines()

    with open('config.yaml', 'r') as configStream:
        configLines = configStream.readlines()

    envVars = configDict['environment_variables']
    for key, value in envDict['environment_variables'].items():
        envVars[key] = value

    newEnvVars = yaml.dump({
        'environment_variables': envVars
    }, default_flow_style=False)

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


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('This script takes one, and only one, argument!')
        sys.exit(1)

    runType = sys.argv[1]
    main(runType)
