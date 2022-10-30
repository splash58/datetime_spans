import pytest

from datetime import datetime, timedelta
from copy import copy

from spans import *


class TestSpanInstance(object):

    def test_ovelap(self):
        now = datetime.now()
        test = Span(now, now + timedelta(minutes=10))
        test1 = Span(now + timedelta(minutes=10), now + timedelta(minutes=20))
        assert not test.overlap(test1)
        assert test.overlap_or_boundary(test1)
        assert not (test & test1)
        test1 = Span(now + timedelta(minutes=5), now + timedelta(minutes=20))
        assert test.overlap(test1)
        assert test.overlap_or_boundary(test1)
        assert (test & test1) == Span(now + timedelta(minutes=5), now + timedelta(minutes=10))

    def test_duration(self):
        now = datetime.now()
        test = Span(now, now + timedelta(minutes=10))
        assert test.duration() == timedelta(minutes=10)

    def test_split(self):
        pass
