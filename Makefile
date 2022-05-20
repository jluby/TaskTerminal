#!/usr/bin/make -f
SHELL = /bin/sh
.DELETE_ON_ERROR:

# boilerplate variables, do not edit
MAKEFILE_PATH := $(abspath $(firstword $(MAKEFILE_LIST)))
MAKEFILE_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

# required values
PACKAGE_DIR ?= src
LINTING_LINELENGTH ?= 120
PYTHON ?= python3
CODECOV_TOKEN ?= ${CODECOV_TOKEN}

# firm variables, usually the same but potentially require editing for current repo
CLEAN_DIR_LIST_INCLUDED = $(PACKAGE_DIR)
CLEAN_DIR_REGEX_INCLUDED = $(PACKAGE_DIR)


# use regex to go through this Makefile and print help lines
# help lines is any comment starting with double '#' (see next comment). Prints alphabetical order.
## help :		print this help.
.PHONY: help
help: Makefile
	@echo "\nPersonal package for managing project TODOs, notes, and references."
	@echo "\n	Generic commands"
	@sed -n 's/^## /		/p' $< | sort


## variables : 	list all variables in the Makefile.
.PHONY: variables
variables:
	@echo MAKEFILE_PATH: $(MAKEFILE_PATH)
	@echo MAKEFILE_DIR: $(MAKEFILE_DIR)
	@echo PYTHON: $(PYTHON)


## clean : 	remove temporary files from repo.
# note: complex regex like (src|test) is not compatible for both OSX and Ubuntu with the same command, hence the loop over directory names
delete-pattern = find . -regex 'pattern' -delete
.PHONY: clean, clean-build, clean-pyc, clean-test
clean: clean-build clean-pyc clean-test
clean-build:
	@rm -rf build/
	@rm -rf dist/
	@rm -rf .eggs/
	@for dir in $(CLEAN_DIR_LIST_INCLUDED); do find . -regex "\./$${dir}/.*egg-info.*" -delete; done
	@for dir in $(CLEAN_DIR_LIST_INCLUDED); do find . -regex "\./$${dir}/.*egg.*" -delete; done
clean-pyc:
	@for dir in $(CLEAN_DIR_LIST_INCLUDED); do find . -regex "\./$${dir}/.*\.py[co]" -delete; done
	@for dir in $(CLEAN_DIR_LIST_INCLUDED); do find . -regex "\./$${dir}/.*__pycache__.*" -delete; done
clean-test:
	@rm -f .coverage
	@rm -rf .pytest_cache/


## format : 	apply style scripts to Python scripts
.PHONY: format-py format
format-py: clean
	$(PYTHON) -m black --include="($(CLEAN_DIR_REGEX_INCLUDED)).*\.pyi?$$" --line-length $(LINTING_LINELENGTH) .
	$(PYTHON) -m isort --line-width $(LINTING_LINELENGTH) --multi-line 3 --trailing-comma $(CLEAN_DIR_LIST_INCLUDED)
format: format-py


## lint :		test that code adheres to style guides.
.PHONY: lint-py lint
lint-py: clean
	$(PYTHON) -m black --check --include="($(CLEAN_DIR_REGEX_INCLUDED)).*\.pyi?$$" --line-length $(LINTING_LINELENGTH) .
	$(PYTHON) -m isort \
		--check-only \
		--line-width $(LINTING_LINELENGTH) \
		--multi-line 3 \
		--trailing-comma \
		$(CLEAN_DIR_LIST_INCLUDED)
lint: lint-py

## autoflake :		delete unused imports.
.PHONY: autoflake flake
autoflake:
	autoflake -r --in-place --remove-all-unused-imports $(CLEAN_DIR_LIST_INCLUDED)
flake: autoflake