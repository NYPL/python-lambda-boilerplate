# Python Lambda Boilerplate

[![Build Status](https://travis-ci.com/NYPL/python-lambda-boilerplate.svg?branch=master)](https://travis-ci.com/NYPL/python-lambda-boilerplate)



A simple boilerplate/starter for creating AWS Lambdas in python (python3.3+). This relies on the [python-lambda](https://github.com/nficano/python-lambda) module for deployment and managing environment variables. It allows you to run local tests and automatically deploy code to AWS based on local variables. This was inspired and largely guided by the [node-lambda-boilerplate](https://github.com/nypl/node-lambda-boilerplate) repository

## Version

v0.1.0

## Requirements

Python 3.6+ (written with Python 3.7)

## Features

- Makefile to run basic commands for building/testing/deploying the Lambda
- Contains unit test scaffolding in /tests
- Includes linting via flake8
- Contains logger and custom error message helpers in /helpers
- Supports TravisCI

## Getting Started

### Installation

1. Create a virtualenv (varies depending on your shell) and activate it
2. Install dependencies via `pip install -r requirements.txt`

### Setup Configurations

**Step 1**
After installing dependencies, copy the config.yaml.sample file to config.yaml and modify the relevant values. At a minimum the following settings should be changed:

- function_name
- description
- role

**Step 2**
Uncomment the `environment_variable` blocks in the relevant config files (if necessary) and add environment-specific configuration in those areas

**Step 3**
Modify the included event.json to add to the Records block, which enables the Lambda to be tested locally

### Develop Locally

To run your lambda locally run `make local-run` which will execute the Lambda (initially outputting "Hello, World")

### Deploy the Lambda

To deploy the Lambda be sure that you have completed the setup steps above and have tested your lambda, as well as configured any necessary environment variables.

To run the deployment run `make deploy ENV=[environment]` where environment is one of development/qa/production

**Deploy via TravisCI**
Lambdas based on this code can also be deployed via TravisCI. To do uncomment the relevant lines in the .travis.yaml file and see the [NYPL General Engineering](https://github.com/NYPL/engineering-general/blob/master/standards/travis-ci.md#deploy) documentation for a guide on how to add the deploy step and *necessary* encrypted credentials

## Tests

The stock python `unittest` is currently used to provide test coverage and can be run with `make test`

Coverage is used to measure test coverage and a report can be seen by running `make coverage-report`

## Linting

Linting is provided via Flake8 and can be run with `make lint`
