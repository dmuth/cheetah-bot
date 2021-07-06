

import logging
import random
import threading
import time

from counters import Counters
from filter.filter import Filter
from filter.profanity import Profanity
from match import Match
from rate_limiters import RateLimiters
from replies import Replies
from sleep_wake import SleepWake

import telegram
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.ext import Updater
from telegram.error import TelegramError

logger = logging


#
# Our main Cheetah Bot class.
#
class CheetahBot():

	counters = None
	filter = None
	match = None
	profanity = None
	rate_limiters = None
	replies = None 
	sleep_wake = None

	about_text = ""
	about_text = """I am Cheetah Bot -- a cybernetic organism: living spots and fur over a metal endoskeleton.\n
My mission is to chirp at you.  Add me to a Telegram group for cheetah sounds and pictures.\n
My directives are as follows:\n
{chee_text}
- I notice profanity and respond to it.
- If you @ me, I respond with cheetah pictures and noises.
- I have a quota of sending {actions} messages per {period} seconds.
{post_every_text}
- I can say {stats_total} different things, choosing from {stats_quotes} quotes and {stats_images} pictures.

@ me with 'help' to see this message again.

Made with 🙀 by Leopards.
"""

	def __init__(self):
		pass


	#
	# Our main entry point to start bot.  This function will never exit.
	#
	def start(self, token, posts_file, group_ids, group_names,
		actions, period, post_every, profanity_reply = False):

		self.counters = Counters(post_every)
		self.filter = Filter()
		self.match = Match()
		self.profanity = Profanity(ignore = not profanity_reply)
		self.rate_limiters = RateLimiters(actions, period)
		self.replies = Replies(posts_file)
		self.sleep_wake = SleepWake()

		post_every_text = ""
		if post_every:
			post_every_text = f"- I reply to the last message every {post_every} messages posted."

		chee_text = "- I respond to messages that are just '/chee'."

		stats = self.replies.getStats()

		self.about_text = self.about_text.format(actions = actions, period = period, 
			post_every_text = post_every_text, chee_text = chee_text, 
			stats_total = stats["total"], stats_quotes = stats["quotes"], stats_images = stats["images"]
			)
		#print("DEBUG: ", self.about_text) # Debugging

		self.allowed_group_ids = self.getAllowedIds(group_ids)
		self.allowed_group_names = self.getAllowedIds(group_names)
		if self.allowed_group_ids or self.allowed_group_names:
			logger.info(f"Allowed Group IDs: {self.allowed_group_ids}")
			logger.info(f"Allowed Group Names: {self.allowed_group_names}")
		else:
			logger.info("No Group IDs or Group Names specified, the bot is open to ALL groups!")

		bot = telegram.Bot(token = token)
		logger.info(f"Successfully authenticated! {bot.get_me()}")
		self.my_username = bot.get_me().username
		self.my_id = bot.get_me().id
		logger.info(f"My usernamne: {self.my_username}, My ID: {self.my_id}")

		updater = Updater(token = token)
		dispatcher = updater.dispatcher

		#
		# Catch errors
		#
		dispatcher.add_error_handler(self.errorHandler)

		#
		# We're just gonna reply to everything.
		#
		echo_handler = MessageHandler(Filters.all, self.echo)
		dispatcher.add_handler(echo_handler)

		updater.start_polling()



	#
	# Our handler that is fired when a message comes in
	#
	def echo(self, update, context):

		results = self.echoParseMessage(update, context)

		if not results:
			return(None)

		(message, text, chat_id) = results[0], results[1], results[2]

		try: 
			self.echoComposeReply(context, update, message, text, chat_id)
		except telegram.error.BadRequest as e:
			if "Have no rights to send a message" in str(e):
				logger.warning(f"echo(): Unable to send message to chat_id={chat_id}: {str(e)}")
			else:
				raise(e)


	#
	# Parse our message and figure out if we should reply.
	#
	def echoParseMessage(self, update, context):

		# Set some defaults
		reply = ""

		# Filter newlines out of our message for logging and matching purposes
		message = update.message
		text = ""
		if update.message.text:
			text = update.message.text.replace("\r", " ").replace("\n", " ")

		# How old is the message?
		age = time.time() - message.date.timestamp()

		logger.info(f"New Message: age={age:.3f}, chat_id={update.effective_chat.id}, chat_name='{update.effective_chat.title}', text={text[0:30]}...")
		#logger.info(f"Update: {update}") # Debugging
		#logger.info(f"Message: {message}") # Debugging
		#logger.info(f"Effective chat: {update.effective_chat}") # Debugging

		# Bail if the message is too old, otherwise we risk spamming groups after a hiatus
		if age > 10:
			logger.info(f"Message is {age} > 10 seconds old, ignoring.")
			return(None)

		# Was this a bot add/remove?
		if self.filter.messageIsIgnorable(update, message, self.my_id):
			return(None)

		# Was this a DM?
		if self.filter.messageIsDm(update):
			logger.info("This is a DM, talk about ourself and bail out (for now...)")
			context.bot.send_message(chat_id = update.effective_chat.id, text = self.about_text)
			return(None)

		#
		# Bail out if we're not in an allowed group
		#
		chat_id = update.effective_chat.id
		chat_name = update.effective_chat.title
		if not self.match.doesGroupMatch(self.allowed_group_ids, self.allowed_group_names, 
			chat_id, chat_name):
			return(None)

		return([message, text, chat_id])


	#
	# Compose our reply
	#
	def echoComposeReply(self, context, update, message, text, chat_id):

		reply = ""

		message_to_me = False
		if self.match.doesUserMatch(self.my_id, self.my_username, update.message, text):
			message_to_me = True

		#
		# Announce ourself it added to a group
		#
		#if self.filter.botWasAddedToGroup(update, message, self.my_id):
		#	logger.info(f"I was added to the chat '{chat_name}' ({chat_id}), let's say hi!")
		#	reply = self.about_text

		#
		# Get our rate limiter for this chat
		# 
		limiter = self.rate_limiters.getRateLimiter(chat_id)

		#
		# Did the user ask us for help?
		#
		if message_to_me:
			#
			# Did the user ask us for help?
			#
			if self.filter.messageContainsHelp(text):
				logger.info("User asked us for help, give it.")
				reply = self.about_text

			elif self.filter.messageContainsStats(text):
				logger.info("User wants to know the bot stats")
				reply = self.getStats(limiter)


		#
		# See if anyone in the chat said "/chee"
		#
		if self.filter.messageIsChee(text):
			reply = "chee"
			logger.info("String '/chee' is exact match.")


		#
		# I'm not thrilled about calling checkForFoulLanguage() twice, but Python
		# doesn't let me do "if (value = func())" syntax like other languages do.
		# Once this goes into a class, I can have the function just set a classwide value instead.
		#
		if self.profanity.hasFoulLanguage(update, text):
			reply = self.profanity.getReply()
			logger.info("Profanity detected")


		#
		# If the message wasn't to the bot, and we're not replying to a user, stop.
		#
		if not reply:
			if not message_to_me:
				#
				# See if we should reply and do so.
				#
				should_post = self.counters.update(chat_id)
				if should_post:
					delay = 10
					#delay = 1 # Debugging
					threading.Timer(delay, self.sendRandomMessageFromThread,
						args = (context.bot, limiter, chat_id,)
						).start()
					logger.info(f"We hit our num message threshold for posting, scheduled group post in {delay} seconds...")
				return(None)


		#
		# If we made it here, we're sending SOME kind of reply.
		#

		#
		# If we already have a reply, then send it out.
		# Otherwise, we have no idea what the user is talking about, so let's just
		# grab a random string of text or URL.
		#
		if reply:
			self.sendMessage(context.bot, limiter, chat_id, reply = reply, 
				message_id = message.message_id)
		else:
			self.sendRandomReply(context.bot, limiter, chat_id, 
				message_id = message.message_id)



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

		retval = [ id for id in group_ids if id != "" ]
		return(retval)


	#
	# Figure out which reply function to use, get a reply, and send it off!
	#
	def sendRandomReply(self, bot, limiter, chat_id, message_id):

		reply = self.replies.getRandomMessage()

		if "url" in reply:
			caption = ""
			if "caption" in reply:
				caption = reply["caption"]

			self.sendMessage(bot, limiter, chat_id, 
				image_url = reply["url"], caption = caption,
				message_id = message_id)

		elif "caption" in reply:
			self.sendMessage(bot, limiter, chat_id, 
				reply = reply["caption"], message_id = message_id)

		else:
			logger.warn(f"Reply '{reply}' has neither caption not URL.  Probably a blank line!  I warned you at startup!")


	#
	# Send a random message to the group.
	#
	def sendRandomMessage(self, bot, limiter, chat_id):

		reply = self.replies.getRandomMessage()

		if "url" in reply:
			self.sendMessage(bot, limiter, chat_id, 
				image_url = reply["url"], caption = reply["caption"])
		else:
			self.sendMessage(bot, limiter, chat_id, 
				reply = reply["caption"])


	#
	# Callback to send a random message from a thread, where there was a delay.
	#
	def sendRandomMessageFromThread(self, bot, limiter, chat_id):
		self.sendRandomMessage(bot, limiter, chat_id)



	#
	# Return the current stats for the bot in the current channel.
	#
	def getStats(self, limiter):
		stats = self.replies.getStats()
		retval = (f"I can send {limiter.actions} messages every {limiter.period} seconds."
			+ f"I have {limiter.getQuota()-1:.1f} more messages left in my quota.\n\n"
			+ f"I can say {stats['total']} different things, choosing from {stats['quotes']} quotes and {stats['images']} pictures."
			)

		return(retval)


	#
	# Send a message in a way that honors our rate limiter's quota.
	# All messages are either a reply or an image.
	#
	def sendMessage(self, bot, limiter, chat_id, 
		reply = None, image_url = None, caption = None, message_id = None
		):

		if self.sleep_wake.isAsleep(chat_id):
			logger.info(f"We're asleep, not sending reply to chat {chat_id}...")
			return(None)

		if limiter.action():

			if reply:
				logger.info(f"Sending reply: {reply[0:40]}..., reply_to={message_id} quota_left={limiter.getQuota():.3f}")
				if not message_id:
					bot.send_message(chat_id = chat_id, text = reply)
				else:
					bot.send_message(chat_id = chat_id, text = reply, 
						reply_to_message_id = message_id)

			elif image_url:
				newline = "\n"
				if not message_id:
					bot.send_photo(chat_id = chat_id, photo = image_url, caption = caption)
					logger.info(f"Sending image: {image_url}, caption: {caption.replace(newline, ' ')[0:20]}... quota_left={limiter.getQuota():.3f}")
				else:
					logger.info(f"Sending image: {image_url}, caption: {caption.replace(newline, ' ')[0:20]}... reply_to={message_id} quota_left={limiter.getQuota():.3f}")
					bot.send_photo(chat_id = chat_id, photo = image_url, caption = caption,
						reply_to_message_id = message_id)

			else:
				raise Exception(f"Not sure what to send with a message that is not a reply and doesn't have a URL")


			#
			# Let the group know that we've gone over our quota.
			# Yes, this will only work with one group, even if we are listening in multiple groups.
			#
			if limiter.isQuotaExhausted():
				self.sleep_wake.goToSleep(bot, limiter, chat_id)

		else:
			logger.info(f"Not sending message, quota currently exhausted. quota_left={limiter.getQuota():.3f}")



