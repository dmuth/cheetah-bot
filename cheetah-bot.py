#!/usr/bin/env python3
# Vim: :set softtabstop=0 noexpandtab tabstop=8 
#
# Telegram bot to repsond to a few messages in groups.
#


import argparse
import json
import logging
import random
import re
import pathlib
import sys
import time
import threading
import traceback
sys.path.append("lib")

import telegram
from telegram.error import TelegramError
from telegram.ext import Updater
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler, MessageHandler, Filters

import match
from lib.match import Match
from lib.limiter import Limiter
from lib.filter.filter import Filter
from lib.filter.profanity import Profanity


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
parser.add_argument("--reply-every-n-messages", type = int, default = 100,
	help = "Every n messages that aren't normally handled by the bot, reply to one.  Disable with -1.")
parser.add_argument("--quotes-file", type = str, required = True,
	help = "Text file that contains things the bot says, one saying per line.")
parser.add_argument("--images-file", type = str, required = True,
	help = "CSV file that contains URLs of images and captions for them.")
args = parser.parse_args()
#print(args) # Debugging


#
# Handle our errors
#
def errorHandler(update: object, context: CallbackContext):

	error_string = str(context.error)

	if "terminated by other getUpdates request" in error_string:
		logger.warning("Looks like another instance of this bot is running. Stop doing that.")

	else:
		logger.error(msg="Exception while handling an update:", exc_info=context.error)

	#
	# Based on an example at 
	# https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/errorhandlerbot.py#L30
	#
	#errors = traceback.format_exception(None, context.error, context.error.__traceback__)
	#error= ''.join(errors)
	#logger.info(error)



#
# Split up our comma-delimited list of IDs, and filter out empty strings.
#
def getAllowedIds(group_ids):

	ids = group_ids.split(",")
	retval = [ id for id in ids if id != "" ]
	return(retval)


#
# Respond to a /start command
#
def start(update, context):
	logger.info(f"chat_id: {update.effective_chat.id}, text={text}")
	context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


#
# Check to see if the message contains "chee" or "cheetahs".
#
def messageContainsChee(text):

	#if (re.search(r"\bchee\b", text)
	if (re.search(r"\bchee\b", text, re.IGNORECASE)
		or re.search(r"^/chee$", text, re.IGNORECASE)
		or re.search(r"\bchees\b", text, re.IGNORECASE)
		or re.search(r"\bcheet\b", text, re.IGNORECASE)
		or re.search(r"\bcheets\b", text, re.IGNORECASE)
		or re.search(r"\bcheetah\b", text, re.IGNORECASE)
		):
		return("Chee")

	return(None)


#
# This flag is set when the bot reaches a fully awake state (aka the queue is full)
# Going to sleep sets this to false, the queue being full again sets this to true.
# The reason behind this flag is so that sleep and wake messages are only printed ONCE
# at each extreme, instead of all the time of the bot sees regular traffic that keeps
# its queue partially filled.
#
# I hate that this is global.  When this bot is converted to a class, this will be addressed.
#
was_fully_awake = True


#
# Our queue is exhausted so we're going to tweak the was_fully_awake flag,
# print a sleep message (if was_fully_awake was full), and schedule a callback
# for when the bot should be fully awake.
#
def goToSleep(bot, limiter, chat_id):

	global was_fully_awake

	if was_fully_awake:
		bot.send_message(chat_id = chat_id, text = "I feel asleep.")

	was_fully_awake = False

	threading.Timer(limiter.getTimeUntilQuotaFull(), 
		wakeUp, args = (bot, limiter, chat_id,)).start()


#
# Fired $period seconds after the queue was last empty and the bot went to sleep.
# This will check to see if the queue is actually full, as the bot may have been pinged a few
# times while the queue refilled.  As such, the announcement will go out only if the 
# bot is "fully rested" aka has a full queue.
#
def wakeUp(bot, limiter, chat_id):

	global was_fully_awake

	logger.info(f"Thread: Firing callback! chat_id={chat_id} quota_left={limiter.getQuota():.3f}")
	if limiter.isQuotaFull():
		logger.info(f"Thread: Queue is full, sending a message to the channel! chat_id={chat_id}")
		bot.send_message(chat_id = chat_id, text = "I'm back and fully rested!  Did ya miss chee?")
		was_fully_awake = True


#
# Send a message in a way that honors our rate limiter's quota.
#
def sendMessage(bot, limiter, chat_id, reply = None, image_url = None, caption = None, message_id = None):

	if limiter.action():

		if reply:
			logger.info(f"Sending reply: {reply}, quota_left={limiter.getQuota():.3f}")
			if not message_id:
				bot.send_message(chat_id = chat_id, text = reply)
			else:
				bot.send_message(chat_id = chat_id, text = reply, 
					reply_to_message_id = message_id)

		elif image_url:
			logger.info(f"Sending reply: {image_url}, quota_left={limiter.getQuota():.3f}")
			if not message_id:
				bot.send_photo(chat_id = chat_id, photo = image_url, caption = caption)
			else:
				bot.send_photo(chat_id = chat_id, photo = image_url, caption = caption,
					reply_to_message_id = message_id)

		else:
			raise Exception(f"Not sure what to send with a message that has no text or URL")


		#
		# Let the group know that we've gone over our quota.
		# Yes, this will only work with one group, even if we are listening in multiple groups.
		#
		if limiter.isQuotaExhausted():
			goToSleep(bot, limiter, chat_id)

	else:
		logger.info(f"Not sending message, quota currently exhausted. quota_left={limiter.getQuota():.3f}")


#
# Return a random cheetah noise.
#
def getRandomMessageText(replies):
	return(random.choice(replies))


#
# Return a random image URL and its caption
#
def getRandomMessageImage(replies):

	retval = {}

	reply = random.choice(replies)
	retval["url"] = reply[0]
	retval["caption"] = reply[1] + "\n\n" + reply[0]

	return(retval)


#
# Figure out which reply function to use, get a reply, and send it off!
#
def sendRandomReply(bot, limiter, chat_id, message_id, quotes, images):

	if random.randint(0, 1):
		reply = getRandomMessageText(quotes)
		sendMessage(bot, limiter, chat_id, reply = reply, message_id = message_id)
	else:
		reply = getRandomMessageImage(images)
		sendMessage(bot, limiter, chat_id, image_url = reply["url"], caption = reply["caption"],
			message_id = message_id)


#
# Keeps track of how many messages that AREN'T for the bot to follow up on are
# sent to each group, so that we can then reply every so often.
#
chat_counters = {}

#
# Keep track of how many messages in each group and return if we should reply
#
def updateCounter(chat_id, reply_every_n) -> bool:

	# If we're not using this feature, bail out
	if reply_every_n < 0:
		return(False)

	if not chat_id in chat_counters:
		chat_counters[chat_id] = 0

	chat_counters[chat_id] += 1

	if chat_counters[chat_id] >= reply_every_n:
		logger.info(f"Counter for chat {chat_id} >= {reply_every_n}. Resetting and returning true!")
		chat_counters[chat_id] = 0
		return(True)

	logger.info(f"Counter for chat {chat_id}: {chat_counters[chat_id]} < {reply_every_n}. No reply this time.")
	return(False)


#
# Dictionary of limiters for each chat ID
#
limiters = {}

#
# Create the rate limiter for the current group, then return it.
#
def getRateLimiter(chat_id, actions, period):

	if not chat_id in limiters:
		limiters[chat_id] = Limiter(actions = actions, period = period)
		
	return(limiters[chat_id])


#
# This is a wrapper which returns our actual handler.
# The reason for this is so that the variables we need can be in-scope, 
# without having to make them globals.
# This will make it easier to turn these functions into a class in the future.
#
def echo_wrapper(my_id, my_username, allowed_group_ids, allowed_group_names, actions, period, reply_every_n,
	quotes, images):

	filter = Filter()
	match = Match()
	profanity = Profanity()

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
		if messageContainsChee(text):
			reply = messageContainsChee(text)
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
		limiter = getRateLimiter(chat_id, actions, period)

		#
		# If the message wasn't to the bot, and we're not replying to a user, stop.
		#
		if not reply:
			if not match.doesUserMatch(my_id, my_username, update.message, text):
				#
				# See if we should reply and do so.
				#
				should_reply = updateCounter(chat_id, reply_every_n)
				if should_reply:
					sendRandomReply(context.bot, limiter, chat_id, 
						message_id = message.message_id,
						quotes = quotes, images = images)
				return(None)

		#
		# If we already have a reply, then send it out.
		# Otherwise, we have no idea what the user is talking about, so let's just
		# grab a random string of text or URL.
		#
		if reply:
			sendMessage(context.bot, limiter, chat_id, reply = reply, 
				message_id = message.message_id)
		else:
			sendRandomReply(context.bot, limiter, chat_id, 
				message_id = message.message_id,
				quotes = quotes, images = images)


	return(echo_core)


#
# Read our quotes and return them in a list
#
def readQuotes(quotes_file) -> list:

	quotes = pathlib.Path.cwd() / quotes_file
	if not quotes.exists():
		raise Exception(f"Quotes file {quotes} does not exist!")
	if not quotes.is_file():
		raise Exception(f"Quotes file {quotes} exists but is not a file!")
	quotes = quotes.read_text()
	quotes = quotes.splitlines()

	return(quotes)


#
# Read our list of URLs and return them and their captions in a list.
#
def readUrls(images_file) -> list:

	#
	# Read our URLs and captions for them.
	# 
	images_file = pathlib.Path.cwd() / args.images_file
	if not images_file.exists():
		raise Exception(f"URLs file {images_file} does not exist!")
	if not images_file.is_file():
		raise Exception(f"URLs file {images_file} exists but is not a file!")
	images_file_contents = images_file.read_text()

	#
	# Separate the URL from the (optional) caption.
	#
	images = []
	for line in images_file_contents.splitlines():
		fields = line.split(",", 1)
		if fields[0] == "url":
			continue
		images.append(fields)

	return(images)


#
# Our main entrypoint
#
def main(args):

	print(args)

	quotes = readQuotes(args.quotes_file)
	images = readUrls(args.images_file)

	bot = telegram.Bot(token = args.token)
	logger.info(f"Successfully authenticated! {bot.get_me()}")
	my_username = bot.get_me().username
	my_id = bot.get_me().id
	logger.info(f"My usernamne: {my_username}, My ID: {my_id}")

	allowed_group_ids = getAllowedIds(args.group_ids)
	logger.info(f"Allowed Group IDs: {allowed_group_ids}")
	allowed_group_names = getAllowedIds(args.group_names)
	logger.info(f"Allowed Group Names: {allowed_group_names}")

	updater = Updater(token = args.token)
	dispatcher = updater.dispatcher

	#
	# Catch errors
	#
	dispatcher.add_error_handler(errorHandler)

	#
	# Uncomment this if I ever want a /start command for some reason.
	#
	#start_handler = CommandHandler('start', start)
	#dispatcher.add_handler(start_handler)

	#
	# We're just gonna reply to everything.
	#
	cb = echo_wrapper(my_id, my_username, allowed_group_ids, allowed_group_names, 
		args.actions, args.period, args.reply_every_n_messages, 
		quotes = quotes, images = images)
	echo_handler = MessageHandler(Filters.all, cb)

	dispatcher.add_handler(echo_handler)

	updater.start_polling()


#
# Start the bot!
# 
main(args)



