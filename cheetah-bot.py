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
parser = argparse.ArgumentParser(description = "Analyze crawled text")
parser.add_argument("token", type = str, help = "API token")
parser.add_argument("--group_ids", type = str,
	help = "Comma-delimited list of group IDs where this bot can operate.  IDs must be an exact match.")
parser.add_argument("--group_names", type = str,
	help = "Comma-delimited group names which are matched on a substring basis.  Useful when unsure of the group ID (which can then be gotten by debug messages) Matching is done on a substring basis, so be careful!")
parser.add_argument("--actions", type = float, default = 10,
	help = "")
parser.add_argument("--period", type = int, default = 600,
	help = "")
args = parser.parse_args()
print(args) # Debugging


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

	if "fuck" in text:
		return("My virgin ears!")
	elif "shithead" in text:
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
def sendMessage(bot, limiter, chat_id, reply, message_id = None):

	if limiter.action():
		logger.info(f"Sending reply: {reply}, quota_left={limiter.getQuota():.3f}")
		if not message_id:
			bot.send_message(chat_id = chat_id, text = reply)
		else:
			bot.send_message(chat_id = chat_id, text = reply, 
				reply_to_message_id = message_id)

		#
		# Let the group know that we've gone over our quota.
		# Yes, this will only work with one group, even if we are listening in multiple groups.
		#
		if limiter.isQuotaExhausted():
			goToSleep(bot, limiter, chat_id)

	else:
		logger.info("Not sending message, quota currently exhausted.")


#
# This is a wrapper which returns our actual handler.
# The reason for this is so that the variables we need can be in-scope, 
# without having to make them globals.
# This will make it easier to turn these functions into a class in the future.
#
def echo_wrapper(my_id, my_username, allowed_group_ids, allowed_group_names, actions, period):

	#
	# Set up our rate limiter
	#
	limiter = rate_limiter.Limiter(actions = actions, period = period)

	#
	# Our handler that is fired when a message comes in
	#
	def echo_core(update, context):

		# Set some defaults
		text = "(No text, sticker/file/group message?)"
		reply = ""
		reply_to_user = False

		# Filter newlines out of our message for logging and matching purposes
		message = update.message
		if update.message.text:
			text = update.message.text.replace("\r", " ").replace("\n", " ")

		logger.info(f"New Message: chat_id={update.effective_chat.id}, text={text[0:30]}...")
		#logger.info(f"Update: {update}") # Debugging
		#logger.info(f"Message: {message}") # Debugging
		#logger.info(f"Effective chat: {update.effective_chat}") # Debugging

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
			reply_to_user = True
			logger.info("String 'chee' detected")

		#
		# If the message wasn't to the bot, and we're not replying to a user, stop.
		#
		if not reply_to_user:
			if not doesUserMatch(my_id, my_username, update.message, text):
				return(None)

		#
		# I'm not thrilled about calling checkForFoulLanguage() twice, but Python
		# doesn't let me do "if (value = func())" syntax like other languages do.
		# Once this goes into a class, I can have the function just set a classwide value instead.
		#
		if checkForFoulLanguage(update, text):
			reply = checkForFoulLanguage(update, text)
			logger.info("Profanity detected")

		# Reply of last resort (replace with random text or image in the future)
		if not reply:
			reply = f"Reply: {update.message.text}"

		#if not reply_to_user:
		#	sendMessage(context.bot, limiter, chat_id, reply)
		#else:
		#	sendMessage(context.bot, limiter, chat_id, reply, message_id = message.message_id)
		sendMessage(context.bot, limiter, chat_id, reply, message_id = message.message_id)
			

	return(echo_core)


#
# Our main entrypoint
#
def main(args):

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
	cb = echo_wrapper(my_id, my_username, allowed_group_ids, allowed_group_names, args.actions, args.period)
	echo_handler = MessageHandler(Filters.all, cb)

	dispatcher.add_handler(echo_handler)

	updater.start_polling()


#
# Start the bot!
# 
main(args)



