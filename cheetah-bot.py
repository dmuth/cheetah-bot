#!/usr/bin/env python3
# Vim: :set softtabstop=0 noexpandtab tabstop=8 
#
# Telegram bot to repsond to a few messages in groups.
#


import argparse
import json
import logging
import traceback

import telegram
from telegram.error import TelegramError
from telegram.ext import Updater
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler, MessageHandler, Filters


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
parser.add_argument("--group_id", type = str, nargs = "+",
	help = "Comma-delimited list of group IDs where this bot can operate.  Matching is done on a substring basis because Telegram does weird things with IDs.  Be careful!")
parser.add_argument("--group_name", type = str, nargs = "+",
	help = "0 or more group names which are matched on a substring basis.  Useful when unsure of the group ID (which can then be gotten by debug messages)")
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
			if id in str(group_id):
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
		logger.info(f"Chat id {chat_id} not found in allowlist, trying chat title...")

		if not doesGroupNameMatch(group_names, chat_name):
			logger.info(f"Chat title {chat_name} not found in allowlist, stopping here!")
			return(None)
		else:
			logger.info(f"Chat title {chat_name} found in allowlist, continuing!")

	else:
		logger.info(f"Chat id {chat_id} found in allow list, continuing!")

	return(True)


#
# Was this message to me, or a reply to me?
#
def doesUserMatch(message, text):

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
# Send a message right back to the sender
# 
def echo(update, context):

	text = "(No text, sticker/file?)"
	message = update.message
	if update.message.text:
		text = update.message.text.replace("\r", " ").replace("\n", " ")

	logger.info(f"New Message: chat_id={update.effective_chat.id}, text={text[0:30]}...")
	#logger.info(f"Update: {update}") # Debugging
	#logger.info(f"Message: {message}") # Debugging
	#logger.info(f"Effective chat: {update.effective_chat}") # Debugging

	if messageIsIgnorable(update, context, message, my_id):
		return(None)

	chat_id = update.effective_chat.id
	chat_name = update.effective_chat.title

	if doesGroupMatch(args.group_id, args.group_name, chat_id, chat_name):
		if doesUserMatch(update.message, text):
			reply = f"Reply: {update.message.text}"
			reply2 = checkForFoulLanguage(update, text)
			if reply2:
				logger.info("Profanity detected")
				reply = reply2

			logger.info(f"Sending reply: {reply}")
			context.bot.send_message(chat_id = chat_id, text = reply)


bot = telegram.Bot(token = args.token)
logger.info(f"Successfully authenticated! {bot.get_me()}")
my_username = bot.get_me().username
my_id = bot.get_me().id
logger.info(f"My usernamne: {my_username}, My ID: {my_id}")

updater = Updater(token = args.token)
dispatcher = updater.dispatcher

#start_handler = CommandHandler('start', start)
#dispatcher.add_handler(start_handler)

#
# We're just gonna reply to everything.
#
echo_handler = MessageHandler(Filters.all, echo)
dispatcher.add_handler(echo_handler)

#
# Catch errors
#
dispatcher.add_error_handler(errorHandler)

updater.start_polling()


