from manygui.Exceptions import UnimplementedMethod
from manygui.Mixins import Attrib, DefaultEventMixin
from manygui.Events import send
from manygui import Defaults
from .Utils import flatten

class RadioGroup(Attrib, Defaults.RadioGroup, DefaultEventMixin):

    # Needed by Attrib
    def refresh(self, **ignore): pass

    def __init__(self, items=[], **kw):
        """
        See :class:`manygui.RadioButton`.
        """
        Attrib.__init__(self, **kw)
        DefaultEventMixin.__init__(self)
        self._items = []
        self.add(items)

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        if 1 or self._value != value: # FIXME: Why is this "commented out"?
            self._value = value
            for item in self._items:
                item._update_state()
        send(self, 'select')

    def add(self, buttons):
        for btn in flatten(buttons):
            btn.group = self

    def remove(self, buttons):
        for btn in buttons:
            if btn in self._items:
                btn.group = None
                #self._items.remove(btn)
