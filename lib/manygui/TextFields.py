from manygui.TextComponents import AbstractTextComponent
from manygui import Defaults

class AbstractTextField(AbstractTextComponent, Defaults.TextField):
    def __init__(self, *args, **kwargs):
        """
        A one-line text-editing Component. (See also :class:`manygui.TextArea`) If the
        enter/return key is pressed within a TextField, the TextField will
        send a enterkey event.
        """
        AbstractTextComponent.__init__(self, *args, **kwargs)
