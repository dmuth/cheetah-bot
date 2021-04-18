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

echo "# "
echo "# Running ${CMD}..."
echo "# "
exec ${CMD}

