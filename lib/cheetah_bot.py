

import logging
import random

from telegram.ext import CallbackContext

logger = logging


#
# Our main Cheetah Bot class.
#
class CheetahBot():


	def __init__(self):
		pass


	#
	# Handle our errors
	#
	def errorHandler(self, update: object, context: CallbackContext):

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
	def getAllowedIds(self, group_ids):

		ids = group_ids.split(",")
		retval = [ id for id in ids if id != "" ]
		return(retval)


	#
	# Figure out which reply function to use, get a reply, and send it off!
	#
	def sendRandomReply(self, bot, limiter, sleep_wake, replies, chat_id, message_id):

		if random.randint(0, 1):
			reply = replies.getRandomMessageText()
			self.sendMessage(bot, limiter, sleep_wake, chat_id, 
				reply = reply, message_id = message_id)
		else:
			reply = replies.getRandomMessageImage()
			self.sendMessage(bot, limiter, sleep_wake, chat_id, 
				image_url = reply["url"], caption = reply["caption"],
				message_id = message_id)



	#
	# Send a message in a way that honors our rate limiter's quota.
	#
	def sendMessage(self, bot, limiter, sleep_wake, chat_id, 
		reply = None, image_url = None, caption = None, message_id = None):

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
				sleep_wake.goToSleep(bot, limiter, chat_id)

		else:
			logger.info(f"Not sending message, quota currently exhausted. quota_left={limiter.getQuota():.3f}")



