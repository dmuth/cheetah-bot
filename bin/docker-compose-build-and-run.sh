#!/bin/bash
#
# This script automates the process of stopping an existing container, (re)building it, and running it
# in the foreground.
#

# Errors are fatal
set -e

#
# Signal received, killing the container and exiting...
#
function cleanup() {

	echo "! "
	echo "! Signal received, killing the container and exiting..."
	echo "! "
	docker-compose kill
	exit

} # End of cleanup()

trap cleanup INT TERM


# Change to where this script lives
pushd $(dirname $0) > /dev/null

echo "# Killing any existing containers..."
docker-compose kill

echo "# Removing any existing containers..."
docker-compose rm -f

echo "# (re-)building container..."
docker-compose build

echo "# Starting up container..."
docker-compose up -d

echo "# And tailing the logs..."
docker-compose logs -f


