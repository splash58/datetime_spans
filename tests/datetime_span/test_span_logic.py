import pytest

from datetime import datetime, timedelta
from copy import copy

from spans import *


class TestSpanLogic(object):
    def test_compare(self):
        now = datetime.now()
        test = Span(now, now + timedelta(minutes=10))
        test_copy = copy(test)
        assert test <= test_copy
        assert test >= test_copy
        assert test == test_copy
        test_copy.end += timedelta(minutes=20)
        assert test < test_copy
        assert test <= test_copy
        test_copy = copy(test)
        test.start -= timedelta(minutes=20)
        assert test > test_copy
        assert test >= test_copy
        test_copy = copy(test)
        test.start += timedelta(minutes=60)
        test.end += timedelta(minutes=60)
        assert not test <= test_copy
        assert not test >= test_copy