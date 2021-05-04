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
import time
import traceback
sys.path.append("lib")

import telegram
from telegram.error import TelegramError
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters

import match
from lib.counters import Counters
from lib.filter.filter import Filter
from lib.filter.profanity import Profanity
from lib.match import Match
from lib.rate_limiters import RateLimiters
from lib.replies import Replies
from lib.sleep_wake import SleepWake
from lib.cheetah_bot import CheetahBot


cheetah_bot = CheetahBot()


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






#
# Respond to a /start command
#
def start(update, context):
	logger.info(f"chat_id: {update.effective_chat.id}, text={text}")
	context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")



#
# This is a wrapper which returns our actual handler.
# The reason for this is so that the variables we need can be in-scope, 
# without having to make them globals.
# This will make it easier to turn these functions into a class in the future.
#
def echo_wrapper(my_id, my_username, allowed_group_ids, allowed_group_names, actions, period, reply_every_n,
	replies):

	global cheetah_bot

	counters = Counters(reply_every_n)
	filter = Filter()
	match = Match()
	profanity = Profanity()
	rate_limiters = RateLimiters(actions, period)
	sleep_wake = SleepWake()


	#
	# Our handler that is fired when a message comes in
	#
	def echo_core(update, context):

		# Set some defaults
		reply = ""

		# Filter newlines out of our message for logging and matching purposes
		message = update.message
		text = ""
		if update.message.text:
			text = update.message.text.replace("\r", " ").replace("\n", " ")

		# How old is the message?
		age = time.time() - message.date.timestamp()

		logger.info(f"New Message: age={age:.3f}, chat_id={update.effective_chat.id}, text={text[0:30]}...")
		#logger.info(f"Update: {update}") # Debugging
		#logger.info(f"Message: {message}") # Debugging
		#logger.info(f"Effective chat: {update.effective_chat}") # Debugging

		# Bail if the message is too old, otherwise we risk spamming groups after a hiatus
		if age > 10:
			logger.info(f"Message is {age} > 10 seconds old, ignoring.")
			return(None)


		# Was this a bot add/remove?
		if filter.messageIsIgnorable(update, message, my_id):
			return(None)

		# Was this a DM?
		if filter.messageIsDm(update):
			logger.info("This is a DM, bailing out (for now...)")
			text = "You must message me in an approved group."
			context.bot.send_message(chat_id = update.effective_chat.id, text = text)
			return(None)

		#
		# Bail out if we're not in an allowed group
		#
		chat_id = update.effective_chat.id
		chat_name = update.effective_chat.title
		if not match.doesGroupMatch(allowed_group_ids, allowed_group_names, chat_id, chat_name):
			return(None)

		#
		# See if anyone in the chat said "cheetah" or "chee"
		#
		if filter.messageContainsChee(text):
			reply = filter.messageContainsCheeReply(text)
			logger.info("String 'chee' detected")

		#
		# I'm not thrilled about calling checkForFoulLanguage() twice, but Python
		# doesn't let me do "if (value = func())" syntax like other languages do.
		# Once this goes into a class, I can have the function just set a classwide value instead.
		#
		if profanity.hasFoulLanguage(update, text):
			reply = profanity.getReply()
			logger.info("Profanity detected")

		#
		# Get our rate limiter for this chat
		# 
		limiter = rate_limiters.getRateLimiter(chat_id)

		#
		# If the message wasn't to the bot, and we're not replying to a user, stop.
		#
		if not reply:
			if not match.doesUserMatch(my_id, my_username, update.message, text):
				#
				# See if we should reply and do so.
				#
				should_reply = counters.update(chat_id)
				if should_reply:
					cheetah_bot.sendRandomReply(context.bot, limiter, sleep_wake, replies, chat_id,
						message_id = message.message_id)
				return(None)

		#
		# If we already have a reply, then send it out.
		# Otherwise, we have no idea what the user is talking about, so let's just
		# grab a random string of text or URL.
		#
		if reply:
			cheetah_bot.sendMessage(context.bot, limiter, sleep_wake, chat_id, reply = reply, 
				message_id = message.message_id)
		else:
			cheetah_bot.sendRandomReply(context.bot, limiter, sleep_wake, replies, chat_id, 
				message_id = message.message_id)


	return(echo_core)



#
# Our main entrypoint
#
def main(args):

	#print(args)
	global cheetah_bot

	replies = Replies(args.quotes_file, args.images_file)

	bot = telegram.Bot(token = args.token)
	logger.info(f"Successfully authenticated! {bot.get_me()}")
	my_username = bot.get_me().username
	my_id = bot.get_me().id
	logger.info(f"My usernamne: {my_username}, My ID: {my_id}")

	allowed_group_ids = cheetah_bot.getAllowedIds(args.group_ids)
	logger.info(f"Allowed Group IDs: {allowed_group_ids}")
	allowed_group_names = cheetah_bot.getAllowedIds(args.group_names)
	logger.info(f"Allowed Group Names: {allowed_group_names}")

	updater = Updater(token = args.token)
	dispatcher = updater.dispatcher

	#
	# Catch errors
	#
	dispatcher.add_error_handler(cheetah_bot.errorHandler)

	#
	# Uncomment this if I ever want a /start command for some reason.
	#
	#start_handler = CommandHandler('start', start)
	#dispatcher.add_handler(start_handler)

	#
	# We're just gonna reply to everything.
	#
	cb = echo_wrapper(my_id, my_username, allowed_group_ids, allowed_group_names, 
		args.actions, args.period, args.reply_every, replies)
	echo_handler = MessageHandler(Filters.all, cb)

	dispatcher.add_handler(echo_handler)

	updater.start_polling()


#
# Start the bot!
# 
main(args)



