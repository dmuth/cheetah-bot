

import pytest
import unittest
from unittest import mock
from unittest.mock import MagicMock

from lib.filter.profanity import Profanity


class TestProfanity:

	@pytest.fixture
	def update(self):
		update = MagicMock()
		yield(update)


	def test_hasFoulLanguage(self, update):
		
		profanity = Profanity(ignore = False)
		assert profanity.hasFoulLanguage(update, "fuck") == True

		profanity = Profanity()
		assert profanity.hasFoulLanguage(update, "Fuck") == True

		profanity = Profanity()
		assert profanity.hasFoulLanguage(update, "F u c k") == False

		profanity = Profanity()
		assert profanity.hasFoulLanguage(update, "fuck2") == True

		profanity = Profanity()
		assert profanity.hasFoulLanguage(update, "clean") == False

		profanity = Profanity()
		assert profanity.hasFoulLanguage(update, "🖕") == True

		profanity = Profanity()
		update = MagicMock()
		update.message.sticker.emoji = "🖕"
		assert profanity.hasFoulLanguage(update, "clean") == True

		profanity = Profanity()
		update = MagicMock()
		update.message.sticker.emoji = "🐆"
		assert profanity.hasFoulLanguage(update, "clean") == False

		profanity = Profanity()
		update = MagicMock()
		assert profanity.hasFoulLanguage(update, "🐆") == False

	def test_hasFoulLanguageIgnore(self, update):

		profanity = Profanity(ignore = True)
		assert profanity.hasFoulLanguage(update, "fuck") == False

		profanity = Profanity(ignore = True)
		assert profanity.hasFoulLanguage(update, "F u c k") == False

		profanity = Profanity(ignore = True)
		update = MagicMock()
		update.message.sticker.emoji = "🖕"
		assert profanity.hasFoulLanguage(update, "clean") == False


