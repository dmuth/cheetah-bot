
import time
import pytest
from unittest.mock import MagicMock

from lib.cheetah_bot import CheetahBot
import telegram
from telegram.error import TelegramError


@pytest.fixture
def bot():

	bot = CheetahBot()
	bot.counters = MagicMock()
	bot.filter = MagicMock()
	bot.match = MagicMock()
	bot.profanity = MagicMock()
	bot.rate_limiters = MagicMock()

	bot.replies = MagicMock()
	stats = {}
	stats["total"] = "total"
	stats["quotes"] = "quotes"
	stats["images"] = "images"
	bot.replies.getStats = MagicMock(return_value = stats)

	pytest.limiter = MagicMock()
	pytest.limiter.actions = "actions"
	pytest.limiter.period = "period"
	pytest.limiter.getQuota = MagicMock(return_value = 73)
	bot.rate_limiters.getRateLimiter = MagicMock(return_value = pytest.limiter)

	bot.sleep_wake = MagicMock()
	bot.my_id = 72
	bot.allowed_group_ids = []
	bot.allowed_group_names = []
	bot.my_username = "whoever"

	pytest.chat_id = 123
	pytest.chat_id2 = 124
	pytest.title = "test title"
	pytest.message = MagicMock()
	pytest.message_text_1 = "test message"

	pytest.context = MagicMock()

	yield(bot)


@pytest.fixture
def update(bot):

	update = MagicMock()
	update.effective_chat.id = pytest.chat_id
	update.effective_chat.title = pytest.title
	update.message.date.timestamp = MagicMock(return_value = time.time())

	yield(update)


@pytest.fixture
def context():
	context = MagicMock()
	return(context)


@pytest.fixture
def limiter():
	limiter = MagicMock()
	return(limiter)


#
# Call the echo() function and verify that we made it through both functions under it.
#
def test_echo_main(bot, update, context):

	bot.filter.messageIsIgnorable = MagicMock(return_value = False)
	bot.filter.messageIsDm = MagicMock(return_value = False)
	bot.match.doesGroupMatch = MagicMock(return_value = True)
	update.message.text = pytest.message_text_1
	limiter.getQuota = MagicMock(return_value = 73)
	bot.sleep_wake.isAsleep = MagicMock(return_value = False)

	bot.echo(update, context)

	context.bot.send_message.assert_called()
	context.bot.send_photo.assert_not_called()

	#
	# Make sure that echo() catches the "have no rights" error.
	#
	context.bot.send_message = MagicMock(side_effect=telegram.error.BadRequest("Have no rights to send a message"))
	bot.echo(update, context)

	#
	# Any other string in an exception will be thrown.
	#
	context.bot.send_message = MagicMock(side_effect=telegram.error.BadRequest("test"))

	pytest.e = None
	try:
		bot.echo(update, context)
	except Exception as e:
		pytest.e = str(e)
	assert "test" in pytest.e




def test_echoParseMessage_message_too_old(bot, update, context):

	update.message.date.timestamp = MagicMock(return_value = time.time() - 100)

	bot.echoParseMessage(update, context)
	bot.filter.messageIsIgnorable.assert_not_called()


def test_echoParseMessage_messageIsIgnorable(bot, update, context):

	#update.message.text = pytest.message_text_1
	bot.echoParseMessage(update, context)
	bot.filter.messageIsIgnorable.assert_called()
	bot.filter.messageIsDm.assert_not_called()


def test_echoParseMessage_messageIsDm(bot, update, context):
	bot.filter.messageIsIgnorable = MagicMock(return_value = False)

	bot.echoParseMessage(update, context)
	bot.filter.messageIsDm.assert_called()
	context.bot.send_message.assert_called()


def test_echoParseMessage_doesGroupMatch(bot, update, context):

	bot.filter.messageIsIgnorable = MagicMock(return_value = False)
	bot.filter.messageIsDm = MagicMock(return_value = False)
	bot.match.doesGroupMatch = MagicMock(return_value = False)

	bot.echoParseMessage(update, context)
	bot.match.doesGroupMatch.assert_called()
	bot.match.doesUserMatch.assert_not_called()


#
# This test starts with the part of the function where replies are created and sent off.
#
def test_echoComposeReply(bot, update, context):

	bot.echoComposeReply(update, context, pytest.message, pytest.message_text_1, pytest.chat_id)

	bot.match.doesUserMatch.assert_called()
	bot.filter.messageContainsHelp.assert_called()
	bot.filter.messageContainsStats.assert_not_called()
	bot.filter.messageIsChee.assert_called()
	bot.profanity.hasFoulLanguage.assert_called()
	bot.sleep_wake.isAsleep.assert_called()
	pytest.limiter.action.assert_not_called()

	bot.filter.messageContainsHelp = MagicMock(return_value = False)
	bot.echoComposeReply(update, context, pytest.message, pytest.message_text_1, pytest.chat_id)
	bot.filter.messageContainsHelp.assert_called()
	bot.filter.messageContainsStats.assert_called()


def test_sendMessage(bot, update, context, limiter):

	bot.sendMessage(context.bot, pytest.limiter, pytest.chat_id)
	bot.sleep_wake.isAsleep.assert_called()
	pytest.limiter.action.assert_not_called()

	bot.sleep_wake.isAsleep = MagicMock(return_value = False)

	#
	# Copying out the contents of the exception in case an exception is NOT thrown.
	# I also tried the pytest.raises() syntax, but it doesn't seem to work for the general Exception class.
	#
	pytest.e = None
	try:
		bot.sendMessage(context.bot, limiter, pytest.chat_id)
	except Exception as e:
		pytest.e = str(e)
	assert "Not sure" in pytest.e

	bot.sleep_wake.isAsleep.assert_called()
	limiter.action.assert_called()


def test_sendMessage_send_message(bot, context, limiter):

	limiter.getQuota = MagicMock(return_value = 73)
	bot.sleep_wake.isAsleep = MagicMock(return_value = False)
	bot.sendMessage(context.bot, limiter, pytest.chat_id, reply = "whatever")
	context.bot.send_message.assert_called()
	context.bot.send_photo.assert_not_called()


def test_sendMessage_send_message_image(bot, context, limiter):

	limiter.getQuota = MagicMock(return_value = 73)
	bot.sleep_wake.isAsleep = MagicMock(return_value = False)
	bot.sendMessage(context.bot, limiter, pytest.chat_id, image_url = "whatever", caption = "whatever")
	context.bot.send_message.assert_not_called()
	context.bot.send_photo.assert_called()


#def test_TEMPLATE(bot, update, context):
#
#	update.message.text = pytest.message_text_1
#	bot.echo(update, context)
#	#bot.filter.messageIsIgnorable.assert_called()
#	#bot.filter.messageIsDm.assert_not_called()


