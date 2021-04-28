
#
# This file holds our main Filter class, where functions that don't
# belong in a more specific calss will be placed.
#
import logging
import re

logger = logging


class Filter():

	def __init__(self):
		pass


	#
	# Print out a log message
	#
	def messageIsDm(self, update, context):

		if not update.effective_chat.title:
			logger.info("This is a DM, bailing out (for now...)")
			text = "You must message me in an approved group."
			context.bot.send_message(chat_id = update.effective_chat.id, text = text)
			return(True)

		return(False)


	#
	# If the message one we can ignore?
	#
	def messageIsIgnorable(self, update, context, message, my_id):

		chat_id = update.effective_chat.id
		chat_name = update.effective_chat.title

		if self.botWasAddedToGroup(update, message, my_id):
			logger.info(f"I was added to the chat '{chat_name}' ({chat_id})!")
			return(True)

		if self.botWasRemovedFromGroup(update, message, my_id):
			logger.info(f"I was removed from the chat '{chat_name}' ({chat_id})")
			return(True)

		if self.messageIsDm(update, context):
			return(True)

		return(False)


	#
	# Was this bot just added to a group?
	# 
	def botWasAddedToGroup(self, update, message, my_id):

		if message.new_chat_members:
			for user in message.new_chat_members:
				if userIsMe(user, my_id):
					return(True)

		return(False)


	#
	# Was this bot just removed from a group?
	#
	def botWasRemovedFromGroup(self, update, message, my_id):

		if message.left_chat_member:
			if userIsMe(message.left_chat_member, my_id):
				return(True)

		return(False)



