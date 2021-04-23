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

import rate_limiter


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
parser.add_argument("--urls-file", type = str, required = True,
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
# Is the group ID from the message present in the allowed list?
#
def doesGroupIdMatch(groups, group_id):

	if groups:
		for id in groups:
			if id == str(group_id):
				return(True)
	return(False)


#
# Is the group name from the message present in the allowed list?
#
def doesGroupNameMatch(groups, group_name):
	if groups:
		for name in groups:
			if name.lower() in group_name.lower():
				return(True)
	return(False)


def doesGroupMatch(group_ids, group_names, chat_id, chat_name):

	if not doesGroupIdMatch(group_ids, chat_id):
		logger.info(f"Chat id '{chat_id}' not found in allowlist, trying chat title...")

		if not doesGroupNameMatch(group_names, chat_name):
			logger.info(f"Chat title '{chat_name}' not found in allowlist, stopping here!")
			return(None)
		else:
			logger.info(f"Chat title '{chat_name}' found in allowlist, continuing!")

	else:
		logger.info(f"Chat id {chat_id} found in allow list, continuing!")

	return(True)


#
# Was this message to me, or a reply to me?
#
def doesUserMatch(my_id, my_username, message, text):

	reply_to = message.reply_to_message

	if reply_to:
		if my_id == reply_to.from_user.id:
			logger.info("This reply was to me!")
			return(True)
		
	if my_username in text:
		logger.info("This message was to me!")
		return(True)

	return(False)

#
# Update our response if there is foul language in the text 
# If not, just return the original reply.
#
def checkForFoulLanguage(update, text):

	if re.search(r"fuck", text, re.IGNORECASE):
		return("Such language!")
	if re.search(r"dammit", text, re.IGNORECASE):
		return("My virgin ears!")
	if re.search(r"sanic\b", text, re.IGNORECASE):
		return("Gotta go fast.")
	if re.search(r"shit\b", text, re.IGNORECASE):
		return("My virgin ears!")
	elif "🖕" in text:
		return("My virgin eyes!")
	elif (update.message.sticker
		and "🖕" in update.message.sticker.emoji):
		return("My virgin eyes!")
	else:
		return(None)


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
# Check to see if a user is me
#
def userIsMe(user, my_id):

	if user.id == my_id:
		return(True)

	return(False)


#
# Was this bot just added to a group?
# 
def botWasAddedToGroup(update, message, my_id):

	if message.new_chat_members:
		for user in message.new_chat_members:
			if userIsMe(user, my_id):
				return(True)

	return(False)


#
# Was this bot just removed from a group?
#
def botWasRemovedFromGroup(update, message, my_id):

	if message.left_chat_member:
		if userIsMe(message.left_chat_member, my_id):
			return(True)

	return(False)


#
# Print out a log message
#
def messageIsDm(update, context):

	if not update.effective_chat.title:
		logger.info("This is a DM, bailing out (for now...)")
		text = "You must message me in an approved group."
		context.bot.send_message(chat_id = update.effective_chat.id, text = text)
		return(True)

	return(False)


#
# If the message one we can ignore?
#
def messageIsIgnorable(update, context, message, my_id):

	chat_id = update.effective_chat.id
	chat_name = update.effective_chat.title

	if botWasAddedToGroup(update, message, my_id):
		logger.info(f"I was added to the chat '{chat_name}' ({chat_id})!")
		return(True)

	if botWasRemovedFromGroup(update, message, my_id):
		logger.info(f"I was removed from the chat '{chat_name}' ({chat_id})")
		return(True)

	if messageIsDm(update, context):
		return(True)

	return(False)


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

	logger.info(f"Thread: Firing callback! quota_left={limiter.getQuota():.3f}")
	if limiter.isQuotaFull():
		logger.info("Thread: Queue is full, sending a message to the channel!")
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
		logger.info("Not sending message, quota currently exhausted.")


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
def sendRandomReply(bot, limiter, chat_id, message_id, quotes, urls):

	if random.randint(0, 1):
		reply = getRandomMessageText(quotes)
		sendMessage(bot, limiter, chat_id, reply = reply, message_id = message_id)
	else:
		reply = getRandomMessageImage(urls)
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
# This is a wrapper which returns our actual handler.
# The reason for this is so that the variables we need can be in-scope, 
# without having to make them globals.
# This will make it easier to turn these functions into a class in the future.
#
def echo_wrapper(my_id, my_username, allowed_group_ids, allowed_group_names, actions, period, reply_every_n,
	quotes, urls):

	#
	# Set up our rate limiter
	#
	limiter = rate_limiter.Limiter(actions = actions, period = period)

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


		# Was this a bot add/remove or a DM?
		if messageIsIgnorable(update, context, message, my_id):
			return(None)

		#
		# Bail out if we're not in an allowed group
		#
		chat_id = update.effective_chat.id
		chat_name = update.effective_chat.title
		if not doesGroupMatch(allowed_group_ids, allowed_group_names, chat_id, chat_name):
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
		if checkForFoulLanguage(update, text):
			reply = checkForFoulLanguage(update, text)
			logger.info("Profanity detected")

		#
		# If the message wasn't to the bot, and we're not replying to a user, stop.
		#
		if not reply:
			if not doesUserMatch(my_id, my_username, update.message, text):
				#
				# See if we should reply and do so.
				#
				should_reply = updateCounter(chat_id, reply_every_n)
				if should_reply:
					sendRandomReply(context.bot, limiter, chat_id, 
						message_id = message.message_id,
						quotes = quotes, urls = urls)
				return(None)

		#
		# If we already have a reply, then send it out.
		# Otherwise, we have no idea what the user is talking about, so let's just
		# grab a random string of text or URL.
		#
		if reply:
			sendMessage(context.bot, limiter, chat_id, reply = reply, 
				message_id = message.message_id,
				quotes = quotes, urls = urls)
		else:
			sendRandomReply(context.bot, limiter, chat_id, 
				message_id = message.message_id,
				quotes = quotes, urls = urls)


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
def readUrls(urls_file) -> list:

	#
	# Read our URLs and captions for them.
	# 
	urls_file = pathlib.Path.cwd() / args.urls_file
	if not urls_file.exists():
		raise Exception(f"URLs file {urls_file} does not exist!")
	if not urls_file.is_file():
		raise Exception(f"URLs file {urls_file} exists but is not a file!")
	urls_file_contents = urls_file.read_text()

	#
	# Separate the URL from the (optional) caption.
	#
	urls = []
	for line in urls_file_contents.splitlines():
		fields = line.split(",", 1)
		if fields[0] == "url":
			continue
		urls.append(fields)

	return(urls)


#
# Our main entrypoint
#
def main(args):

	print(args)

	quotes = readQuotes(args.quotes_file)
	urls = readUrls(args.urls_file)

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
		quotes = quotes, urls = urls)
	echo_handler = MessageHandler(Filters.all, cb)

	dispatcher.add_handler(echo_handler)

	updater.start_polling()


#
# Start the bot!
# 
main(args)



