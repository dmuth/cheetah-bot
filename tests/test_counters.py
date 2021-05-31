

from unittest import mock
import time

#import pytest

from lib.counters import Counters


chat_id = 123
chat_id2 = 124

def test_counters_disabled():

	counters = Counters(-1)
	assert counters.update(chat_id) == False
	assert counters.update(chat_id2) == False
	assert counters.update(chat_id) == False
	assert counters.update(chat_id2) == False
	assert counters.update(chat_id) == False
	assert counters.update(chat_id2) == False

	counters = Counters(None)
	assert counters.update(chat_id) == False
	assert counters.update(chat_id2) == False
	assert counters.update(chat_id) == False
	assert counters.update(chat_id2) == False
	assert counters.update(chat_id) == False
	assert counters.update(chat_id2) == False


def test_counters():

	counters = Counters(3)
	assert counters.update(chat_id) == False
	assert counters.update(chat_id2) == False
	assert counters.update(chat_id) == False
	assert counters.update(chat_id2) == False
	assert counters.update(chat_id) == True
	assert counters.update(chat_id2) == True
	assert counters.update(chat_id) == False
	assert counters.update(chat_id2) == False

	counters = Counters(2)
	assert counters.update(chat_id) == False
	assert counters.update(chat_id2) == False
	assert counters.update(chat_id) == True
	assert counters.update(chat_id2) == True



