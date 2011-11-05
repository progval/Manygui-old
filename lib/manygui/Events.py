
''' Event framework for Manygui.

    Magnus Lie Hetland 2001-11-26
    Valentin Lorentz 2011
'''

TODO = '''
    - Add tags
    - Fix optional arguments/use of kwdargs in place of positionals etc.
'''

__all__ = '''

    any
    events
    link
    unlink
    send
    sender
    unlinkSource
    unlinkHandler
    unlinkMethods

'''.split()


import time
import collections
registry = {}
from .Mixins import Attrib
from .Utils import IdentityStack
from . import Devices
source_stack = IdentityStack()

class Internal: pass
any  = Internal
void = Internal

class events:
    """Namespace for all event types."""
    class AbstractEvent(Attrib):
        """Base event."""
        device = None
        """The device which triggered the event (mouse, keyboard, ...)."""
        time = None
        """The timestamp at the moment the event was raised."""
        # We don't set a component attribute here, because some events may
        # not be related to a component (timer/trigger?)

        def __init__(self, *args, **kwargs):
            Attrib.__init__(self, *args, **kwargs)
            self.time = time.time()

    class SelectEvent(AbstractEvent):
        component = None
        item = None

    class ToggleEvent(AbstractEvent):
        component = None

    class CloseEvent(AbstractEvent):
        component = None # Probably a Window

    ####################
    # System events

    class SystemEvent(AbstractEvent):
        pass

    class ShutdownEvent(SystemEvent):
        pass

    ####################
    # MVC events

    class ModelEvent(AbstractEvent):
        names = []


    ####################
    # Mouse events

    class MouseEvent(AbstractEvent):
        device = Devices.Mouse()
        component = None

    class LeftClickEvent(MouseEvent):
        pass

    class RightClickEvent(MouseEvent):
        pass

    class PressEvent(MouseEvent):
        pass

    class ReleaseEvent(MouseEvent):
        pass

    class MouseSelectEvent(MouseEvent, SelectEvent):
        pass


    ####################
    # Keyboard events

    class KeyboardEvent(AbstractEvent):
        device = Devices.Keyboard()
        component = None
        text = None

    class TextInputEvent(KeyboardEvent):
        device = Devices.Keyboard()
        component = None

    class PressEnterEvent(KeyboardEvent):
        pass

#def link(source, event, handler, loop=0):
def link(*args, **kwds):
    """link(source, event=None, handler, loop=0)

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
        source, handler = args;
        if source is any:
            event = None
        elif hasattr(source, 'DefaultEvent'):
            event = source.DefaultEvent
        else:
            event = any
    else:
        source, event, handler = args
    if event is None:
        assert hasattr(source, 'DefaultEvent'), 'The source object has no ' +\
                'default event set. You must give the event to link.'
        # Note : we could use any in that case (that's why the previous
        # implementation did). But it would be too confusing to users to
        # have two different behavior depending on the implementation of
        # the components.
        event = source.DefaultEvent
    loop = kwds.get('loop', 0)
    handler.__dict__['loop'] = loop
    if source not in registry:
        registry[source] = {}
    if event not in registry[source]:
        registry[source][event] = []
    if not handler in registry[source][event]:
        registry[source][event].append(handler)

#def unlink(source, event, handler):
def unlink(*args, **kwds):
    """unlink(source, event=None, handler)

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

    If `event` is not given (or None), it will default to the default event
    of the source.
    """
    assert len(args) < 4, 'link takes only three positional arguments'
    if len(args) == 2:
        source, handler = args;
        if source is any:
            event = None
        else:
            event = source.DefaultEvent
    else:
        source, event, handler = args
    try:
        registry[source][event].remove(handler)
    except (KeyError, ValueError): pass

def lookup(source, event):
    if not isinstance(event, type):
        event = event.__class__
    if event is None:
        event = source.DefaultEvent

    # Filter by source
    events = {}
    if source in registry:
        events.update(registry[source])
    if any in registry:
        for event, lst in registry[any].items():
            if event in events:
                events[event].extend(lst)
            else:
                events.update({event: lst})

    # Filter by event
    lst = []
    for e in events:
        if issubclass(event, e) or e is any:
            lst += events[e]
    return lst

def send(source, event=None, loop=0):
    """send(source, event=None, loop=0)

    When this is called, any handlers (callables) linked to the source,
    but which will not cause a send-loop (unless loop is true) will be
    called in the order in which they were linked.

    If `event` is not given (or None), it will default to the default event
    of the source.

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

        You can't use :class:`manygui.any` here.
    """
    assert source is not any
    assert event is not any
    source_stack.append(source)
    if event is None:
        event = source.DefaultEvent()
    try:
        results = []
        for handler in lookup(source, event):
            if handler is not None:
                if not loop and not handler.loop \
                   and handler in source_stack: continue
            result = handler(source=source, event=event)
            if result is not None: results.append(result)
        if results: return results
    finally:
        source_stack.pop()

class Sender:
    def __init__(self, event):
        self.event = event
    def __call__(self, source, event):
        if self.event is None:
            event = source.DefaultEvent
        else:
            event = self.event
        send(source, event())
        
def sender(event=None):
    return Sender(event)

def unlinkSource(source):
    'Unlink all handlers linked to a given source.'
    del registry[source]

def unlinkHandler(handler):
    'Unlink a handler completely from the event framework.'
    for s in list(registry.keys()):
        for e in list(registry[s].keys()):
            try: retistry[s][e].remove(handler)
            except ValueError: pass

def unlinkMethods(obj):
    'Unlink all handlers that are methods of obj.'
    for name in dir(obj):
        attr = getattr(obj, name)
        if isinstance(attr, collections.Callable):
            try:
                unlinkHandler(attr)
            except: pass
