# datetime_spans

A small tool for designing schedules and the like. He only has two classes

* Span - contains a time interval with a closed start and an open end.
What does it mean that the start point is in the interval but the end point is not
* SpanList - a list with objects of type Span

### Base usage

work_time = Span(datetime.strptime("14:30:00", "%H:%M:%S"), datetime.strptime("18:20:00", "%H:%M:%S"))