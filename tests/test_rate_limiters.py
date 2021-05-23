

from unittest import mock
import time

#import pytest

from lib.rate_limiters import RateLimiters


def test_rate_limiters():

	times = [0, 30, 30, 30, 30, 30, 45, 60 ]
	with mock.patch("time.time", mock.MagicMock(side_effect = times)) as m:
		limiters = RateLimiters(actions = 2, period = 60)
		r = limiters.getRateLimiter(123)
		assert r.isQuotaFull() == True
		assert r.isQuotaExhausted() == False
		assert r.getQuota() == 2
		assert r.action() == True
		assert r.isQuotaFull() == False
		assert r.getQuota() == 1
		assert r.getQuota() == 1.5
		assert r.getQuota() == 2


