# Taken from: https://github.com/sensu/sensu-go-ansible/blob/master/Makefile
COLOR_OK=\\x1b[0;32m
COLOR_NONE=\x1b[0m
COLOR_ERROR=\x1b[31;01m
COLOR_WARNING=\x1b[33;01m
COLOR_ZSCALER=\x1B[34;01m

VERSION=$(shell grep -E -o '(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?' ./plugins/module_utils/version.py)

help:
	@echo "$(COLOR_ZSCALER)"
	@echo "  ______              _           "
	@echo " |___  /             | |          "
	@echo "    / / ___  ___ __ _| | ___ _ __ "
	@echo "   / / / __|/ __/ _\` | |/ _ \ '__|"
	@echo "  / /__\__ \ (_| (_| | |  __/ |   "
	@echo " /_____|___/\___\__,_|_|\___|_|   "
	@echo "                                  "
	@echo "                                  "
	@echo "$(COLOR_NONE)"
	@echo "$(COLOR_OK)ZPA Ansible Collection$(COLOR_NONE) version $(COLOR_WARNING)$(VERSION)$(COLOR_NONE)"
	@echo ""
	@echo "$(COLOR_WARNING)Usage:$(COLOR_NONE)"
	@echo "$(COLOR_OK)  make [command]$(COLOR_NONE)"
	@echo ""
	@echo "$(COLOR_WARNING)Available commands:$(COLOR_NONE)"
	@echo "$(COLOR_OK)  help$(COLOR_NONE)           Show this help message"
	@echo "$(COLOR_WARNING)clean$(COLOR_NONE)"
	@echo "$(COLOR_OK)  clean                      	Remove all auto-generated files$(COLOR_NONE)"
	@echo "$(COLOR_WARNING)development$(COLOR_NONE)"
	@echo "$(COLOR_OK)  check-format               	Check code format/style with black$(COLOR_NONE)"
	@echo "$(COLOR_OK)  format                     	Reformat code with black$(COLOR_NONE)"
	@echo "$(COLOR_OK)  docs                       	Build collection documentation$(COLOR_NONE)"
	@echo "$(COLOR_OK)  reqs                       	Recreate the requirements.txt file$(COLOR_NONE)"
	@echo "$(COLOR_WARNING)test$(COLOR_NONE)"
	@echo "$(COLOR_OK)  test:unit                     Execute the unit test suite$(COLOR_NONE)"
	@echo "$(COLOR_OK)  test:unit:coverage            Execute unit tests with coverage report$(COLOR_NONE)"
	@echo "$(COLOR_OK)  test:integration:zpa          Execute the full integration test suite$(COLOR_NONE)"
	@echo "$(COLOR_OK)  test:integration:coverage     Execute integration tests with coverage$(COLOR_NONE)"
	@echo "$(COLOR_OK)  coverage:html                 Generate HTML coverage report$(COLOR_NONE)"
	@echo "$(COLOR_OK)  coverage:report               Show coverage report in terminal$(COLOR_NONE)"
	@echo "$(COLOR_OK)  old-sanity          		Sanity tests for Ansible v2.9 and Ansible v2.10$(COLOR_NONE)"
	@echo "$(COLOR_OK)  new-sanity          	        Sanity tests for Ansible v2.11 and above$(COLOR_NONE)"
# Make sure we have ansible_collections/zscaler/zpacloud_enhanced
# as a prefix. This is ugly as heck, but it works. I suggest all future
# developer to treat next few lines as an opportunity to learn a thing or two
# about GNU make ;)

collection := $(notdir $(realpath $(CURDIR)      ))
namespace  := $(notdir $(realpath $(CURDIR)/..   ))
toplevel   := $(notdir $(realpath $(CURDIR)/../..))

err_msg := Place collection at <WHATEVER>/ansible_collections/zscaler/zpacloud
ifneq (zpacloud,$(collection))
  $(error $(err_msg))
else ifneq (zscaler,$(namespace))
  $(error $(err_msg))
else ifneq (ansible_collections,$(toplevel))
  $(error $(err_msg))
endif

python_version := $(shell \
  python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))' \
)

.PHONY: docs
docs:		## Build collection documentation
	rm -rf antsibull
	mkdir antsibull
	poetry run pip install -r docs/dev_requirements.txt
	poetry run antsibull-docs collection --use-current --dest-dir antsibull --no-indexes zscaler.zpacloud
	mkdir -p docs/source/modules
	mv antsibull/collections/zscaler/zpacloud/* docs/source/modules
	rm -rf antsibull
	rm -f docs/source/modules/index.rst
	cd docs && sphinx-build source html

clean:		## Remove all auto-generated files
	rm -rf tests/output
	rm -rf *.tar.gz
	rm -rf .coverage coverage.xml htmlcov .pytest_cache
	rm -rf .tox .eggs *.egg-info

.PHONY: format
format:		## Format with black
	poetry run black .

.PHONY: check-format
check-format:	## Check with black
	poetry run black --check --diff .

test\:unit:
	@echo "$(COLOR_ZSCALER)Running unit tests...$(COLOR_NONE)"
	poetry run pytest tests/unit/ -v --tb=short

test\:unit\:coverage:
	@echo "$(COLOR_ZSCALER)Running unit tests with coverage...$(COLOR_NONE)"
	poetry run pytest tests/unit/ -v --tb=short \
		--cov=plugins \
		--cov-report=xml:coverage.xml \
		--cov-report=html:tests/output/coverage \
		--cov-report=term-missing
	@echo "$(COLOR_OK)Coverage report generated at tests/output/coverage/index.html$(COLOR_NONE)"

test\:integration\:zpa:
	@echo "$(COLOR_ZSCALER)Running zpa integration tests...$(COLOR_NONE)"
	poetry run ansible-playbook tests/integration/run_all_tests.yml

test\:integration\:coverage:
	@echo "$(COLOR_ZSCALER)Running integration tests with coverage...$(COLOR_NONE)"
	poetry run ansible-test coverage erase
	poetry run ansible-test integration --coverage --python $(python_version) -v
	poetry run ansible-test coverage xml --requirements
	poetry run ansible-test coverage html --requirements
	@echo "$(COLOR_OK)Coverage report generated at tests/output/coverage/$(COLOR_NONE)"

coverage\:html:
	@echo "$(COLOR_ZSCALER)Generating HTML coverage report...$(COLOR_NONE)"
	poetry run coverage html -d tests/output/coverage
	@echo "$(COLOR_OK)Open tests/output/coverage/index.html in your browser$(COLOR_NONE)"

coverage\:report:
	@echo "$(COLOR_ZSCALER)Coverage Report:$(COLOR_NONE)"
	poetry run coverage report --show-missing

.PHONY: old-sanity
old-sanity:		## Sanity tests for Ansible v2.9 and Ansible v2.10
	ansible-test sanity -v --skip-test pylint --skip-test rstcheck --python $(python_version)

.PHONY: new-sanity
new-sanity:		## Sanity tests for Ansible v2.11 and above
	ansible-test sanity -v --skip-test pylint --skip-test pep8 --python $(python_version)

.PHONY: new-sanity-docker
new-sanity-docker:
	ansible-test sanity --docker default -v

.PHONY: reqs
reqs:       ## Recreate the requirements.txt file
	poetry export -f requirements.txt --output requirements.txt --only=main --without-hashes
	poetry run python ./.github/update-requirements.py

install:
	rm -f zscaler-zpacloud-*.tar.gz
	poetry run ansible-galaxy collection build . --force
	poetry run ansible-galaxy collection install zscaler-zpacloud-*.tar.gz --force
	rm -f zscaler-zpacloud-*.tar.gz

.PHONY: clean-pyc clean-build docs clean local-setup