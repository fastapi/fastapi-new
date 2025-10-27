#!/usr/bin/env bash
set -x

ruff check src tests scripts --fix
ruff format src tests scripts
