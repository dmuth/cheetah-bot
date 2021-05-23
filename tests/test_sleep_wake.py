

from unittest import mock
from unittest.mock import MagicMock
import threading

#import pytest

from lib.sleep_wake import SleepWake


def test_sleep_wake():

	start = MagicMock()

	with mock.patch("threading.Timer", MagicMock(side_effect = start)) as m:
		sleep = SleepWake()
		bot = MagicMock()
		limiter = MagicMock()
		chat_id = 123

		sleep.goToSleep(bot, limiter, chat_id)

		bot.send_message.assert_called_once()
		name, _, kwargs = bot.mock_calls[0]
		assert name == "send_message"
		assert kwargs["chat_id"] == chat_id

		m.assert_called_once()
		start.assert_called_once()
		assert start.mock_calls[0][2]["args"][2] == chat_id

		#
		# Second call to exercise code when bot is not fully awake
		#
		start.reset_mock()
		m.reset_mock()
		bot.reset_mock()
		limiter.reset_mock()

		sleep.goToSleep(bot, limiter, chat_id)

		m.assert_called_once()
		bot.assert_not_called()
		assert start.mock_calls[0][2]["args"][2] == chat_id


def test_isAsleep():

	start = MagicMock()

	with mock.patch("threading.Timer", MagicMock(side_effect = start)) as m:

		sleep = SleepWake()
		bot = MagicMock()
		limiter = MagicMock()
		limiter.getQuota = MagicMock(side_effect = [ 1 ])
		limiter.isQuotaFull = MagicMock(returns = True)
		chat_id = 123
		
		assert sleep.isAsleep(chat_id) == False

		sleep.goToSleep(bot, limiter, chat_id)

		assert sleep.isAsleep(chat_id) == True

		sleep.wakeUp(bot, limiter, chat_id)

		assert sleep.isAsleep(chat_id) == False


def test_wake_up():

	sleep = SleepWake()
	bot = MagicMock()
	limiter = MagicMock()
	limiter.getQuota = MagicMock(side_effect = [ 1 ])
	limiter.isQuotaFull = MagicMock(returns = True)
	chat_id = 123

	sleep.wakeUp(bot, limiter, chat_id)
	bot.send_message.assert_called_once()
	name, _, kwargs = bot.mock_calls[0]
	assert name == "send_message"
	assert kwargs["chat_id"] == chat_id

	



