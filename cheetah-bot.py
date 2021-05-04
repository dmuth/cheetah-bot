#!/usr/bin/env python3
# Vim: :set softtabstop=0 noexpandtab tabstop=8 
#
# Telegram bot to repsond to a few messages in groups.
#


import argparse
import json
import logging
import re
import sys
sys.path.append("lib")


import match
from lib.cheetah_bot import CheetahBot




#
# Set up the logger
#
logger = logging
logger.basicConfig(level = logger.INFO, 
	format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s', 
	datefmt='%Y-%m-%dT%H:%M:%S')


#
# Parse our arguments
#
parser = argparse.ArgumentParser(description = "Telegram bot to post cheetah sounds and pictures.")
parser.add_argument("token", type = str, help = "API token")
parser.add_argument("--group_ids", type = str,
	help = "Comma-delimited list of group IDs where this bot can operate.  IDs must be an exact match.")
parser.add_argument("--group_names", type = str,
	help = "Comma-delimited group names which are matched on a substring basis.  Useful when unsure of the group ID (which can then be gotten by debug messages) Matching is done on a substring basis, so be careful!")
parser.add_argument("--actions", type = float, default = 10,
	help = "Used for rate-limiting.  How many actions can we take in a specified period?")
parser.add_argument("--period", type = int, default = 600,
	help = "Used for rate-limiting.  How long is our period in seconds?")
parser.add_argument("--reply-every", type = int, default = 100,
	help = "Every n messages that aren't normally handled by the bot, reply to one.  Disable with -1.")
parser.add_argument("--quotes-file", type = str, required = True,
	help = "Text file that contains things the bot says, one saying per line.")
parser.add_argument("--images-file", type = str, required = True,
	help = "CSV file that contains URLs of images and captions for them.")
args = parser.parse_args()
#print(args) # Debugging


cheetah_bot = CheetahBot()
cheetah_bot.start(args.token, args.quotes_file, args.images_file, 
	args.group_ids, args.group_names, args.actions, args.period, args.reply_every)




