import pytest

from datetime import datetime, timedelta
from copy import copy

from spans import *


class TestSpanArithmetic(object):

    def test_timedelta(self):
        # other: timedelta
        now = datetime.now()
        test = Span(now, now + timedelta(minutes=10))
        test1 = Span(now, now + timedelta(minutes=15))
        assert test + timedelta(minutes=5) == test1
        test = Span(now, now + timedelta(minutes=10))
        test1 = Span(now, now + timedelta(minutes=5))
        assert test - timedelta(minutes=5) == test1
