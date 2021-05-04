
import logging
import pathlib
import random
import time

logger = logging


class Replies():

	# Array of quotes for the bot to say
	quotes = []

	# Array of URLs and comments
	images = []


	def __init__(self, quotes_file, images_file):
		self._readQuotes(quotes_file)
		self._readUrls(images_file)


	#
	# Return a random cheetah noise.
	#
	def getRandomMessageText(self):
		return(random.choice(self.quotes))


	#
	# Return a random image URL and its caption
	#
	def getRandomMessageImage(self):

		retval = {}

		reply = random.choice(self.images)
		retval["url"] = reply[0]
		retval["caption"] = reply[1] + "\n\n" + reply[0]

		return(retval)


	#
	# Read our quotes and populate our array.
	#
	def _readQuotes(self, quotes_file) -> list:

		quotes = pathlib.Path.cwd() / quotes_file
		if not quotes.exists():
			raise Exception(f"Quotes file {quotes} does not exist!")
		if not quotes.is_file():
			raise Exception(f"Quotes file {quotes} exists but is not a file!")
		quotes = quotes.read_text()
		self.quotes = quotes.splitlines()

		logger.info(f"Read {len(self.quotes)} quotes from {quotes_file}")


	#
	# Read our list of URLs and populate our list with both them and captions.
	#
	def _readUrls(self, images_file) -> list:

		#
		# Read our URLs and captions for them.
		# 
		images = pathlib.Path.cwd() / images_file
		if not images.exists():
			raise Exception(f"URLs file {images_file} does not exist!")
		if not images.is_file():
			raise Exception(f"URLs file {images_file} exists but is not a file!")
		images_file_contents = images.read_text()

		#
		# Separate the URL from the (optional) caption.
		#
		self.images = []
		for line in images_file_contents.splitlines():
			fields = line.split(",", 1)
			if fields[0] == "url":
				continue
			self.images.append(fields)

		logger.info(f"Read {len(self.images)} image URLs from {images_file}")


