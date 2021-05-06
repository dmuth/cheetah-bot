
#
# This file holds our main Filter class, where functions that don't
# belong in a more specific class will be placed.
#
import logging
import re

logger = logging


class Filter():

	def __init__(self):
		pass


	#
	# Check to see if a user is me
	#
	def userIsMe(self, user, my_id):

		if user.id == my_id:
			return(True)

		return(False)


	#
	# Print out a log message
	#
	def messageIsDm(self, update):

		if not update.effective_chat.title:
			return(True)

		return(False)


	#
	# If the message one we can ignore?
	#
	def messageIsIgnorable(self, update, message, my_id):

		chat_id = update.effective_chat.id
		chat_name = update.effective_chat.title

		if self.botWasRemovedFromGroup(update, message, my_id):
			logger.info(f"I was removed from the chat '{chat_name}' ({chat_id})")
			return(True)

		if message.new_chat_members:
			logger.info("A member was added to chat, ignoring...")

		if message.left_chat_member:
			logger.info("A member was removed from chat, ignoring...")

		return(False)


	#
	# Was this bot just added to a group?
	# 
	def botWasAddedToGroup(self, update, message, my_id):

		if message.new_chat_members:
			for user in message.new_chat_members:
				if self.userIsMe(user, my_id):
					return(True)

		return(False)


	#
	# Was this bot just removed from a group?
	#
	def botWasRemovedFromGroup(self, update, message, my_id):

		if message.left_chat_member:
			if self.userIsMe(message.left_chat_member, my_id):
				return(True)

		return(False)


	#
	# Check to see if the message is exactly "chee" or "/chee".
	#
	def messageIsChee(self, text):
		if text == "chee" or text == "/chee":
			return(True)
		return(False)


	#
	# Check to see if the message contains "chee" or "cheetahs".
	#
	def messageContainsChee(self, text):

		if (re.search(r"\bchee\b", text, re.IGNORECASE)
			or re.search(r"^/chee$", text, re.IGNORECASE)
			or re.search(r"\bchees\b", text, re.IGNORECASE)
			or re.search(r"\bcheet\b", text, re.IGNORECASE)
			or re.search(r"\bcheets\b", text, re.IGNORECASE)
			or re.search(r"\bcheetah\b", text, re.IGNORECASE)
			or re.search(r"\bcheetahs\b", text, re.IGNORECASE)
			):
			return(True)

		return(False)

	#
	# Get our (hardcoded at this time) reply to messages with "chee" in them.
	#
	def messageContainsCheeReply(self, text):
		return("Chee")


