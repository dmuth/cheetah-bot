

import logging
import time

logger = logging


#
# This class is used to do rate limiting on the basis of a certain amount of actions per period of time.
#
class RateLimiter():

	# How many actions can we perform per period?
	actions = 10

	# How long is a period in seconds?
	period = 60

	# Time when the last limit check was made
	prev_time = 0
	
	#
	# How much of a quota do we have left?  
	# Every action subtracts 1 from this value.
	#
	quota = 0

	# How much the queue fills per second.
	fill_rate = 0


	def __init__(self, actions = 10, period = 600):

		self.actions = actions
		self.period = period
		self.prev_time = time.time()
		self.quota = actions
		self.fill_rate = actions / period

		if self.actions < 1:
			raise Exception(f"Actions must be at least 1. ({self.actions} was provided.)")

		logger.info(f"Limiter initialized with {actions} actions per period of {period} seconds. Quota = {self.quota}, replenished at {self.fill_rate:.3f}/sec.")

	#
	# Update the current value of our quota based on how much 
	# time has elapsed since when we checked last.
	#
	def _updateQuota(self):
		current_time = time.time()
		elapsed = current_time - self.prev_time
		self.prev_time = current_time

		# Replenish the quota based on how much time has elapsed
		self.quota += elapsed * self.fill_rate

		# Don't let our quota exceed the max
		if self.quota > self.actions:
			self.quota = self.actions


	#
	# Perform an action as long as our quota is at least 1.
	#
	# True is returned if we have the quota to do that action, false otherwise.
	#
	def action(self) -> bool:

		self._updateQuota()
		#print(f"Quota left: {self.quota}") # Debugging
		
		if self.quota < 1:
			# Not enough quota to do that
			return(False)

		# We have enough quota. Deduct 1 and proceed.
		self.quota -= 1
		return(True)


	#
	# Return our current quota value.
	#
	def getQuota(self) -> float:
		self._updateQuota()
		return(self.quota)


	#
	# Return if the quota is full or not.
	#
	def isQuotaFull(self) -> bool:
		self._updateQuota()
		return(self.quota == self.actions)


	#
	# Check to see if the quota is exhausted ATM.
	#
	def isQuotaExhausted(self) -> bool:
		if self.quota < 1:
			return(True)
		return(False)


	#
	# Return how many seconds until the quota is full.
	# This is really just a silly abstraction to make the calling code easier to read.
	#
	def getTimeUntilQuotaFull(self) -> float:
		return(self.period)


