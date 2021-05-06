
import logging
import re
import time

logger = logging


class Match():

	def __init__(self):
		pass


	#
	# Is the group ID from the message present in the allowed list?
	#
	def doesGroupIdMatch(self, groups, group_id):

		if groups:
			for id in groups:
				if id == str(group_id):
					return(True)
		return(False)


	#
	# Is the group name from the message present in the allowed list?
	#
	def doesGroupNameMatch(self, groups, group_name):
		if groups:
			for name in groups:
				if name.lower() in group_name.lower():
					return(True)
		return(False)


	#
	# Check both the group name and group ID and see if one matches.
	#
	def doesGroupMatch(self, group_ids, group_names, chat_id, chat_name):

		#
		# If no restrictions were defined, then let any group interact with the bot.
		#
		if (not group_ids) and (not group_names):
			return(True)

		if not self.doesGroupIdMatch(group_ids, chat_id):
			logger.info(f"Chat id '{chat_id}' not found in allowlist, trying chat title...")

			if not self.doesGroupNameMatch(group_names, chat_name):
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
	def doesUserMatch(self, my_id, my_username, message, text):

		reply_to = message.reply_to_message

		if reply_to:
			if my_id == reply_to.from_user.id:
				logger.info("This message was a reply to me!")
				return(True)
		
		if my_username in text:
			logger.info("This message has my username in it!")
			return(True)

		return(False)


	#
	# Does the message have "help" in it?
	#
	def doesMessageHaveHelp(self,text):

		if (re.search(r"\bhelp\b", text, re.IGNORECASE)):
			logger.info("Message is asking for help!")
			return(True)

		return(False)




