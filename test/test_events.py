"""
>>> from manygui.Events import *
>>> from manygui.Events import registry
>>> class FooEvent(events.AbstractEvent):
...     pass
...
>>> class FooEvent2(events.AbstractEvent):
...     pass
...
>>> class FooEvent3(events.AbstractEvent):
...     pass
...
>>> class FooEvent4(events.AbstractEvent):
...     pass
...
>>> class SpamEvent(events.AbstractEvent):
...     pass
...
>>> class EggEvent(SpamEvent):
...     pass
...
>>> class Test:
...     DefaultEvent = EggEvent
...     def handle(self, **kw):
...         print('Handled!')
...

Basic functionality:

>>> s = Test()
>>> q = Test()
>>> link(s, q.handle)
>>> send(s)
Handled!
>>> unlink(s, q.handle)
>>> send(s)

>>> link(s, SpamEvent, q.handle)
>>> send(s)
Handled!
>>> unlink(s, SpamEvent, q.handle)
>>> send(s)

#>>> t = Test()
#>>> link(event=FooEvent, t.handle, weak=1)
#>>> send(event=FooEvent())
Handled!

[More comparison demonstrations?]

Strong handlers:

>>> s = Test()
>>> t = Test()
>>> link(s, FooEvent, t.handle)
>>> del t
>>> send(s, FooEvent())
Handled!

Loop blocking:

>>> q = Test()
>>> s = Test()
>>> t = Test()
>>> link(q, q.handle, loop=1)
>>> link(s, t.handle)
>>> link(t, t.handle)
>>> send(q)
Handled!
>>> send(s)
Handled!
>>> send(t)
>>> send(t, loop=1)
Handled!

Return values from event handlers:

>>> s = Test()
>>> def handler1(**kw): return 1
...
>>> def handler2(**kw): return 2
...
>>> def handler3(**kw): return 3
...
>>> link(s, FooEvent2, handler1)
>>> link(s, FooEvent2, handler2)
>>> link(s, FooEvent2, handler3)
>>> send(s, FooEvent2())
[1, 2, 3]

Globbing:

>>> def globbed_handler(**kw):
...     print('Here I am!')
...
>>> link(any, any, globbed_handler)
>>> s = Test()
>>> send(s, FooEvent3())
Here I am!
>>> unlink(any, any, globbed_handler)

[Other API functions]

Exception handling:

>>> def faulty_handler(**kw):
...     print(1/0)
...
>>> s = Test()
>>> link(s, any, faulty_handler)
>>> try:
...     send(s)
... except:
...     print('Caught something')
...
Caught something

Relaying with sender wrapper:

>>> src = Test()
>>> link(src, sender(FooEvent4))
>>> def relayed_event_handler(**kwds):
...     print('Caught relayed_event')
>>> link(any, FooEvent4, relayed_event_handler)
>>> send(src, FooEvent4())
Caught relayed_event

"""

if __name__ == "__main__":
    print("If you want detailed output, use \"python test_events.py -v\".")
    print("No output after this line indicates success.")
    import doctest, test_events
    doctest.testmod(test_events)
