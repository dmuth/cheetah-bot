

import logging
import time

logger = logging


#
# This class is used to do rate limiting on the basis of a certain amount of actions per period of time.
#
class Limiter():

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


	def __init__(self, actions = 10, period = 600):

		self.actions = actions
		self.period = period
		self.prev_time = time.time()
		self.quota = actions

		if self.actions < 1:
			raise Exception(f"Actions must be at least 1. ({self.actions} was provided.)")

		logger.info(f"Limiter initialized with {actions} actions per period of {period} seconds. Quota = {self.quota}, replenished at {actions/period:.3f}/sec.")


	#
	# Perform an action as long as our quota is at least 1.
	#
	# True is returned if we have the quota to do that action, false otherwise.
	#
	def action(self) -> bool:

		current_time = time.time()
		elapsed = current_time - self.prev_time
		self.prev_time = current_time

		# Replenish the quota based on how much time has elapsed
		self.quota += elapsed * ( self.actions / self.period )

		# Don't let our quota exceed the max
		if self.quota > self.actions:
			self.quota = self.actions

		#print(f"Quota left: {self.quota}") # Debugging
		
		if self.quota < 1:
			# Not enough quota to do that
			return(False)

		# We have enough quota. Deduct 1 and proceed.
		self.quota -= 1
		return(True)


	#
	# Return our current quota.
	#
	def getQuota(self) -> float:
		return(self.quota)


