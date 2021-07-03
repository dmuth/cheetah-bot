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

CMD="./cheetah-bot.py"

echo "# "
echo "# About to run Cheetah Bot with these arguments:"
echo "# "
if test "${TOKEN}"
then
	echo "# TOKEN: <REDACTED>"
else
	echo "# TOKEN: <NOT SET> - This will probably break the bot..."
fi
echo "# GROUP_NAMES: ${GROUP_NAMES}"
echo "# GROUP_IDS: ${GROUP_IDS}"
echo "# ACTIONS: ${ACTIONS}"
echo "# PERIOD: ${PERIOD}"
echo "# POST_EVERY: ${POST_EVERY}"
echo "# CHEE_MORE: ${CHEE_MORE}"
echo "# POSTS_FILE: ${POSTS_FILE}"
echo "# PROFANITY_REPLY: ${PROFANITY_REPLY}"
echo "# HTTP_PROXY: ${HTTP_PROXY}"
echo "# HTTPS_PROXY: ${HTTPS_PROXY}"
echo "# "

ARGS=""
if test "${PROFANITY_REPLY}" 
then
	if test "${PROFANITY_REPLY}" != "0"
	then
		echo "TEST TRUE2 ${PROFANITY_REPLY}"
		ARGS="${ARGS} --profanity-reply"
	fi
fi

#set -x # Debugging
exec ${CMD} ${TOKEN} --group_names ${GROUP_NAMES} --group_ids ${GROUP_IDS} \
	--actions ${ACTIONS} --period ${PERIOD} --post-every ${POST_EVERY} \
	--posts-file ${POSTS_FILE} ${ARGS} 



