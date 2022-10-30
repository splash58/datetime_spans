from __future__ import annotations

from datetime import datetime, timedelta
from copy import copy

__all__ = ['Span', 'SpanList']


class Span:
    format_spec = None

    @staticmethod
    def empty():
        return Span(datetime.min, datetime.min)

    def __init__(self, start: datetime, end: datetime):
        """

        :param start:
        :param end:
        """
        self.start = copy(start)
        self.end = copy(end)
        if end < start:
            raise ValueError('End before Start')

    def __str__(self) -> str:
        if self.start == self.end:
            return f'[empty)'
        if self.format_spec is not None:
            return f'[{format(self.start, self.format_spec)}..{format(self.end, self.format_spec)})'
        else:
            return f'[{self.start.__str__()}..{self.end.__str__()})'

    def __format__(self, format_spec):
        if self.start == self.end:
            return f'[empty)'
        return f'[{format(self.start, format_spec)}..{format(self.end, format_spec)})'

    def __repr__(self):
        if self.start == self.end:
            return f'Range.empty()'
        return f'Range({self.start.__repr__()}, {self.end.__repr__()})'

    def __contains__(self, item: datetime) -> bool:
        return self.start <= item < self.end

    def __copy__(self) -> Span:
        return Span(self.start, self.end)

    def __bool__(self):
        return not self.start == self.end

    def __sub__(self, other: Span | timedelta) -> Span | SpanList:
        if isinstance(other, timedelta):
            end = max(self.start, self.end - other)
            return Span(self.start, end)
        self._checkOther(other, '-')
        if self < other:
            return SpanList([])
        if not self.overlap(other):
            return SpanList([copy(self)])
        res = []
        if self.start < other.start:
            res.append(Span(self.start, other.start))
        if other.end < self.end:
            res.append(Span(other.end, self.end))
        return SpanList(res)

    def __add__(self, other: Span | timedelta) -> Span | SpanList:
        if isinstance(other, timedelta):
            end = self.end + other
            return Span(self.start, end)
        self._checkOther(other, '+')
        if other < self:
            return SpanList([copy(self)])
        if self.overlap_or_boundary(other):
            res = copy(self)
            res |= other
            return SpanList([res])
        return SpanList([
            copy(self),
            copy(other),
        ])

    def __and__(self, other: Span) -> Span:
        if not self.overlap(other):
            return Span.empty()
        return Span(max(self.start, other.start), min(self.end, other.end))

    def __eq__(self, other: Span) -> bool:
        if not isinstance(other, Span):
            raise TypeError(f'unsupported operand type(s) for ==: {type(self)} and {type(other)}')
        return other.start == self.start and other.end == self.end

    def __lt__(self, other: Span | timedelta) -> bool:
        if isinstance(other, timedelta):
            return self.duration() < other
        elif isinstance(self, Span):
            return self.start >= other.start and other.end >= self.end and \
                   not (other.start == self.start and other.end == self.end)
        raise TypeError(f'unsupported operand type(s) for >: {type(self)} and {type(other)}')

    def __le__(self, other: Span | timedelta) -> bool:
        if isinstance(other, timedelta):
            return self.duration() <= other
        elif isinstance(self, Span):
            return self.start >= other.start and self.end <= other.end
        raise TypeError(f'unsupported operand type(s) for <=: {type(self)} and {type(other)}')

    def __gt__(self, other: Span | timedelta) -> bool:
        if isinstance(other, timedelta):
            return self.duration() > other
        elif isinstance(self, Span):
            return self.start <= other.start and other.end <= self.end and \
                   not (other.start == self.start and other.end == self.end)
        raise TypeError(f'unsupported operand type(s) for >: {type(self)} and {type(other)}')

    def __ge__(self, other: Span | timedelta) -> bool:
        if isinstance(other, timedelta):
            return self.duration() >= other
        elif isinstance(self, Span):
            return self.start <= other.start and other.end <= self.end
        raise TypeError(f'unsupported operand type(s) for >=: {type(self)} and {type(other)}')

    def overlap(self, other: Span) -> bool:
        self._checkOther(other, 'overlap')
        return self.overlap_or_boundary(other) and \
            other.start != self.end and other.end != self.start

    def overlap_or_boundary(self, other: Span) -> bool:
        return self.start <= other.end and other.start <= self.end

    def duration(self):
        return self.end - self.start

    def split(self, delta: timedelta, full=False, rest=timedelta()):
        res = []
        start = copy(self.start)
        while start + delta - rest < self.end:
            res.append(Span(start, start + delta - rest))
            start += delta - rest
            rest = timedelta()
        if not full:
            res.append(Span(start, self.end))
        return SpanList(res)

    def _checkOther(self, other: Span, op: str):
        if not isinstance(other, Span):
            raise TypeError(f'unsupported operand type(s) for {op}: {type(self)} and {type(other)}')

    def __ior__(self, other: Span) -> Span:
        if not self.overlap_or_boundary(other):
            raise ValueError('range needs to overlap')
        self.start = min(self.start, other.start)
        self.end = max(self.end, other.end)
        return self

    def __iand__(self, other: Span) -> Span:
        if not self.overlap(other):
            self.start = datetime.min
            self.end = datetime.min
        else:
            self.start = max(self.start, other.start)
            self.end = min(self.end, other.end)
        return self


class SpanList:

    merge = False
    format_spec = None

    @property
    def start(self) -> datetime:
        if not self.ranges:
            raise AttributeError('Empty Ranges')
        return self.ranges[0].start

    @property
    def end(self) -> SpanList:
        if not self.ranges:
            raise AttributeError('Empty Ranges')
        return self.ranges[-1].end

    def __init__(self, ranges: [Span, datetime, list] = None, end: datetime = None):
        """

        :param ranges: Span | datetime | List :
        :param end: date
        """
        self.ranges: [Span] = []
        if ranges is not None:
            if isinstance(ranges, datetime):
                if end is None:
                    raise ValueError('Need start and end.')
                else:
                    ranges = Span(ranges, end)
            if isinstance(ranges, Span):
                ranges = [ranges]
            self.ranges.extend(ranges)
            self.normalize()

    def normalize(self) -> SpanList:
        self.ranges = list(filter(lambda x: bool(x), self.ranges))
        if not self.ranges:
            return self
        self.ranges.sort(key=lambda x: (x.start, x.end))
        if not self.merge:
            return self
        result = []
        merge = self.ranges[0]
        for i in range(1, len(self.ranges)):
            if self.ranges[i].start > merge.end:
                result.append(merge)
                merge = self.ranges[i]
            else:
                merge |= self.ranges[i]
        result.append(merge)
        self.ranges = result
        return self

    def __str__(self):
        if not self.ranges:
            return f'[ empty ]'
        if self.format_spec:
            string = ",\n  ".join(format(x, self.format_spec) for x in self.ranges)
        else:
            string = ",\n  ".join(str(x) for x in self.ranges)
        return f'[\n  {string}\n]'

    def __format__(self, format_spec):
        string = ",\n  ".join(format(x, format_spec) for x in self.ranges)
        return f'[\n  {string}\n]'

    def __repr__(self):
        string = ",\n    ".join(repr(x) for x in self.ranges)
        if string:
            return f'Ranges([\n    {string}\n])'
        return f'Ranges([])'

    def __bool__(self):
        return bool(len(self.ranges))

    def __getitem__(self, item):
        return self.ranges[item]

    def __delitem__(self, key):
        del self.ranges[key]

    def __add__(self, other: Span | SpanList) -> SpanList:
        if isinstance(other, Span):
            self._append(other)
        elif isinstance(other, SpanList):
            self._extend(other.ranges)
        else:
            raise TypeError(f'unsupported operand type(s) for +: {type(self)} and {type(other)}')
        return self

    def __sub__(self, other: Span | SpanList) -> SpanList:
        res = []
        if isinstance(other, Span):
            for x in self.ranges:
                res.extend((x - other).ranges)
        elif isinstance(other, SpanList):
            c = copy(self)
            for r in other.ranges:
                c -= r
            return c
        else:
            raise TypeError(f'unsupported operand type(s) for +: {type(self)} and {type(other)}')
        return SpanList(res)

    def __and__(self, other: Span | SpanList):
        res = []
        if isinstance(other, Span):
            for x in self.ranges:
                res.append(x & other)
        elif isinstance(other, SpanList):
            c = copy(self)
            res = []
            for r in other.ranges:
                res.extend((c & r).ranges)
        else:
            raise TypeError(f'unsupported operand type(s) for +: {type(self)} and {type(other)}')
        return SpanList(res)

    __iadd__ = __add__
    __isub__ = __sub__
    __iand__ = __and__

    def duration(self):
        return sum([x.duration() for x in self.ranges], timedelta())

    def split(self, delta: timedelta, full=False, transfer=False):
        res = []
        rest = timedelta()
        for x in self.ranges:
            temp = x.split(delta, full=full, rest=rest)
            if transfer:
                res = x.duration() - temp.duration()
            res.extend(temp)
        return SpanList(res)

    def _append(self, other: Span) -> SpanList:
        if not isinstance(other, Span):
            raise TypeError(f'unsupported operand type(s) for append: {type(other)}')
        self.ranges.append(copy(other))
        self.normalize()
        return self

    def _extend(self, other: list[Span]) -> SpanList:
        if not isinstance(other, list):
            raise TypeError(f'unsupported operand type(s) for extend: {type(other)}')
        for x in other:
            if not isinstance(x, Span):
                raise TypeError(f'unsupported operand type(s) for extend: {type(x)}')
            self.ranges.append(copy(x))
        self.normalize()
        return self
