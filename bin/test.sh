#!/bin/sh

# Usage examples:
#   bin/test.sh
#   bin/test.sh tests/test_metadata.py
#   bin/test.sh tests/test_metadata.py::test_metadata_extraction

set -e

dir=$(dirname "$0")
cd "$dir/.."

if [ $# -gt 0 ]
then
  uv run python -m pytest -v -p no:faulthandler $@
else
  uv run python -m pytest -v -p no:faulthandler tests
fi
