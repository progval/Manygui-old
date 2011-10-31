from manygui.Exceptions import UnimplementedMethod
from manygui.Mixins import Attrib
from manygui.ToggleButtons import AbstractToggleButton
from manygui import Defaults

class AbstractRadioButton(AbstractToggleButton, Defaults.RadioButton):

    _group = None
    _value = None

    def __init__(self, *args, **kwargs):
        """
        A RadioButton is a toggle button, just like :class:`manygui.CheckBox`, with slightly
        different appearance, and with the difference that it belongs to a
        RadioGroup. Only one RadioButton can be active (have its on attribute
        be a true Boolean value)in the :class:`manygui.RadioGroup` at one time, so when one is
        clicked or programmatically turned on, the others are automatically
        switched off by the RadioGroup. Each RadioButton also has a value
        attribute, which should be unique within its RadioGroup. When one
        RadioButton is active, the value attribute of its RadioGroup is
        automatically set to that of the active RadioButton. The RadioGroup of
        a RadioButton is set by assigning the RadioGroup to the group
        attribute of the RadioButton. Setting the value attribute of the
        RadioGroup will automatically activate the correct RadioButton.
        """
        AbstractToggleButton.__init__(self, *args, **kwargs)

    def _get_group(self):
        return self._group

    def _set_group(self, new_group):
        old_group = self._group
        if new_group is not old_group:
            if old_group:
                old_group._items.remove(self)
            self._group = new_group
            if new_group:
                new_group._items.append(self)
                self._update_state()

    def _update_state(self):
        group = self._group
        if group:
            self.on = self._value == group._value

    def _get_value(self):
        return self._value

    def _set_value(self, new_value):
        if new_value != self._value:
            self._value = new_value
            self._update_state()

    def do_action(self):
        group = self._group
        if group:
            group.value = self._value
        AbstractToggleButton.do_action(self)
