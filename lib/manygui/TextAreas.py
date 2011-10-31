from manygui.TextComponents import AbstractTextComponent
from manygui import Defaults

class AbstractTextArea(AbstractTextComponent, Defaults.TextArea):
    def __init__(self, *args, **kwargs):
        """
        A multiline text-editing Component. Its text is stored in the text
        attribute, which will be modified (according to the MVC mechanism)
        when the component loses focus. It also supports the Boolean editable
        property, which may be used to control whether the user can edit the
        text area or not.
        """
        AbstractTextComponent.__init__(self, *args, **kwargs)
