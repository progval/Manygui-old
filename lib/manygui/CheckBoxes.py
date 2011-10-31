from manygui.ToggleButtons import AbstractToggleButton
from manygui import Defaults

class AbstractCheckBox(AbstractToggleButton, Defaults.CheckBox):
    def __init__(self, *args, **kwargs):
        """
        CheckBox is a kind of button, and thus will also generate 'click' and
        'default' events when clicked. But in addition, each CheckBox has a
        Boolean attribute on, which is toggled each time the box is clicked.
        The state of the CheckBox can be altered by assigning to this
        attribute.
        """
        AbstractToggleButton.__init__(self, *args, **kwargs)
