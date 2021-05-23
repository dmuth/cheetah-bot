

import logging
import threading

logger = logging


#
# This class holds code that relates to whether to put the bot to sleep or wake it up
# in each group.  If either happens, a message is printed in the group.
#
class SleepWake():

	#
	# A status of the bot in various chat_ids.
	# If there's no entry, it assumed that the bot was previously fully awake.
	#
	was_fully_awake = {}

	#
	# Is the bot asleep for a given chat?
	# I expect this will eventually replace was_fully_awake
	#
	is_asleep = {}


	def __init__(self):
		pass
		self.was_fully_awake = {}
		self.is_asleep = {}


	#
	# Our quota is exhausted so we're going to tweak the was_fully_awake flag,
	# print a sleep message (if was_fully_awake was full), and schedule a callback
	# for when the bot should be fully awake.
	#
	def goToSleep(self, bot, limiter, chat_id):

		#
		# If not present in the status dictionary, the bot HAD to have 
		# been fully awake, because that this means this function was 
		# not previously run for this group.
		#
		if not chat_id in self.was_fully_awake:
			self.was_fully_awake[chat_id] = True

		#
		# If (and only if, so as to prevent flapping!) we were previously fully awake,
		# tell the group we're going to sleep, Metal Gear style.
		#
		if self.was_fully_awake[chat_id]:
			bot.send_message(chat_id = chat_id, text = "I feel asleep.")

		self.was_fully_awake[chat_id] = False
		self.is_asleep[chat_id] = True

		threading.Timer(limiter.getTimeUntilQuotaFull(), 
			self.wakeUp, args = (bot, limiter, chat_id,)).start()


	#
	# Fired $period seconds after the quota was last empty and the bot went to sleep.
	# This will check to see if the quota is actually full, as the bot may have been pinged a few
	# times while the quota refilled.  As such, the announcement will go out only if the 
	# bot is "fully rested" aka has a full quota.
	#
	def wakeUp(self, bot, limiter, chat_id):

		logger.info(f"Thread: Firing callback! chat_id={chat_id} quota_left={limiter.getQuota():.3f}")
		logger.info(f"Sleep/Wake chat_id={chat_id}, overall status: {self.was_fully_awake}")

		# TODO: In the future, I should consider pulling out the quota check and was_fully_awake.
		if limiter.isQuotaFull():
			logger.info(f"Thread: Quota is full, sending a message to the channel! chat_id={chat_id}")
			bot.send_message(chat_id = chat_id, 
				text = "I'm back and fully rested!  Did ya miss chee?")

			self.was_fully_awake[chat_id] = True
	
		# Mark ourself as awake now.	
		self.is_asleep[chat_id] = False


	#
	# Check to see if a chat is asleep.
	#
	def isAsleep(self, chat_id):

		#
		# If not found, default state is awake.
		#
		if not chat_id in self.is_asleep:
			self.is_asleep[chat_id] = False
	
		return(self.is_asleep[chat_id])

