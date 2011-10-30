# Copyright (c) 2011, Valentin Lorentz
#
# Permission is hereby granted, free  of charge, to any person obtaining
# a  copy  of this  software  and  associated  documentation files  (the
# "Software"), to  deal in  the Software without  restriction, including
# without limitation  the rights to  use, copy, modify,  merge, publish,
# distribute,  sublicense, and/or sell  copies of  the Software,  and to
# permit persons to whom the Software  is furnished to do so, subject to
# the following conditions:
#
# The  above  copyright  notice  and  this permission  notice  shall  be
# included in all copies or substantial portions of the Software.
#
# THE  SOFTWARE IS  PROVIDED  "AS  IS", WITHOUT  WARRANTY  OF ANY  KIND,
# EXPRESS OR  IMPLIED, INCLUDING  BUT NOT LIMITED  TO THE  WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT  SHALL THE AUTHORS OR COPYRIGHT HOLDERS  BE LIABLE FOR ANY
# CLAIM, DAMAGES OR  OTHER LIABILITY, WHETHER IN AN  ACTION OF CONTRACT,
# TORT  OR OTHERWISE, ARISING  FROM, OUT  OF OR  IN CONNECTION  WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Dummy backend for core tests."""

from manygui.backends import *
__all__ = manygui.__all__

from manygui import Events
from manygui import Canvases
from manygui import Labels
from manygui import ListBoxes
from manygui import Buttons
from manygui import CheckBoxes
from manygui import RadioButtons
from manygui import RadioGroups
from manygui import TextFields
from manygui import TextAreas
from manygui import Frames
from manygui import Windows
from manygui import Applications

class ComponentMixin:
    """Base class for all components"""
    class _upstream:
        """Container for attributes handled by the upstream backend.

        As dummygui does not have upstream backend, they are stored here."""
        class _attributes:
            pass

        @classmethod
        def get(cls, name, default=None):
            """Get an attribute, and set it to the `default` parameter, if the
            attribute does not exist."""
            if name not in cls._attributes.__dict__:
                setattr(cls._attributes, name, default)
            return getattr(cls._attributes, name)

        @classmethod
        def set(cls, name, value):
            setattr(cls._attributes, name, value)

    def triggerEvent(self, event):
        Events.send(self, event)

    def _is_created(self):
        return True

    def _ensure_created(self):
        return True

    def _ensure_events(self):
        pass

    def _ensure_geometry(self):
        pass

    def _ensure_visibility(self):
        pass

    def _ensure_enabled_state(self):
        pass

    def _ensure_destroyed(self):
        pass

class Canvas(ComponentMixin, Canvases.AbstractCanvas):
    def drawPolygon(self, pointlist, edgeColor=None, edgeWidth=None,
            fillColor=None, closed=0):
        pass

class Label(ComponentMixin, Labels.AbstractLabel):
    def _ensure_text(self):
        pass

class ListBox(ComponentMixin, ListBoxes.AbstractListBox):
    def _ensure_items(self):
        pass
    def _ensure_selection(self):
        pass

class Button(ComponentMixin, Buttons.AbstractButton):
    def _ensure_text(self):
        pass

class CheckBox(ComponentMixin, CheckBoxes.AbstractCheckBox):
    def _ensure_state(self):
        pass
    def _ensure_text(self):
        pass

class RadioButton(ComponentMixin, RadioButtons.AbstractRadioButton):
    def _ensure_state(self):
        pass
    def _ensure_text(self):
        pass

class TextField(ComponentMixin, TextFields.AbstractTextField):
    def _ensure_editable(self):
        pass
    def _ensure_text(self):
        pass
    def _ensure_selection(self):
        pass

    def _backend_selection(self):
        return self._upstream.get('selection', (0, 0))
    def _backend_text(self):
        return self._upstream.get('text', '')

class TextArea(ComponentMixin, TextAreas.AbstractTextArea):
    def _ensure_editable(self):
        pass
    def _ensure_text(self):
        pass
    def _ensure_selection(self):
        pass

    def _backend_selection(self):
        return self._upstream.get('selection', (0, 0))
    def _backend_text(self):
        return self._upstream.get('text', '')

class Frame(ComponentMixin, Frames.AbstractFrame):
    pass

class Window(ComponentMixin, Windows.AbstractWindow):
    def _ensure_title(self):
        pass

class Application(ComponentMixin, Applications.AbstractApplication):
    def _mainloop(self):
        pass
