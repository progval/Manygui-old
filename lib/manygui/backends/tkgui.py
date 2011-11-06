from manygui.backends import *
__all__ = manygui.__all__

from tkinter import * # A bit risky
from operator import truth
import re, tkinter, os

# Figure out proper setting for Tk's "exportselection" option.
EXPORTSELECTION = 'true'
if os.name in ['nt', 'os2']:
    EXPORTSELECTION = 'false'

class ComponentMixin:
    # mixin class, implementing the backend methods
    # FIXME: Defaults...
    #_height = -1
    #_width = -1
    #_x = -1
    #_y = -1

    _tk_comp = None
    _tk_id = None
    _tk_style = 0
    _tk_opts = {}
    
    def _is_created(self):
        return self._tk_comp is not None

    def _ensure_created(self):
        if self._is_created(): return 0

        if self._container is None: parent = None
        else: parent = self._container._tk_comp

        component = self._tk_class(parent, **self._tk_opts)

        # FIXME: Should be handled by _ensure_title and _ensure_text
        if self._tk_class is Toplevel: #?
            component.title(self._get_tk_text())
        else:
            try:
                component.config(text=self._get_tk_text())
            except: # not all widgets have a 'text' property
                pass
            if self._tk_class is tkinter.Label:
                component.config(justify=self._tk_style, anchor=W)

        try:
            component.configure(exportselection=EXPORTSELECTION)
        except:
            pass            

        self._tk_comp = component

        return 1

    def _ensure_events(self):
        pass

    def _show(self):
        self._tk_comp.place(x=self._x, y=self._y,
                            width=self._width, height=self._height)

    def _hide(self):
        self._tk_comp.place_forget()

    def _ensure_geometry(self):
        if self._tk_comp and self._visible: self._show()

    def _ensure_visibility(self):
        if self._tk_comp:
            if self._visible: self._show()
            else: self._hide()

    def _ensure_enabled_state(self):
        if self._tk_comp:
            if self._enabled: newstate = NORMAL
            else: newstate = DISABLED
            try: self._tk_comp.config(state=newstate)
            except TclError: pass # Widget doesn't support -state

    def _ensure_destroyed(self):
        if self._tk_comp:
            self._tk_comp.destroy()
            self._tk_comp = None

    def _get_tk_text(self):
        # helper function for creation: return text needed for creation
        # (normally _text, maybe _title or other depending on the class)
        return self._text

    def _ensure_text(self):
        pass

################################################################

# NOTE: This is not finished!

class Canvas(ComponentMixin, AbstractCanvas):

    # TODO: Add native versions of other drawing methods

    # FIXME: Has to store figures until backend component is
    #        created...

    _tk_class = tkinter.Canvas

    def __init__(self, *args, **kwds):
        AbstractCanvas.__init__(self, *args, **kwds)
        self._items = []
        self._deferred_methods = []

    def _ensure_created(self):
        result = ComponentMixin._ensure_created(self)
        self._tk_comp.configure(background='white')
        self._call_deferred_methods()
        return result

    def _call_deferred_methods(self):
        for methcall in self._deferred_methods:
            meth = getattr(self, methcall[0])
            meth(*methcall[1:])

    def clear(self):
        if self._tk_comp:
            list(map(self._tk_comp.delete, self._item_ids))

    def flush(self):
        if self._tk_comp:
            tkinter.Canvas.update(self._tk_comp)

    def drawPolygon(self, pointlist,
                    edgeColor=None, edgeWidth=None, fillColor=None, closed=True):
        if not self._tk_comp:
            self._deferred_methods.append(("drawPolygon",pointlist,edgeColor,
                                          edgeWidth,fillColor,closed))
            return
        if edgeColor is None:
            edgeColor = self.defaultLineColor
        if edgeWidth is None:
            edgeWidth = self.defaultLineWidth
        if fillColor is None:
            fillColor = self.defaultFillColor

        edgeColor = _convert_color(edgeColor)
        fillColor = _convert_color(fillColor)

        if closed:
            # FIXME: Won't work until component is created!
            item = self._tk_comp.create_polygon(pointlist,
                                                fill=fillColor,
                                                width=edgeWidth,
                                                outline=edgeColor)
        else:
            if fillColor:
                item = self._tk_comp.create_polygon(pointlist,
                                                    fill=fillColor,
                                                    outline='')
                self._items.append(item)
            d = {'fill': edgeColor, 'width': edgeWidth}
            item = self._tk_comp.create_line(*pointlist, **d)
            self._items.append(item)

    def _ensure_events(self):
        if self._tk_comp:
            self._tk_comp.bind('<ButtonRelease-1>', self._tk_clicked)

    def _tk_clicked(self, event):
        send(self, events.LeftClickEvent(x=event.x, y=event.y))

def _convert_color(c):
    if c is None or c is colors.transparent: return ''
    return '#%02X%02X%02X' % \
           (int(c.red*255), int(c.green*255), int(c.blue*255))

################################################################

class Label(ComponentMixin, AbstractLabel):
    #_width = 100 # auto ?
    #_height = 32 # auto ?
    _tk_class = tkinter.Label
    _tk_style = LEFT

    def _ensure_text(self):
        if self._tk_comp:
            # FIXME: Wrong place for the style...
            # FIXME: anchor assumes LEFT
            self._tk_comp.config(text=self._text, justify=self._tk_style, anchor=W)

################################################################

class ScrollableListBox(tkinter.Frame):

    # Replacement for Tkinter.Listbox

    _delegated_methods = """get configure bind curselection delete insert
    select_clear select_set""".split()

    def __init__(self, *args, **kw):
        tkinter.Frame.__init__(self, *args, **kw)

        self._yscrollbar = tkinter.Scrollbar(self)
        self._yscrollbar.pack(side=RIGHT, fill=Y)

        self._listbox = tkinter.Listbox(self,
                                        yscrollcommand=self._yscrollbar.set,
                                        selectmode="single")
        self._listbox.pack(side=LEFT, expand=YES, fill=BOTH)
        self._yscrollbar.config(command=self._listbox.yview)

        for delegate in self._delegated_methods:
            setattr(self, delegate, getattr(self._listbox, delegate))

class ListBox(ComponentMixin, AbstractListBox):
    _tk_class = ScrollableListBox

    def _backend_selection(self):
        if self._tk_comp:
            selection = self._tk_comp.curselection()[0]
            try:
                selection = int(selection)
            except ValueError: pass
            return selection

    def _ensure_items(self):
        if self._tk_comp:
            self._tk_comp.delete(0, END)
            for item in self._items:
                self._tk_comp.insert(END, str(item))

    def _ensure_selection(self):
        if self._tk_comp:
            self._tk_comp.select_clear(self._selection)
            self._tk_comp.select_set(self._selection)

    def _ensure_events(self):
        if self._tk_comp:
            self._tk_comp.bind('<ButtonRelease-1>', self._tk_clicked)
            self._tk_comp.bind('<KeyRelease-space>', self._tk_clicked)

    def _tk_clicked(self, event):
        send(self)

################################################################

class ButtonBase(ComponentMixin):

    def _ensure_events(self):
        if self._tk_comp:
            self._tk_comp.bind('<Return>', self._tk_clicked) # Press enter key
            self._tk_comp.bind('<Button-1>', self._tk_clicked)
            self._tk_comp.bind('<ButtonRelease-1>', self._tk_released)

    def _tk_clicked(self, event):
        # With Tk, "click, press = press, None"
        send(self, events.LeftClickEvent())
        send(self, events.PressEvent())

    def _tk_released(self, event):
        send(self, events.ReleaseEvent())

    def _ensure_text(self):
        if self._tk_comp:
            self._tk_comp.configure(text=self._text)

class Button(ButtonBase, AbstractButton):
    _tk_class = Button

class ToggleButtonMixin(ButtonBase):

    def _ensure_events(self):
        ButtonBase._ensure_events(self)
        if self._tk_comp:
            self._tk_comp.config(command=self._tk_toggle)

    def _ensure_state(self):
        if self._tk_comp is not None:
            self._var.set(truth(self.on))

    def _ensure_created(self):
        result = ComponentMixin._ensure_created(self)
        if result:
            self._var = IntVar()
            self._tk_comp.config(variable=self._var, anchor=W)
        return result

    def _ensure_text(self):
        if self._tk_comp:
            self._tk_comp.configure(text=self._text)

    def _tk_toggle(self):
        self.modify(on=not self.on)
        send(self, events.ToggleEvent())

class CheckBox(ToggleButtonMixin, AbstractCheckBox):
    _tk_class = Checkbutton

class RadioButton(ToggleButtonMixin, AbstractRadioButton):
    _tk_class = Radiobutton

    def _tk_toggle(self):
        if self.group is None:
            self.modify(on=not self.on)
        else:
            self.group.modify(value=self.value)
        send(self)

    def _ensure_created(self):
        result = ToggleButtonMixin._ensure_created(self)
        if result:
            self._tk_comp.config(value=1) # FIXME: Shaky...
        return result

################################################################

class DisabledTextBindings:
    """ Mixin that abstracts out all behavior needed to get
    selectable-but-not-editable behavior out of Tk text widgets.
    We bind all keystrokes, passing them through to the underlying
    control when _editable is true, and ignoring all but select
    and copy keystrokes when _editable is false. The mixed-in
    class must provide and maintain the _editable attribute. """

    def _install_bindings(self):
        self._ctl = 0
        self._alt = 0
        self._shift = 0
        self._tk_comp.bind("<Key>", self._keybinding)
        self._tk_comp.bind("<KeyPress-Control_L>", self._ctldown)
        self._tk_comp.bind("<KeyRelease-Control_L>", self._ctlup)
        self._tk_comp.bind("<KeyPress-Alt_L>", self._altdown)
        self._tk_comp.bind("<KeyRelease-Alt_L>", self._altup)
        self._tk_comp.bind("<KeyPress-Shift_L>", self._shiftdown)
        self._tk_comp.bind("<KeyRelease-Shift_L>", self._shiftup)
        self._tk_comp.bind("<Key-Insert>", self._insertbinding)
        self._tk_comp.bind("<Key-Up>", self._arrowbinding)
        self._tk_comp.bind("<Key-Down>", self._arrowbinding)
        self._tk_comp.bind("<Key-Left>", self._arrowbinding)
        self._tk_comp.bind("<Key-Right>", self._arrowbinding)
        self._tk_comp.bind("<ButtonRelease>", self._insertbinding)

        # Easy place to put this - not _editable-related, but common
        # to all text widgets.
        self._tk_comp.bind("<Leave>", self._update_model)

    # Track modifier key state.
    def _ctldown(self, ev):
        self._ctl = 1
    def _ctlup(self, ev):
        self._ctl = 0
    def _altdown(self, ev):
        self._alt = 1
    def _altup(self, ev):
        self._alt = 0
    def _shiftdown(self, ev):
        self._shift = 1
    def _shiftup(self, ev):
        self._shift = 0

    def _keybinding(self, ev):
        """ This method binds all keys, and causes them to be
        ignored when _editable is not set. """
        if self._editable:
            return None
        else:
            # This is truly horrid. Please add appropriate
            # code for Mac platform, someone.
            if (ev.char == "\x03") or (ev.char == "c" and self._alt):
                # DON'T ignore this key: it's a copy operation.
                return None
            return "break"

    def _insertbinding(self,ev):
        # Overrides _keybinding for the Insert key.
        if self._editable:
            return None
        if self._ctl:
            # Allow copy.
            return None
        return "break"

    def _arrowbinding(self,ev):
        # This method's sole reason for existence is to allow arrows
        # to work even when _editable is false.
        return None

    def _update_model(self,ev):
        pass

class TextField(ComponentMixin, AbstractTextField, DisabledTextBindings):
    _tk_class = tkinter.Entry

    def _backend_text(self):
        if self._tk_comp:
            return self._tk_comp.get()

    def _backend_selection(self):
        if self._tk_comp:
            if self._tk_comp.select_present():
                start = self._tk_comp.index('sel.first')
                end = self._tk_comp.index('sel.last')
            else:
                start = end = self._tk_comp.index('insert')
            return start, end
            
    def _ensure_created(self):
        result = ComponentMixin._ensure_created(self)
        if result:
            self._install_bindings()
        return result

    def _ensure_text(self):
        if self._tk_comp:
            if self._text != self._tk_comp.get():
                self._tk_comp.delete(0, END)
                self._tk_comp.insert(0, self._text)

    def _ensure_selection(self):
        if self._tk_comp:
            start, end = self._selection
            self._tk_comp.selection_range(start, end)

    def _do_ensure_selection(self, ev=None):
        self._ensure_selection()

    def _ensure_editable(self):
        pass

    def _send_action(self, dummy): # FIXME: dummy...
        send(self)

    def _ensure_events(self):
        if self._tk_comp:
            self._tk_comp.bind('<KeyPress-Return>', self._send_action) # do_action
            if EXPORTSELECTION == 'false':
                self._tk_comp.bind('<KeyRelease-Tab>', self._do_ensure_selection)

    def _update_model(self, ev):
        self.modify(text=self._backend_text())

class ScrollableTextArea(tkinter.Frame):

    # Replacement for Tkinter.Text

    _delegated_methods = """bind config get mark_names index delete insert
    mark_set tag_add tag_remove tag_names configure""".split()

    def __init__(self, *args, **kw):
        tkinter.Frame.__init__(self, *args, **kw)
        
        self._yscrollbar = tkinter.Scrollbar(self)
        self._yscrollbar.pack(side=RIGHT, fill=Y)

        self._xscrollbar = tkinter.Scrollbar(self, orient=HORIZONTAL)
        self._xscrollbar.pack(side=BOTTOM, fill=X)
        
        self._textarea = tkinter.Text(self,
                                      yscrollcommand=self._yscrollbar.set,
                                      xscrollcommand=self._xscrollbar.set)
        self._textarea.pack(side=TOP, expand=YES, fill=BOTH)

        self._yscrollbar.config(command=self._textarea.yview)
        self._xscrollbar.config(command=self._textarea.xview)

        for delegate in self._delegated_methods:
            setattr(self, delegate, getattr(self._textarea, delegate))

class TextArea(ComponentMixin, AbstractTextArea, DisabledTextBindings):
    _tk_class = ScrollableTextArea

    def _ensure_created(self):
        result = ComponentMixin._ensure_created(self)
        if result:
            self._tk_comp.config(wrap=NONE)
            self._install_bindings()
        return result

    def _backend_text(self):
        if self._tk_comp:
            return self._tk_comp.get(1.0, END)[:-1] # Remove the extra newline. (Always?)

    def _to_char_index(self, idx):
        # This is no fun, but there doesn't seem to be an easier way than
        # counting the characters in each line :-(   -- jak
        txt = self._tk_comp
        idx = txt.index(idx)
        line, col = idx.split(".")
        line = int(line)
        tlen = 0
        for ll in range(1, line):
            tlen += len(txt.get("%s.0"%ll, "%s.end"%ll))
            tlen += 1
        tlen += int(col)
        return tlen

    def _backend_selection(self):
        if self._tk_comp:
            try:
                start = self._tk_comp.index('sel.first')
                end = self._tk_comp.index('sel.last')
            except TclError:
                start = end = self._tk_comp.index('insert')
                # Convert to character positions...
            start = self._to_char_index(start)
            end = self._to_char_index(end)
            return start, end

    def _ensure_text(self):
        if self._tk_comp:
            if self._text != self._tk_comp.get("1.0","end"):
                self._tk_comp.config(state=NORMAL) # Make sure we can change the text
                self._tk_comp.delete(1.0, END)
                self._tk_comp.insert(1.0, self._text)
                self._ensure_editable() # Make sure the state is sync'ed

    def _ensure_selection(self):
        if self._tk_comp:
            start, end = self._selection
            self._tk_comp.tag_remove('sel', '1.0', 'end')
            self._tk_comp.tag_add('sel', '1.0 + %s char' % start, '1.0 + %s char' % end)

    def _ensure_editable(self):
        # Inheriting from DisabledTextBindings nullifies the need for this. - jak
        pass

    def _update_model(self,ev):
        self.modify(text=self._tk_comp.get("1.0","end"))

################################################################

class Frame(ComponentMixin, AbstractFrame):
    _tk_class = tkinter.Frame
    #_tk_opts = {'relief':'raised','borderwidth':2}

#from manygui.Frames import FakeFrame
#class Frame(FakeFrame): pass

################################################################

class Window(ComponentMixin, AbstractWindow):
    _tk_class = Toplevel
    _tk_style = 0

    def _ensure_created(self):
        result = ComponentMixin._ensure_created(self)
        #if result:
        #    self._tk_comp.SetAutoLayout(1)
        return result

    def _ensure_visibility(self):
        if self._tk_comp:
            if self._visible:
                self._tk_comp.deiconify()
            else:
                self._tk_comp.withdraw()

    def _ensure_geometry(self):
        geometry = "%dx%d+%d+%d" % (self._width, self._height,self._x, self._y)
        if self._tk_comp:
            self._tk_comp.geometry(geometry)
    
    def _ensure_events(self):
        self._tk_comp.bind('<Configure>', self._tk_size_handler)
        self._tk_comp.protocol('WM_DELETE_WINDOW', self._tk_close_handler)

    def _ensure_title(self):
        if self._tk_comp:
            self._tk_comp.title(self._title)

    def _tk_close_handler(self):
        global _app
        self._tk_comp.destroy()
        self.destroy()
        _app._window_deleted()

    def _tk_size_handler(self, dummy):
        g = self._tk_comp.geometry()
        m = re.match('^(\d+)x(\d+)', g)
        w = int(m.group(1))
        h = int(m.group(2))
        dw = w - self._width
        dh = h - self._height
        self._width = w
        self._height = h
        self.resized(dw, dh)

    def _get_tk_text(self):
        return self._title

################################################################

class Application(AbstractApplication):
    def __init__(self):
        AbstractApplication.__init__(self)
        self._root = Tk()
        self._root.withdraw()
        # FIXME: Ugly...
        global _app
        _app = self

    def _window_deleted(self):
        if not self._windows:
            self._root.destroy()
    
    def _mainloop(self):
        self._root.mainloop()

################################################################
