import pytest

from datetime import datetime, timedelta
from copy import copy

from spans import *


class TestSpanArithmetic:

    def test_add_timedelta(self):
        # other: timedelta
        now = datetime.now()
        test = Span(now, now + timedelta(minutes=10))
        test1 = Span(now, now + timedelta(minutes=15))
        assert test + timedelta(minutes=5) == test1

    def test_sub_timedelta(self):
        now = datetime.now()
        test = Span(now, now + timedelta(minutes=10))
        test1 = Span(now, now + timedelta(minutes=5))
        assert test - timedelta(minutes=5) == test1

    def test_add_span(self):
        now = datetime.now()
        test = Span(now, now + timedelta(minutes=10))
        test1 = Span(now + timedelta(minutes=5), now + timedelta(minutes=30))
        assert test + test1 == SpanList([Span(now, now + timedelta(minutes=30))])
        assert test1 + test == SpanList([Span(now, now + timedelta(minutes=30))])

        test1 = Span(now + timedelta(minutes=45), now + timedelta(minutes=60))
        assert test + test1 == SpanList([test, test1])
        assert test1 + test == SpanList([test, test1])

    def test_sub_span(self):
        now = datetime.now()
        test = Span(now, now + timedelta(minutes=10))
        test1 = Span(now + timedelta(minutes=5), now + timedelta(minutes=30))
        assert test - test1 == SpanList([Span(now, now + timedelta(minutes=5))])
        assert test1 - test == \
               SpanList([Span(now + timedelta(minutes=10), now + timedelta(minutes=30))])
        test1 = Span(now - timedelta(minutes=15), now + timedelta(minutes=25))
        assert test1 - test == \
               SpanList([
                   Span(now - timedelta(minutes=15), now),
                   Span(now + timedelta(minutes=10), now + timedelta(minutes=25)),
               ])

        test1 = Span(now + timedelta(minutes=45), now + timedelta(minutes=60))
        assert test - test1 == SpanList([test])
        assert test1 - test == SpanList([test1])
