#!/bin/bash
#
# This script is a wrapper for running Cheetah Bot from the dev container or CLI.
#

# Errors are fatal
set -e

#
# Change to the parent of this script
#
pushd $(dirname $0) > /dev/null
cd ..

#
# Add our lib to the path
#
export PYTHONPATH=$PYTHONPATH:$(pwd)/lib

echo "#"
echo "# Running pytest $@ ..."
echo "#"
pytest $@

