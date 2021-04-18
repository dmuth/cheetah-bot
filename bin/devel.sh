#!/bin/bash

# Errors are fatal
set -e


#
# Change to the parent of this script
#
pushd $(dirname $0) > /dev/null
cd ..

#
# Build our container
#
./bin/build.sh

#
# Run the container with a spawned bash shell
#
docker run -it -v $(pwd):/mnt cheetah-bot bash


