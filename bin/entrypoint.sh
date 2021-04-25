#!/bin/sh
#
# The entrypoint script, which is run when the container is started.
#

# Errors are fatal
set -e


# Our command to run
CMD="/mnt/bin/run-bot.sh"

if test "$1"
then
	echo "# "
	echo "# Argument specified! Executing command: $@"
	echo "# "
	echo "# Run "
	echo "# "
	echo "# ${CMD}"
	echo "# "
	echo "# to start the bot"
	echo "# "
	echo "# Environment variables will be printed as confirmation."
	echo "# "
	exec $@
fi

cd /mnt

if test ! "${TOKEN}"
then
	echo "! "
	echo "! TOKEN env var not specified, bailing out!"
	echo "! "
	exit 1
fi

if test ! "${GROUP_NAMES}"
then
	if test ! "${GROUP_IDS}"
	then
		echo "! "
		echo "! Neither GROUP_NAMES nor GROUP_IDS are specified in env!"
		echo "! "
		echo "! I need at least ONE set to allowlist specific groups, so I'm gonna bail."
		echo "! "
		exit 1
	fi
fi


echo "# "
echo "# Running ${CMD}..."
echo "# "
exec ${CMD} ${TOKEN} --group_names "${GROUP_NAMES}" --group_ids "${GROUP_IDS}" \
	--actions ${ACTIONS} --period ${PERIOD} \
	--quotes-file ${QUOTES_FILE} --urls-file ${URLS_FILE}



