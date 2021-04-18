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
docker run -it \
	-v $(pwd):/mnt \
	-e "TOKEN=${TOKEN}" \
	-e "GROUP_NAME=${GROUP_NAME}" \
	-e "GROUP_ID=${GROUP_ID}" \
	cheetah-bot bash


