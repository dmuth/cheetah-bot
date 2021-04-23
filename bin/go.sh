#!/bin/bash
#
# Run our container
#

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
# Run our Docker container with any arguments that were passed in
#
docker run -it \
	-e "TOKEN=${TOKEN}" \
	-e "GROUP_NAMES=${GROUP_NAMES}" \
	-e "GROUP_IDS=${GROUP_IDS}" \
	-e "ACTIONS=${ACTIONS}" \
	-e "PERIOD=${PERIOD}" \
	-e "REPLY_EVERY_N_MESSAGES=${REPLY_EVERY_N_MESSAGES}" \
	-e "QUOTES_FILE=${QUOTES_FILE}" \
	-e "URLS_FILE=${URLS_FILE}" \
	cheetah-bot $@

echo "# Done!"

