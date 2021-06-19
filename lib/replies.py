
import logging
import pathlib
import random
import time

logger = logging


class Replies():

	# Array of things for the bot to say
	posts = []

	# Dictionary of stats on posts 
	stats = {}
	stats["quotes"] = 0
	stats["images"] = 0
	stats["total"] = 0


	def __init__(self, posts_file):
		self._readFile(posts_file)


	#
	# Return our stats.
	#
	def getStats(self):
		return(self.stats)


	#
	# Return a random message
	#
	def getRandomMessage(self):

		retval = {}

		reply = random.choice(self.posts)

		if "url" in reply:
			retval["url"] = reply["url"]

			if "caption" in reply:
				retval["caption"] = reply["caption"] + "\n\n" + reply["url"]

		else:
			retval["caption"] = reply["caption"]

		return(retval)


	#
	# Read our file and populate our list with Captions and (optionally) URLs
	#
	def _readFile(self, posts_file) -> list:

		#
		# Read our URLs and captions for them.
		# 
		posts = pathlib.Path.cwd() / posts_file
		if not posts.exists():
			raise Exception(f"URLs file {posts_file} does not exist!")
		if not posts.is_file():
			raise Exception(f"URLs file {posts_file} exists but is not a file!")
		posts_file_contents = posts.read_text()

		#
		# Separate the URL from the (optional) caption.
		#
		self.posts = []
		for line in posts_file_contents.splitlines():
			fields = line.split(",", 1)
			if fields[0] == "url":
				continue

			#
			# Add a blank caption by default because SO much stuff will break, and it's
			# just not worth adding if/thens all over the place.
			#
			# In the future, I might consider encapsulating posts/quotes in a class.
			#
			data = {}
			data["caption"] = ""

			if fields[0]:
				data["url"] = fields[0]

			if len(fields) > 1 and fields[1]:
				data["caption"] = fields[1]
			else:
				logger.warn(f"Unable to find a caption in line: {line}!  Adding a blank one.")

			if "url" in data:
				self.stats["images"] += 1
				self.stats["total"] += 1
			elif "caption" in data:
				self.stats["quotes"] += 1
				self.stats["total"] += 1

			self.posts.append(data)

		logger.info(f"Read {len(self.posts)} lines from {posts_file}.  It contains {self.stats['images']} images and {self.stats['quotes']} quotes.")


