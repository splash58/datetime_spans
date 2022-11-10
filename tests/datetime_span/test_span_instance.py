import pytest

from datetime import datetime, timedelta
from copy import copy

from spans import *


class TestSpanInstance(object):
    def test_bool(self):
        now = datetime.now()
        temp = Span(now, now)
        assert not temp

    def test_contains(self):
        now = datetime.now()
        assert now in Span(now, now + timedelta(minutes=10))
        assert now not in Span(now - timedelta(minutes=10), now)

    def test_copy(self):
        now = datetime.now()
        test = Span(now, now + timedelta(minutes=10))
        test_copy = copy(test)
        assert test == test_copy
        test_copy.end += timedelta(minutes=20)
        assert test != test_copy




