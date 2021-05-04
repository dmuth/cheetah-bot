
import logging
import pathlib
import random
import time

logger = logging


class Counters():

	#
	# Keeps track of how many messages that AREN'T for the bot to follow up on are
	# sent to each group, so that we can then reply every so often.
	#
	chat_counters = {}

	#
	# How often should I reply to messages?
	#
	reply_every_n = None

	def __init__(self, reply_every_n):
		self.reply_every_n = reply_every_n


	#
	# Keep track of how many messages in each group and return if we should reply
	#
	def update(self, chat_id) -> bool:

		# If we're not using this feature, bail out
		if self.reply_every_n < 0:
			return(False)

		if not chat_id in self.chat_counters:
			self.chat_counters[chat_id] = 0

		self.chat_counters[chat_id] += 1

		if self.chat_counters[chat_id] >= self.reply_every_n:
			logger.info(f"Counter for chat {chat_id} >= {self.reply_every_n}. Resetting and returning true!")
			self.chat_counters[chat_id] = 0
			return(True)

		logger.info(f"Counter for chat {chat_id}: {self.chat_counters[chat_id]} < {self.reply_every_n}. No reply this time.")
		return(False)


