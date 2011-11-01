
''' Event framework for Manygui.

    Magnus Lie Hetland 2001-11-26
'''

TODO = '''
    - Add tags
    - Fix optional arguments/use of kwdargs in place of positionals etc.
'''

__all__ = '''

    any
    link
    unlink
    send
    sender
    unlinkSource
    unlinkHandler
    unlinkMethods

'''.split()


import time
from .References import ref, mapping
import collections
registry = mapping()
from .Utils import IdentityStack
source_stack = IdentityStack()

# TODO: remove this?
class Internal: pass
any  = Internal()
void = Internal()

#def link(source, event, handler,  weak=0, loop=0):
def link(*args, **kwds):
    """link(source, event='default', handler, weak=0, loop=0)

    Creates a link in the Manygui event system, between the source (any
    object) and the handler (any callable, or a (obj,func) pair, where
    func is an unbound method or function, and obj is an object which will
    be supplied as the first parameter to func). Supplying an event (a
    string) will make the link carry only information about events of that
    type. If no event is supplied, 'default' will be assumed. Setting weak
    to a true value will use weak references when setting up the link, so
    that no objects will be "kept alive" by the link.

    A send-loop occurs if an object sends an event "to itself" (i.e. it is
    the source argument of a call to send which hasn't returned at the
    point where one of its methods are about to be activated as a
    handler). The truth value loop decides whether this handler will be
    activated in such a loop. (If send was called with loop=1, loops will
    be allowed anyway.)

    Note that source, event, and handler are strictly positional
    parameters, while the others (weak, and loop) must be supplied as
    keyword parameters.

    Sometimes one might want an event handler that reacts to a specific
    event from any source, or any event from a specific source; or even
    any event from any source. To do that, simply use the special value
    any as either source, event, or both.

    Example:

    .. code-block:: pycon

            from manygui import *
            >>> def monitor_events(event, **kw):
            ...     print 'An event occurred:', event
            ...
            >>> link(any, any, monitor_events)
            >>> btn = Button()
            >>> send(btn, 'foobar')
            An event occurred: foobar

    If you use send(btn, 'click') in this example, you will get two
    events, since the Button will detect the click event (which is its
    default), and issue a default event as well.

    .. note::

            You need to explicitly supply the event type if you want to
            respond to any event type; otherwise you will only respond to the
            default type.

    Event handlers that react to the same event will be called in the
    order they were registered (with link), subject to the following: (1)
    All handlers registered with a specific source will be called before
    handlers with the value any as source; (2) all handlers registered
    with a specific event (including default) are called before handlers
    with the value any as event.

    For more information on sending events, see func:`manygui.send`.
    """
    assert len(args) < 4, 'link takes only three positional arguments'
    if len(args) == 2:
        source, handler = args; event = 'default'
    else:
        source, event, handler = args
    weak = kwds.get('weak', 0)
    loop = kwds.get('loop', 0)
    s = ref(source, weak)
    h = ref(handler, weak)
    h.loop = loop
    if s not in registry:
        registry[s] = {}
    if event not in registry[s]:
        registry[s][event] = []
    if not h in registry[s][event]:
        registry[s][event].append(h)

#def unlink(source, event, handler):
def unlink(*args, **kwds):
    """unlink(source, event='default', handler)

    Undoes a call to link with the same positional arguments. If handler
    has been registered with either source or event as any, that parameter
    will be irrelevant when deciding whether or not to remove that link.
    For instance:

    .. code-block:: python

            link(foo, any, bar)
            unlink(foo, baz, bar)

    Here the link created by link(foo, any, bar) will be removed by the
    call to unlink.

    .. note::

            This behaviour (unlinking handlers registered with the any
            value) may change in future releases.

    Default Events: When used without the event argument, both link and
    send use an event type called default. Most event-generating
    components have a default event type, such as click for Buttons. The
    fact that this event type is default for Button means that when a
    Button generates a click event it will also generate a default event.
    So, if you listen to both click events and default events from a
    Button, your event handler will always be called twice.
    """
    assert len(args) < 4, 'link takes only three positional arguments'
    if len(args) == 2:
        source, handler = args; event = 'default'
    else:
        source, event, handler = args
    h = ref(handler, weak=0)
    for lst in lookup(source, event):
        try:
            lst.remove(h)
        except (KeyError, ValueError): pass

def lookup(source, event):
    source = ref(source, weak=0)
    lists = []
    sources = [source]
    if source() is not any: sources.append(ref(any, weak=0))
    events = [event]
    if event is not any: events.append(any)
    for s in sources:
        for e in events:
            try:
                h = registry[s][e]
                lists.append(registry[s][e])
            except KeyError: pass
    return lists

def send(source, event='default', loop=0, **kw):
    """send(source, event='default', loop=0, **kwds)

    When this is called, any handlers (callables) linked to the source,
    but which will not cause a send-loop (unless loop is true) will be
    called with all the keyword arguments provided (except loop), in the
    order in which they were linked. In addition to the supplied keyword
    arguments, the event framework will add source, event, and the time
    (as measured by the standard Python function time.time) when send was
    called, supplied with the time argument.

    Note that source, and event, are strictly positional parameters, while
    the others (loop, and any additional arguments the user might add)
    must be supplied as keyword parameters.

    Example:

    .. code-block:: python

            # Link an event handler to a button, and then manually send a
            # default event from the button. This event would have been
            # sent automatically if we clicked the button. Note that we
            # only use the arguments we need, and lump the rest in **kw.

            def click(source, time, **kw):
                print 'Button %s clicked at %f.' % (source.text, time)

            btn = Button(text='Click me')
            link(btn, click)

            send(btn) # Fake a button click -- will call click()

    For information about the order in which event handlers are called,
    see :func:`manygui.link`.

    .. important::

       Due to the current semantics of the any value, using it in
       send may not be a good idea, since the result might not be what you
       expect. For instance, calling send(any, any) will only activate event
       handlers which have been linked to the value any as both source and
       event, not to "event handlers with any source and any event". This may
       change in future releases. The current behaviour of send with any is
       consistent with unlink.
    """
    args = {'source': source, 'event': event}
    args.update(kw)
    source_stack.append(source)
    try:
        results = []
        args.setdefault('time', time.time())
        for handlers in lookup(source, event):
            live_handlers = []
            for r in handlers:
                if not r.is_dead():
                    live_handlers.append(r)
                    obj = r.obj
                    if obj is not None:
                        obj = obj()
                        if not loop and not r.loop \
                           and obj in source_stack: continue
                    handler = r()
                    result = handler(**args)
                    if result is not None: results.append(result)
            handlers[:] = live_handlers
        if results: return results
    finally:
        source_stack.pop()

class Sender:
    def __init__(self, event):
        self.event = event
    def __call__(self, source, event, **kwds):
        send(source, self.event, **kwds)
        
def sender(event='default'):
    return Sender(event)

def unlinkSource(source):
    'Unlink all handlers linked to a given source.'
    del registry[source]

def unlinkHandler(handler):
    'Unlink a handler completely from the event framework.'
    h = ref(handler, weak=0)
    for s in list(registry.keys()):
        for e in list(registry[s].keys()):
            try: retistry[s][e].remove(h)
            except ValueError: pass

def unlinkMethods(obj):
    'Unlink all handlers that are methods of obj.'
    for name in dir(obj):
        attr = getattr(obj, name)
        if isinstance(attr, collections.Callable):
            try:
                unlinkHandler(attr)
            except: pass
