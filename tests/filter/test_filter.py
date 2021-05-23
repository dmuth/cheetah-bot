

import unittest
from unittest import mock
from unittest.mock import MagicMock

from lib.filter.filter import Filter
#import pytest


class TestFilter(unittest.TestCase):

	def test_botWasAddedToGroup(self):

		filter = Filter()

		user = MagicMock()
		user_id = 123
		user.id = user_id

		update = MagicMock()
		message = MagicMock()
		message.new_chat_members = [ user ]
		my_id = user_id
	
		self.assertTrue(filter.botWasAddedToGroup(update, message, my_id))
		self.assertFalse(filter.botWasAddedToGroup(update, message, my_id + 1))
	

	def test_botWasRemovedFromGroup(self):
		filter = Filter()

		user = MagicMock()
		user_id = 123
		user.id = user_id

		update = MagicMock()
		message = MagicMock()
		message.left_chat_member = user
		my_id = user_id

		self.assertTrue(filter.botWasRemovedFromGroup(update, message, my_id))
		self.assertFalse(filter.botWasRemovedFromGroup(update, message, my_id + 1))


	def test_messageIsIgnorable(self):

		filter = Filter()

		user_id = 123
		user = MagicMock()
		user.id = user_id

		update = MagicMock()
		update.effective_chat.id = 1234
		update.effective_chat.title = "unit test"
		message = MagicMock()
		message.left_chat_member = user
		my_id = user_id

		self.assertTrue(filter.messageIsIgnorable(update, message, my_id))
		self.assertFalse(filter.messageIsIgnorable(update, message, my_id + 1))



