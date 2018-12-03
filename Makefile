

.DEFAULT: help
help:
	@echo "make help"
	@echo "    display this help statement"
	@echo "make deploy"
	@echo "    deploy lambda using python-lambda to the environemnt specified as: "
	@echo "    make deploy ENV=[environment]"
	@echo "make run-local"
	@echo "    invoke python-lambda's local test environement"
	@echo "    uses the development environemnt variables and the events in event.json"
	@echo "make build"
	@echo "    package the lambda for upload to AWS. Puts output in dist/"
	@echo "make test"
	@echo "    runs unittests defined in tests/ directory"
	@echo "make coverage-report"
	@echo "    display report on test coverage"
	@echo "make link"
	@echo "    lint package with flake8"

deploy:
	python3 -m scripts.lambdaRun $(ENV)

run-local:
	python3 -m scripts.lambdaRun run-local

build:
	python3 -m scripts.lambdaRun build-$(ENV)

test:
	coverage3 run -m unittest

coverage-report:
	coverage3 report -m

lint:
	flake8
