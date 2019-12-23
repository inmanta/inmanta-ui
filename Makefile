# Shortcuts for various dev tasks. Based on makefile from pydantic
.DEFAULT_GOAL := all
isort = isort -rc src tests
black = black src tests

VERSION := $(shell python3 setup.py -V)
RPMDIR := "$(shell pwd)/rpms"

ifndef $(RELEASE)
RELEASE := dev
endif

ifeq ($(BUILDID),)
   ifeq ("$(RELEASE)","dev")
BUILDID := .dev$(shell date --utc +%Y%m%d%H%M)
   endif
   ifeq ("$(RELEASE)","next")
BUILDID := .next$(shell date --utc +%Y%m%d%H%M)
   endif
endif

ifeq ($(RELEASE), dev)
ISO_REPO := inmanta-service-orchestrator-3-dev
REPOMANAGER_REPO := inmanta-service-orchestrator-dev/3
endif
ifeq ($(RELEASE), next)
ISO_REPO := inmanta-service-orchestrator-3-next
REPOMANAGER_REPO := inmanta-service-orchestrator-next/3
endif
ifeq ($(RELEASE), stable)
ISO_REPO := inmanta-service-orchestrator-3
REPOMANAGER_REPO := inmanta-service-orchestrator/3
endif

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
	rm -rf build dist *.egg-info rpms
	find -name .env | xargs rm -rf
	python setup.py clean

.PHONY: ensure-valid-release-type
ensure-valid-release-type:
ifneq ($(RELEASE), dev)
  ifneq ($(RELEASE), next)
    ifneq ($(RELEASE), stable)
    $(error RELEASE parameter should have value 'dev', 'next' or 'stable')
    endif
  endif
endif

.PHONY: build
build: ensure-valid-release-type
	rm -rf dist/*
	pip3 install -U wheel
	python3 setup.py egg_info -Db "$(BUILDID)" sdist bdist_wheel

.PHONY: set-web-console-version
set-web-console-version:
ifeq ($(WEB_CONSOLE_VERSION),)
	npm config set @inmanta:registry https://npm.pkg.github.com
	npm config set //npm.pkg.github.com/:_authToken ${GITHUB_TOKEN}
	$(eval WEB_CONSOLE_VERSION := $(shell npm view @inmanta/web-console --json |jq -r '."dist-tags".latest'))
endif

.PHONY: upload-python-package
upload-python-package: build
	pip install -U devpi-client
	devpi use https://artifacts.internal.inmanta.com/inmanta/$(RELEASE)
	devpi login ${DEVPI_USER} --password=${DEVPI_PASS}
	# upload packages
	devpi upload dist/*
	devpi logoff

.PHONY: collect-dependencies
collect-dependencies: ensure-valid-release-type set-web-console-version
	mkdir -p dist
	export PIP_INDEX_URL="https://artifacts.internal.inmanta.com/inmanta/$(RELEASE)"; python3 -m irt.main package-dependencies --package-dir . --constraint-file ./requirements.txt --destination "dist/deps-${VERSION}$(BUILDID).tar.gz"
	# Download npm package from github packages
	npm config set @inmanta:registry https://npm.pkg.github.com
	npm config set //npm.pkg.github.com/:_authToken ${GITHUB_TOKEN}
	cd dist; npm pack @inmanta/web-console@$(WEB_CONSOLE_VERSION)

.PHONY: rpm
rpm: ensure-valid-release-type set-web-console-version build collect-dependencies
	rm -rf ${RPMDIR}
	sed -i '0,/^%define version.*/s/^%define version.*/%define version ${VERSION}/' inmanta.spec

ifneq ($(BUILDID),)
	sed -i '0,/^%define buildid.*/s/^%define buildid.*/%define buildid $(BUILDID)/' inmanta.spec
else
	sed -i '0,/^%define buildid.*/s/^%define buildid.*/%define buildid %{nil}/' inmanta.spec
endif

ifneq ("$(RELEASE)","stable")
	sed -i '0,/^%define release.*/s/^%define release.*/%define release 0/' inmanta.spec
endif

	mock -r inmanta-and-epel-7-x86_64 --bootstrap-chroot --enablerepo="inmanta-oss-$(RELEASE),$(ISO_REPO)" --define="web_console_version $(WEB_CONSOLE_VERSION)" --buildsrpm --spec inmanta.spec --sources dist --resultdir ${RPMDIR}
	mock -r inmanta-and-epel-7-x86_64 --bootstrap-chroot --enablerepo="inmanta-oss-$(RELEASE),$(ISO_REPO)" --define="web_console_version $(WEB_CONSOLE_VERSION)" --rebuild ${RPMDIR}/python3-inmanta-ui-${VERSION}-*.src.rpm --resultdir ${RPMDIR}

.PHONY: upload
upload: RPM := $(shell basename ${RPMDIR}/python3-inmanta-ui-${VERSION}-*.x86_64.rpm)

.PHONY: upload
upload: ensure-valid-release-type
	@echo Uploading $(RPM)
	ssh repomanager@jenkins.ii.inmanta.com "/usr/bin/repomanager --config /etc/repomanager.toml --repo $(REPOMANAGER_REPO) --distro el7 --file - --file-name ${RPM}" < ${RPMDIR}/${RPM}
