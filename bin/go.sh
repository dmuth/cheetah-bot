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
# If the first argument is bash, then mount the current directory as /mnt.
#
V=""
if test "$1" == "bash"
then
	V="-v $(pwd):/mnt"
fi


#
# Go through all of our variables, and set each with a value 
# from .env if not currently set.
#
# I tried doing looping, but it looks like trying to set by a 
# dereferenced value doesn't work, alas.
#
test "${TOKEN}" || TOKEN=$(cat ./.env | egrep "^TOKEN=" | cut -d= -f2- | sed -e 's/^"//' -e 's/"$//')
test "${GROUP_NAMES}" || GROUP_NAMES=$(cat ./.env | egrep "^GROUP_NAMES=" | cut -d= -f2- | sed -e 's/^"//' -e 's/"$//')
test "${GROUP_IDS}" || GROUP_IDS=$(cat ./.env | egrep "^GROUP_IDS=" | cut -d= -f2- | sed -e 's/^"//' -e 's/"$//')
test "${ACTIONS}" || ACTIONS=$(cat ./.env | egrep "^ACTIONS=" | cut -d= -f2- | sed -e 's/^"//' -e 's/"$//')
test "${PERIOD}" || PERIOD=$(cat ./.env | egrep "^PERIOD=" | cut -d= -f2- | sed -e 's/^"//' -e 's/"$//')
test "${POST_EVERY}" || POST_EVERY=$(cat ./.env | egrep "^POST_EVERY=" | cut -d= -f2- | sed -e 's/^"//' -e 's/"$//')
test "${CHEE_MORE}" || CHEE_MORE=$(cat ./.env | egrep "^CHEE_MORE=" | cut -d= -f2- | sed -e 's/^"//' -e 's/"$//')
test "${QUOTES_FILE}" || QUOTES_FILE=$(cat ./.env | egrep "^QUOTES_FILE=" | cut -d= -f2- | sed -e 's/^"//' -e 's/"$//')
test "${IMAGES_FILE}" || IMAGES_FILE=$(cat ./.env | egrep "^IMAGES_FILE=" | cut -d= -f2- | sed -e 's/^"//' -e 's/"$//')
test "${HTTP_PROXY}" || HTTP_PROXY=$(cat ./.env | egrep "^HTTP_PROXY=" | cut -d= -f2- | sed -e 's/^"//' -e 's/"$//')
test "${HTTPS_PROXY}" || HTTPS_PROXY=$(cat ./.env | egrep "^HTTPS_PROXY=" | cut -d= -f2- | sed -e 's/^"//' -e 's/"$//')

#
# Run our Docker container with any arguments that were passed in
#
docker run -it \
	${V} \
	-e "TOKEN=${TOKEN}" \
	-e "GROUP_NAMES=${GROUP_NAMES}" \
	-e "GROUP_IDS=${GROUP_IDS}" \
	-e "ACTIONS=${ACTIONS}" \
	-e "PERIOD=${PERIOD}" \
	-e "POST_EVERY=${POST_EVERY}" \
	-e "CHEE_MORE=${CHEE_MORE}" \
	-e "QUOTES_FILE=${QUOTES_FILE}" \
	-e "IMAGES_FILE=${IMAGES_FILE}" \
	-e "HTTP_PROXY=${HTTP_PROXY}" \
	-e "HTTPS_PROXY=${HTTPS_PROXY}" \
	cheetah-bot $@

echo "# Done!"

