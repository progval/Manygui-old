"""Defaults for the manygui package.

Each class in module Defaults provides default attributes for the
widget of the same name, plus an attribute named _explicit_attributes
that lists the attributes which need to be set explicitly per instance
(currently, the latter defaults to "all defaulted attributes").
"""

from .Events import events

# For the Frame.place method:

direction = 'right'
space = 10

def _list_attributes(klass):
    klass._explicit_attributes = list(klass.__dict__.keys())

class Button:
    _text = 'Button'
    _DefaultEvent = events.LeftClickEvent
    _x = 0
    _y = 0
    _width = 80
    _height = 30
    _hmove = 0
    _vmove = 0
    _hstretch = 0
    _vstretch = 0
    _visible = 1
    _enabled = 1
_list_attributes(Button)

class Canvas:
    _text = 'Canvas' # Hardly needed...
    _DefaultEvent = events.LeftClickEvent
    _x = 0
    _y = 0
    _width = 400
    _height = 300
    _hmove = 0
    _vmove = 0
    _hstretch = 0
    _vstretch = 0
    _visible = 1
    _enabled = 1
_list_attributes(Canvas)

class CheckBox:
    _text = 'CheckBox'
    _DefaultEvent = events.ToggleEvent
    _x = 0
    _y = 0
    _width = 100
    _height = 15
    _hmove = 0
    _vmove = 0
    _hstretch = 0
    _vstretch = 0
    _visible = 1
    _enabled = 1
_list_attributes(CheckBox)

class Frame:
    _text = 'Frame' # Hardly needed...
    _DefaultEvent = events.LeftClickEvent
    _x = 0
    _y = 0
    _width = 400
    _height = 300
    _hmove = 0
    _vmove = 0
    _hstretch = 0
    _vstretch = 0
    _visible = 1
    _enabled = 1
_list_attributes(Frame)

class Label:
    _text = 'Label'
    _DefaultEvent = events.LeftClickEvent
    _x = 0
    _y = 0
    _width = 100
    _height = 15
    _hmove = 0
    _vmove = 0
    _hstretch = 0
    _vstretch = 0
    _visible = 1
    _enabled = 1
_list_attributes(Label)

class ListBox:
    _text = 'ListBox'
    _DefaultEvent = events.SelectEvent
    _x = 0
    _y = 0
    _width = 100
    _height = 100
    _hmove = 0
    _vmove = 0
    _hstretch = 0
    _vstretch = 0
    _visible = 1
    _enabled = 1
    _items = ()
    _selection = 0
_list_attributes(ListBox)

class RadioButton:
    _text = 'RadioButton'
    _DefaultEvent = events.LeftClickEvent
    _x = 0
    _y = 0
    _width = 100
    _height = 15
    _hmove = 0
    _vmove = 0
    _hstretch = 0
    _vstretch = 0
    _visible = 1
    _enabled = 1
_list_attributes(RadioButton)

class RadioGroup:
    _items = None
    _value = None
    _DefaultEvent = events.SelectEvent
_list_attributes(RadioGroup)

class TextArea:
    _text = ''
    _DefaultEvent = events.TextInputEvent
    _x = 0
    _y = 0
    _width = 100
    _height = 100
    _hmove = 0
    _vmove = 0
    _hstretch = 0
    _vstretch = 0
    _visible = 1
    _enabled = 1
    _editable = 1
    _selection = (0, 0)
_list_attributes(TextArea)

class TextField:
    _text = ''
    _DefaultEvent = events.PressEnterEvent
    _x = 0
    _y = 0
    _width = 100
    _height = 25
    _hmove = 0
    _vmove = 0
    _hstretch = 0
    _vstretch = 0
    _visible = 1
    _enabled = 1
    _editable = 1
    _selection = (0, 0)
_list_attributes(TextField)

class Window:
    _text = 'Window'
    _DefaultEvent = events.CloseEvent
    _x = 30
    _y = 30
    _width = 400
    _height = 300
    _hmove = 0
    _vmove = 0
    _hstretch = 0
    _vstretch = 0
    _visible = 1
    _enabled = 1
    _title = 'Untitled'
_list_attributes(Window)

def shift_window():
    Window._x += 30
    Window._x %= 360
    Window._y += 30
    Window._y %= 360

