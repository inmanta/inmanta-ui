# Shortcuts for various dev tasks. Based on makefile from pydantic
.DEFAULT_GOAL := all
isort = isort -rc src tests
black = black src tests

.PHONY: install
install:
	pip install -U setuptools pip
	pip install -U -r requirements.txt
	pip install -e .

.PHONY: format
format:
	$(isort)
	$(black)

.PHONY: build-pytest-inmanta-extensions
build-pytest-inmanta-extensions:
	pip install -c requirements.txt -U setuptools pip
	git clone https://github.com/inmanta/inmanta.git inmanta-core
	python3 inmanta-core/tests_common/copy_files_from_core.py
	cd inmanta-core/tests_common/; python3 setup.py sdist --dist-dir ../../extra_dist
	rm -rf inmanta-core

.PHONY: pep8
pep8:
	pip install -c requirements.txt pep8-naming flake8-black flake8-isort
	flake8 src tests

.PHONY: mypy
mypy:
	MYPYPATH=src python -m mypy --html-report mypy -p inmanta_ui

.PHONY: test
test:
	pytest -vvv tests

.PHONY: testcov
testcov:
	pytest --cov=inmanta_ext.inmanta_ui --cov=inmanta_ui --cov-report html:coverage --cov-report term -vvv tests

.PHONY: all
all: pep8 test mypy

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf mypy
	rm -rf coverage
	rm -rf *.egg-info
	rm -f .coverage
	rm -f .coverage.*
	rm -rf build
	find -name .env | xargs rm -rf
	python setup.py clean