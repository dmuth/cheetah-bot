

import logging
from rate_limiter import RateLimiter

logger = logging


#
# This class holds 1 or more rate limiters, 1 per channel that it is in.
#
class RateLimiters():


	#
	# Dictionary of limiters for each chat ID
	#
	limiters = {}

	def __init__(self, actions, period):
		self.actions = actions
		self.period = period


	#
	# Create the rate limiter for the current group, then return it.
	#
	def getRateLimiter(self, chat_id):

		if not chat_id in self.limiters:
			self.limiters[chat_id] = RateLimiter(actions = self.actions, period = self.period)
		
		return(self.limiters[chat_id])



