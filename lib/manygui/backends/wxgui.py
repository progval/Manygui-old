
from manygui.backends import *
__all__ = manygui.__all__

################################################################

from wxPython.wx import *

class ComponentMixin:
    # mixin class, implementing the backend methods

    _wx_comp = None
    _wx_id = None
    _wx_style = 0
    
    def _is_created(self):
        return self._wx_comp is not None

    def _ensure_created(self):
        if self._wx_comp is None:
            if self._container is not None:
                parent = self._container._get_panel()
            else:
                parent = None
            if self._wx_id is None:
                self._wx_id = wxNewId()
            if hasattr(self, '_get_wx_text'):
                frame = self._wx_class(parent,
                                       self._wx_id,
                                       self._get_wx_text(),
                                       style=self._wx_style)
            else:
                frame = self._wx_class(parent,
                                       self._wx_id,
                                       style=self._wx_style)
            self._wx_comp = frame
            return 1
        return 0

    def _get_panel(self):
        return self._wx_comp

    def _ensure_events(self):
        pass

    def _ensure_geometry(self):
        if self._wx_comp:
            self._wx_comp.SetPosition((int(self._x), int(self._y)))
            self._wx_comp.SetSize((int(self._width), int(self._height)))

    def _ensure_visibility(self):
        if self._wx_comp:
            self._wx_comp.Show(int(self._visible))

    def _ensure_enabled_state(self):
        if self._wx_comp:
            self._wx_comp.Enable(int(self._enabled))

    def _ensure_destroyed(self):
        if self._wx_comp:
            self._wx_comp.Destroy()
            self._wx_comp = None

    def _ensure_text(self):
        if self._wx_comp and hasattr(self._wx_comp, 'SetLabel'):
            self._wx_comp.SetLabel(str(self._text))

################################################################

class Label(ComponentMixin, AbstractLabel):
    _wx_class = wxStaticText
    _wx_style = wxALIGN_LEFT

    def _get_wx_text(self):
        # return the text required for creation
        return str(self._text)

################################################################

class ListBox(ComponentMixin, AbstractListBox):
    _wx_class = wxListBox
    _wx_style = wxLB_SINGLE # FIXME: Not used... But default?

    def _backend_selection(self):
        if self._wx_comp:
            return self._wx_comp.GetSelection()

    def _ensure_items(self):
        if self._wx_comp:
            for index in range(self._wx_comp.Number()):
                self._wx_comp.Delete(0)
            self._wx_comp.InsertItems(list(map(str, list(self._items))), 0)

    def _ensure_selection(self):
        if self._wx_comp:
            if self._wx_comp.Number() > 0:
                self._wx_comp.SetSelection(int(self._selection)) # Does not cause an event

    def _ensure_events(self):
        if self._wx_comp:
            EVT_LISTBOX(self._wx_comp, self._wx_id, self._wx_clicked)

    def _wx_clicked(self, event):
        send(self, 'select')

################################################################

class Button(ComponentMixin, AbstractButton):
    _wx_class = wxButton

    def _ensure_events(self):
        EVT_BUTTON(self._wx_comp, self._wx_id, self._wx_clicked)

    def _wx_clicked(self, evt):
        send(self, 'click')

    def _get_wx_text(self):
        return str(self._text)


class ToggleButtonMixin(ComponentMixin):

    def _ensure_state(self):
        if self._wx_comp is not None:
            self._wx_comp.SetValue(int(self._on))

    def _get_wx_text(self):
        # return the text required for creation
        return str(self._text)


class CheckBox(ToggleButtonMixin, AbstractCheckBox):
    _wx_class = wxCheckBox

    def _wx_clicked(self, evt):
        val = self._wx_comp.GetValue()
        if val == self._on:
            return
        self.modify(on=val)
        send(self, 'click')

    def _ensure_events(self):
        EVT_CHECKBOX(self._wx_comp, self._wx_id, self._wx_clicked)

class RadioButton(ToggleButtonMixin, AbstractRadioButton):
    _wx_class = wxRadioButton

    def _wx_clicked(self, evt):
        if evt.GetInt():
            if self.group is not None:
                self.group.modify(value=self.value)
            send(self, 'click')
    
    def _ensure_created(self):
        # FIXME: What about moving buttons between groups? Would that
        # require destruction and recreation? [mlh20011214]
        # The first radiobutton in a group must have the wxRB_GROUP style
        if self._group and 0 == self._group._items.index(self):
            self._wx_style |= wxRB_GROUP
        return ToggleButtonMixin._ensure_created(self)

    def _ensure_events(self):
        EVT_RADIOBUTTON(self._wx_comp, self._wx_id, self._wx_clicked)

################################################################

# IMPORTANT NOTE: Until the 'copy-paste' structure has been
# fixed (e.g. with a common superclass), fixes in one of these
# text classes should probably also be done in the other.

class TextField(ComponentMixin, AbstractTextField):
    _wx_class = wxTextCtrl

    def _backend_selection(self):
        if self._wx_comp:
            return self._wx_comp.GetSelection()


    def _backend_text(self):
        if self._wx_comp:
            return  self._wx_comp.GetValue()
            
    def _ensure_text(self):
        if self._wx_comp:
            # XXX Recursive updates seem to be no problem here,
            # wx does not seem to trigger the EVT_TEXT handler
            # when a new text equal to the old one is set.
            self._wx_comp.SetValue(str(self._text))

    def _ensure_selection(self):
        if self._wx_comp:
            start, end = self._selection
            self._wx_comp.SetSelection(int(start), int(end))

    def _ensure_editable(self):
        if self._wx_comp:
            self._wx_comp.SetEditable(int(self._editable))

    def _ensure_events(self):
        EVT_TEXT_ENTER(self._wx_comp, self._wx_id, self._wx_enterkey)
        EVT_KILL_FOCUS(self._wx_comp, self._wx_killfocus)

    def _wx_killfocus(self, event):
        self.modify(text=self._wx_comp.GetValue())

    def _wx_enterkey(self, event):
        send(self, 'enterkey')

    def _get_wx_text(self):
        # return the text required for creation
        # XXX From here or from model?
        return str(self._text)


# FIXME: 'Copy-Paste' inheritance... TA and TF could have a common wx
# superclass. The only differences are the _wx_style and event handling.
class TextArea(ComponentMixin, AbstractTextArea):
    _wx_class = wxTextCtrl
    _wx_style = wxTE_MULTILINE | wxHSCROLL

    def _backend_selection(self):
        if self._wx_comp:
            start, end = self._wx_comp.GetSelection()
            if sys.platform[:3] == 'win':
                # under windows, the native widget contains
                # CRLF line separators
                # XXX Is this a wxPython bug?
                text = self.text
                start -= text[:start].count('\n')
                end -= text[:end].count('\n')
            return start, end

    def _backend_text(self):
        if self._wx_comp:
            return  self._wx_comp.GetValue()
            
    def _ensure_text(self):
        if self._wx_comp:
            # XXX Recursive updates seem to be no problem here,
            # wx does not seem to trigger the EVT_TEXT handler
            # when a new text equal to the old one is set.
            self._wx_comp.SetValue(str(self._text))

    def _ensure_selection(self):
        if self._wx_comp:
            start, end = self._selection
            if sys.platform[:3] == 'win':
                # under windows, the natice widget contains
                # CRLF line separators
                # XXX Is this a wxPython bug?
                text = self.text
                start += text[:start].count('\n')
                end += text[:end].count('\n')
            self._wx_comp.SetSelection(int(start), int(end))

    def _ensure_editable(self):
        if self._wx_comp:
            self._wx_comp.SetEditable(int(self._editable))

    def _ensure_events(self):
        EVT_KILL_FOCUS(self._wx_comp, self._wx_killfocus)

    def _wx_killfocus(self, event):
        self.modify(text=self._wx_comp.GetValue())

    def _get_wx_text(self):
        # return the text required for creation
        # XXX From here or from model?
        return str(self._text)

################################################################

class Frame(ComponentMixin, AbstractFrame):
    _wx_class = wxPanel

################################################################

class Window(ComponentMixin, AbstractWindow):
    _wx_class = wxFrame
    _wx_style = wxDEFAULT_FRAME_STYLE | wxNO_FULL_REPAINT_ON_RESIZE
    _wx_frame = None

    def _ensure_geometry(self):
        # override this to set the CLIENT size (not the window size)
        # to take account for title bar, borders and so on.
        if self._wx_comp:
            self._wx_comp.SetPosition((int(self._x), int(self._y)))
            self._wx_comp.SetClientSize((int(self._width), int(self._height)))

    def _get_panel(self):
        return self._wx_frame
    
    def _ensure_created(self):
        result = ComponentMixin._ensure_created(self)
        if result:
            # Controls should be contained in a wxPanel (which
            # is itself contained in the wxFrame)
            # Using the default style gives us proper handling
            # of TAB to move between the controls.
            self._wx_frame = wxPanel(self._wx_comp, wxNewId())
        return result
    
    def _ensure_events(self):
        EVT_CLOSE(self._wx_comp, self._wx_close_handler)
        EVT_SIZE(self._wx_comp, self._wx_size_handler)

    def _ensure_title(self):
        if self._wx_comp:
            self._wx_comp.SetTitle(str(self._title))

    # wxPython event handlers receive an event as parameter
    def _wx_close_handler(self, evt):
        self.destroy()

    def _wx_size_handler(self, evt):
        w, h = evt.GetSize()
        self._wx_frame.SetSize((w, h))
        dw = w - self._width
        dh = h - self._height
        self.modify(width=w)
        self.modify(height=h)
        self.resized(dw, dh)

    def _get_wx_text(self):
        # return the text required for creation
        return str(self._title)

################################################################

class Application(AbstractApplication, wxApp):
    def __init__(self):
        AbstractApplication.__init__(self)
        wxApp.__init__(self, 0)
        
    def OnInit(self):
        return 1

    def _mainloop(self):
        self.MainLoop()

################################################################
