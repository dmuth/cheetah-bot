#!/bin/sh
#
# The entrypoint script, which is run when the container is started.
#

# Errors are fatal
set -e


# Our command to run
CMD="/mnt/cheetah-bot.py"

if test "$1"
then
	echo "# "
	echo "# Argument specified! Executing command: $@"
	echo "# "
	echo "# Run ${CMD} to start the bot"
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

if test ! "${GROUP_NAME}"
then
	if test ! "${GROUP_ID}"
	then
		echo "! "
		echo "! Neither GROUP_NAME nor GROUP_ID are specified in env!"
		echo "! "
		echo "! I need at least ONE set to allowlist specific groups, so I'm gonna bail."
		echo "! "
		exit 1
	fi
fi


echo "# "
echo "# Running ${CMD}..."
echo "# "
exec ${CMD} ${TOKEN} --group_name "${GROUP_NAME}" --group_id "${GROUP_ID}"


