#!/usr/bin/env bash

set -e
set -x

mypy src
ty check src
ruff check src tests scripts
ruff format src tests --check
