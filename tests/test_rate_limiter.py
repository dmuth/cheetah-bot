

from unittest import mock
import time

#import pytest

from lib.rate_limiter import RateLimiter


def test_quota():

	times = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
	with mock.patch("time.time", mock.MagicMock(side_effect = times)) as m:
		r = RateLimiter(actions = 2, period = 60)
		assert r.isQuotaFull() == True
		assert r.isQuotaExhausted() == False
		assert r.getTimeUntilQuotaFull() == 60
		assert r.getQuota() == 2
		assert r.action() == True
		assert r.isQuotaFull() == False
		assert r.isQuotaExhausted() == False
		assert r.getQuota() == 1
		assert r.action() == True
		assert r.getQuota() == 0
		assert r.action() == False
		assert r.action() == False
		assert r.getQuota() == 0
		assert r.isQuotaFull() == False
		assert r.isQuotaExhausted() == True
		assert r.getTimeUntilQuotaFull() == 60

def test_quota_over_time():

	times = [0, 30, 30, 30, 30, 30, 45, 60 ]
	with mock.patch("time.time", mock.MagicMock(side_effect = times)) as m:
		r = RateLimiter(actions = 2, period = 60)
		assert r.isQuotaFull() == True
		assert r.isQuotaExhausted() == False
		assert r.getQuota() == 2
		assert r.action() == True
		assert r.isQuotaFull() == False
		assert r.getQuota() == 1
		assert r.getQuota() == 1.5
		assert r.getQuota() == 2


