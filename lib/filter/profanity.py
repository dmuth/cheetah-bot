
import logging
import re

logger = logging


class Profanity():

	def __init__(self):
		pass


	#
	# Our reply in response to foul language
	# 
	reply = ""


	#
	# Update our response if there is foul language in the text 
	#
	def hasFoulLanguage(self, update, text) -> bool:

		if re.search(r"fuck", text, re.IGNORECASE):
			self.reply = "Such language!"
		elif re.search(r"dammit", text, re.IGNORECASE):
			self.reply = "My virgin ears!"
		elif re.search(r"shit\b", text, re.IGNORECASE):
			self.reply = "My virgin ears!"

		elif re.search(r"sonic\b", text, re.IGNORECASE):
			self.reply = "Gotta go fast!"
		elif re.search(r"sanic\b", text, re.IGNORECASE):
			self.reply = "¡ʇsɐɟ oɓ ɐʇʇo⅁"

		elif "🖕" in text:
			self.reply =  "My virgin eyes!"
		elif (update.message.sticker
			and "🖕" in update.message.sticker.emoji):
			self.reply = "My virgin eyes!"

		if self.reply:
			return(True)

		return(False)


	#
	# If we have a reply, return it and clear the value.
	#
	def getReply(self):

		if self.reply:
			reply = self.reply
			self.reply = ""
			return(reply)

		return(None)




