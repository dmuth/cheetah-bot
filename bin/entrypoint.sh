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
	echo "#	${CMD}"
	echo "# "
	echo "# to start the bot, or this to capture all output in the parent container:"
	echo "# "
	echo "#	${CMD} 2>&1 | tee output.txt"
	echo "# "
	echo "# Environment variables will be printed as confirmation."
	echo "# "
	echo "# If you are running mitmproxy on the host machine, run this to import the mitm CA: "
	echo "# "
	echo "#	./bin/import-mitmproxy-cert.py"
	echo "# "
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

echo "# "
echo "# Running ${CMD}..."
echo "# "
exec ${CMD}



