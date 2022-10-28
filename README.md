# datetime_spans

A small tool for designing schedules and the like. It has two classes

* Span - contains a time interval with a closed start and an open end.
It means that the start point is in the interval but the end point is out
* SpanList - a list with objects of type Span

### Usage Eexample

    >>> from datetime import datetime, timedelta
    >>> from datetime_spans import *

    >>> working_time = Span(datetime.strptime("09:00", "%H:%M"), datetime.strptime("18:00", "%H:%M"))
    >>> break_time = Span(datetime.strptime("13:00", "%H:%M"), datetime.strptime("14:00", "%H:%M"))
    >>> office_time = working_time - break_time
    >>> format(office_time, '%H:%M')
    [
       [09:00..13:00),
       [14:00..18:00)
    ]

    >>> office_time.duration()
    '8:00:00'

    >>> appointments = office_time.split(timedelta(hours=1))
    [  
       [09:00..10:00),  [10:00..11:00),  [11:00..12:00),  [12:00..13:00)
       [14:00..15:00),  [15:00..16:00),  [16:00..17:00),  [17:00..18:00)
    ]

    # customer wants
    >>> can = Span(datetime.strptime("10:30", "%H:%M"), datetime.strptime("13:15", "%H:%M"))
    # suitable appointments
    >>> SpanList([x for x in appointments if x <= can]).__format__("%H:%M")
    [
       [11:00..12:00),
       [12:00..13:00)
    ]

### Span Class description

