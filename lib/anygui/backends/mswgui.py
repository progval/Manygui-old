from anygui.backends import *
__all__ = anygui.__all__

from anygui.Utils import log

################################################################
import win32gui, win32con

# BUGS:
#
#    When I start test_listbox there is no way to control it
#    with the keyboard, even tabbing into the listbox.
#    Actually, it seems that the arrow keys don't work here
#    at all.

class ComponentMixin:
    # mixin class, implementing the backend methods
    #_height = -1 # -1 means default size in wxPython
    #_width = -1
    #_x = -1
    #_y = -1

    _hwnd = None
    _win_style_ex = 0

    _hfont = win32gui.GetStockObject(win32con.ANSI_VAR_FONT)
    
    def _is_created(self):
        return self._hwnd is not None

    def _ensure_created(self):
        app = application()
        if not self._hwnd:
            if self._container:
                parent = self._container._hwnd
            else:
                parent = 0
            self._hwnd = win32gui.CreateWindowEx(self._win_style_ex,
                self._wndclass,
                self._get_msw_text(),
                self._win_style,
                self._x,
                self._y,
                self._width,
                self._height,
                parent,
                0, # hMenu
                0, # hInstance
                None)
            app._hwnd_map[self._hwnd] = self
            if self._container:
                self._container._hwnd_map[self._hwnd] = self
            win32gui.SendMessage(self._hwnd,
                                 win32con.WM_SETFONT,
                                 self._hfont,
                                 0)
                                 
            return 1
        return 0

    def _ensure_events(self):
        pass

    def _ensure_geometry(self):
        if self._hwnd:
            win32gui.SetWindowPos(self._hwnd,
                                  0,
                                  self._x, self._y,
                                  self._width, self._height,
                                  win32con.SWP_NOACTIVATE | win32con.SWP_NOZORDER)

    def _ensure_visibility(self):
        if self._hwnd:
            if self._visible:
                win32gui.ShowWindow(self._hwnd, win32con.SW_SHOWNORMAL)
            else:
                win32gui.ShowWindow(self._hwnd, win32con.SW_HIDE)

    def _ensure_enabled_state(self):
        if self._hwnd:
            if self._enabled:
                win32gui.EnableWindow(self._hwnd, 1)
            else:
                win32gui.EnableWindow(self._hwnd, 0)

    def _ensure_destroyed(self):
        if self._container:
            del self._container._hwnd_map[self._hwnd]
        if self._hwnd:
            win32gui.DestroyWindow(self._hwnd)
        self._hwnd = None

    def _ensure_text(self):
        pass

##################################################################

class Label(ComponentMixin, AbstractLabel):
    #_width = 100 # auto ?
    #_height = 32 # auto ?
    _wndclass = "STATIC"
    #_text = "mswLabel"
    _win_style = win32con.SS_LEFT | win32con.WS_CHILD

    def _ensure_text(self):
        if self._hwnd:
            win32gui.SetWindowText(self._hwnd, str(self._text))

    def _get_msw_text(self):
        # return the text required for creation
        return str(self._text)

##################################################################

class ListBox(ComponentMixin, AbstractListBox):
    _wndclass = "LISTBOX"
    _win_style = win32con.WS_CHILD | win32con.WS_VSCROLL | win32con.WS_BORDER | win32con.LBS_NOTIFY
    _win_style_ex = win32con.WS_EX_CLIENTEDGE

    def _get_msw_text(self):
        return ""

    def _backend_selection(self):
        if self._hwnd:
            return win32gui.SendMessage(self._hwnd,
                                        win32con.LB_GETCURSEL,
                                        0,
                                        0)

    def _ensure_items(self):
        if self._hwnd:
            win32gui.SendMessage(self._hwnd,
                                 win32con.LB_RESETCONTENT, 0, 0)
            for item in map(str, list(self._items)):
                # FIXME: This doesn't work! Items get jumbled...
                win32gui.SendMessage(self._hwnd,
                                     win32con.LB_ADDSTRING,
                                     0,
                                     item)
                

    def _ensure_selection(self):
        if self._hwnd:
            win32gui.SendMessage(self._hwnd,
                                 win32con.LB_SETCURSEL,
                                 self._selection, 0)

    def _WM_COMMAND(self, hwnd, msg, wParam, lParam):
        # lParam: handle of control (or NULL, if not from a control)
        # HIWORD(wParam): notification code
        # LOWORD(wParam): id of menu item, control, or accelerator
        if wParam >> 16 == win32con.LBN_SELCHANGE:
            #self.do_action()
            send(self, 'select')

##################################################################

class Button(ComponentMixin, AbstractButton):
    _wndclass = "BUTTON"
    _win_style = win32con.BS_PUSHBUTTON | win32con.WS_CHILD
    #_text = "mswButton"

    def _get_msw_text(self):
        # return the text required for creation
        return str(self._text)

    def _WM_COMMAND(self, hwnd, msg, wParam, lParam):
        #log("Button._WM_COMMAND called, looking for %s==%s"%(wParam>>16,win32con.BN_CLICKED))
        # lParam: handle of control (or NULL, if not from a control)
        # HIWORD(wParam): notification code
        # LOWORD(wParam): id of menu item, control, or accelerator
        if (wParam >> 16) == win32con.BN_CLICKED:
            #self.do_action()
            send(self, 'click')

    def _ensure_text(self):
        if self._hwnd:
            win32gui.SetWindowText(self._hwnd, str(self._text))


class ToggleButtonMixin(ComponentMixin):

    def _get_msw_text(self):
        # return the text required for creation
        return str(self._text)

    def _ensure_text(self):
        if self._hwnd:
            win32gui.SetWindowText(self._hwnd, str(self._text))

    def _WM_COMMAND(self, hwnd, msg, wParam, lParam):
        # lParam: handle of control (or NULL, if not from a control)
        # HIWORD(wParam): notification code
        # LOWORD(wParam): id of menu item, control, or accelerator
        if (wParam >> 16) == win32con.BN_CLICKED:
            #self.do_action()
            send(self, 'click')

    def _ensure_state(self):
        if not self._hwnd:
            return
        if self.on:
            val = win32con.BST_CHECKED
        else:
            val = win32con.BST_UNCHECKED
        win32gui.SendMessage(self._hwnd, win32con.BM_SETCHECK, val, 0)

    def _WM_COMMAND(self, hwnd, msg, wParam, lParam):
        # lParam: handle of control (or NULL, if not from a control)
        # HIWORD(wParam): notification code
        # LOWORD(wParam): id of menu item, control, or accelerator
        if (wParam >> 16) != win32con.BN_CLICKED:
            return
        val = win32gui.SendMessage(self._hwnd, win32con.BM_GETSTATE, 0, 0)
        val = val & win32con.BST_CHECKED
        if val == self.on:
            return
        self.modify(on=val)
        #self.do_action()
        send(self, 'click')


class CheckBox(ToggleButtonMixin, AbstractCheckBox):
    _wndclass = "BUTTON"
    #_text = "mswCheckBox"
    _win_style = win32con.BS_AUTOCHECKBOX | win32con.WS_CHILD


class RadioButton(ToggleButtonMixin, AbstractRadioButton):
    _wndclass = "BUTTON"
    #_text = "mswCheckBox"
    _win_style = win32con.BS_AUTORADIOBUTTON | win32con.WS_CHILD
    
    def _ensure_created(self):
        # The first radiobutton in a group must have the wxRB_GROUP style
        if self._group and 0 == self._group._items.index(self):
            self._win_style |= win32con.WS_GROUP
        return ToggleButtonMixin._ensure_created(self)

    def _WM_COMMAND(self, hwnd, msg, wParam, lParam):
        # lParam: handle of control (or NULL, if not from a control)
        # HIWORD(wParam): notification code
        # LOWORD(wParam): id of menu item, control, or accelerator
        if (wParam >> 16) != win32con.BN_CLICKED:
            return
        #val = win32gui.SendMessage(self._hwnd, win32con.BM_GETSTATE, 0, 0)
        #val = val & win32con.BST_CHECKED
        #if val == self.on:
        #    return
        #self.modify(on=val)
        #self.do_action()
        if self.group is not None:
            self.group.modify(value=self.value)
        send(self, 'click')

##################################################################

### IMPORTANT NOTE: Until the 'copy-paste' structure has been
### fixed (e.g. with a common superclass), fixes in one of these
### text classes should probably also be done in the other.

class TextField(ComponentMixin, AbstractTextField):
    _wndclass = "EDIT"
    #_text = "mswTextField"
    _win_style = win32con.ES_NOHIDESEL | win32con.ES_AUTOHSCROLL | \
                 win32con.WS_CHILD | win32con.WS_BORDER
    _win_style_ex = win32con.WS_EX_CLIENTEDGE

    def _to_native(self, text):
        return text.replace('\n', '\r\n')

    def _from_native(self, text):
        return text.replace('\r\n', '\n')

    def _backend_text(self):
        if self._hwnd:
            return self._from_native(win32gui.GetWindowText(self._hwnd))

    #def _set_text(self, text):
    #    if self._hwnd:
    #        win32gui.SetWindowText(self._hwnd, self._to_native(text))

    def _backend_selection(self):
        #log("TextField._backend_selection")
        if self._hwnd:
            result = win32gui.SendMessage(self._hwnd,
                                          win32con.EM_GETSEL,
                                          0, 0)
            start, end = result & 0xFFFF, result >> 16
            #log("    start,end=%s,%s"%(start,end))
            # under windows, the natice widget contains
            # CRLF line separators
            text = self.text
            start -= text[:start].count('\n')
            end -= text[:end].count('\n')
            return start, end
            
    def _ensure_text(self):
        if self._hwnd:
            # avoid recursive updates
            if str(self._text) != self._backend_text():
                win32gui.SetWindowText(self._hwnd, self._to_native(str(self._text)))
        
    def _ensure_selection(self):
        #log("TextField._ensure_selection")
        if self._hwnd:
            start, end = self._selection
            text = self.text
            start += text[:start].count('\n')
            end += text[:end].count('\n')
            #log("    start,end=%s,%s"%(start,end))
            win32gui.SendMessage(self._hwnd,
                                 win32con.EM_SETSEL,
                                 start, end)

    def _ensure_editable(self):
        if self._hwnd:
            if self._editable:
                win32gui.SendMessage(self._hwnd,
                                     win32con.EM_SETREADONLY,
                                     0, 0)
            else:
                win32gui.SendMessage(self._hwnd,
                                     win32con.EM_SETREADONLY,
                                     1, 0)

##    def _ensure_events(self):
##        if self._hwnd:
##            EVT_TEXT_ENTER(self._hwnd, self._msw_id, self._msw_enterkey)

##    def _msw_enterkey(self, event):
##        self.do_action()

    def _get_msw_text(self):
        # return the text required for creation
        return self._to_native(str(self._text))

    def _WM_COMMAND(self, hwnd, msg, wParam, lParam):
        # HIWORD(wParam): notification code
        if (wParam >> 16) == win32con.EN_KILLFOCUS:
            self.modify(selection=self._backend_selection())
            self.modify(text=self._backend_text())


# FIXME: Inheriting TextField overrides TextArea defaults.
#        This is a temporary fix. (mlh20011222)
import anygui.Defaults # Deleted at the end of the module [xyzzy42]
class TextArea(anygui.Defaults.TextArea, TextField, AbstractTextArea):
    _win_style = TextField._win_style | win32con.ES_MULTILINE | \
                 win32con.ES_AUTOVSCROLL | win32con.ES_WANTRETURN

##################################################################

class ContainerMixin(ComponentMixin):
    def __init__(self):
        self._hwnd_map = {} # maps child window handles to instances
    
    def _finish_creation(self):
        #log("ContainerMixin._finish_creation %s"%self)
        for comp in self._contents:
            #log("  Adding %s"%comp)
            self._hwnd_map[comp._hwnd] = comp

    def _WM_COMMAND(self, hwnd, msg, wParam, lParam):
        #log("ContainerMixin _WM_COMMAND called for %s"%self)
        # lParam: handle of control (or NULL, if not from a control)
        # HIWORD(wParam): notification code
        # LOWORD(wParam): id of menu item, control, or accelerator
        app = application()
        try:
            child_window = self._hwnd_map[lParam]
        except KeyError:
            #log("NO SUCH CHILD WINDOW %s"%lParam)
            # we receive (when running test_textfield.py)
            # EN_CHANGE (0x300) and EN_UPDATE (0x400) notifications
            # here even before the call to CreateWindow returns.
            return
        #log("Dispatching to child %s"%child_window)
        child_window._WM_COMMAND(hwnd, msg, wParam, lParam)

    def _WM_SIZE(self, hwnd, msg, wParam, lParam):
        w, h = lParam & 0xFFFF, lParam >> 16
        dw = w - self._width
        dh = h - self._height
        self.modify(width=w)
        self.modify(height=h)
        self.resized(dw, dh)


class Frame(ContainerMixin, AbstractFrame):
    _win_style = win32con.WS_CHILD
    _win_style_ex = 0

    def __init__(self, *args, **kw):
        ContainerMixin.__init__(self)
        AbstractFrame.__init__(self, *args, **kw)

    def _get_msw_text(self):
        return ""

    def _finish_creation(self):
        ContainerMixin._finish_creation(self)
        AbstractFrame._finish_creation(self)


class Window(ContainerMixin, AbstractWindow):

    _win_style = win32con.WS_OVERLAPPEDWINDOW | win32con.WS_CLIPCHILDREN
    _win_style_ex = 0

    def __init__(self, *args, **kw):
        ContainerMixin.__init__(self)
        AbstractWindow.__init__(self, *args, **kw)

    def _ensure_geometry(self):
        # take account for title bar and borders
        if self._hwnd:
            import win32api
            win32gui.SetWindowPos(self._hwnd,
                                  0,
                                  self._x, self._y,
                                  self._width \
                                   + 2*win32api.GetSystemMetrics(win32con.SM_CXFRAME),
                                  self._height \
                                   + win32api.GetSystemMetrics(win32con.SM_CYCAPTION) \
                                   + 2*win32api.GetSystemMetrics(win32con.SM_CYFRAME),
                                  win32con.SWP_NOACTIVATE | win32con.SWP_NOZORDER)

    def _ensure_events(self):
        pass

    def _ensure_created(self):
        res = ComponentMixin._ensure_created(self)
        if res:
            win32gui.ShowWindow(self._hwnd, win32con.SW_HIDE)
            win32gui.UpdateWindow(self._hwnd)
        return res

    def _finish_creation(self):
        ContainerMixin._finish_creation(self)
        AbstractWindow._finish_creation(self)

    def _get_msw_text(self):
        return str(self._title)

    def _ensure_title(self):
        if self._hwnd:
            win32gui.SetWindowText(self._hwnd, self._title)

    def _WM_CLOSE(self, hwnd, msg, wParam, lParam):
        self.destroy()
        return 1

################################################################

class Application(AbstractApplication):
    _hwnd_map = {} # maps top level window handles to window instances
    _wndclass = None

    def __init__(self):
        AbstractApplication.__init__(self)
        if not self._wndclass:
            self._register_class()
        Window._wndclass = self._wndclass
        Frame._wndclass = self._wndclass
        global _app
        _app = self

    def _register_class(self):
        # register a window class for toplevel windows.
        wndclass = win32gui.WNDCLASS()
        wndclass.hbrBackground = win32con.COLOR_BTNFACE + 1
        wndclass.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        wndclass.hIcon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
        wndclass.lpszClassName = "msw.anygui.PythonWindow"
        wndclass.lpfnWndProc = self._wndproc
        self.__class__._wndclass = win32gui.RegisterClass(wndclass)

    def _wndproc(self, hwnd, msg, wParam, lParam):
        #log("_wndproc called with %s,%s,%s,%s"%(hwnd,msg,wParam,lParam))
        try:
            window = self._hwnd_map[hwnd]
        except:
            #log("NO WINDOW TO DISPATCH???")
            return win32gui.DefWindowProc(hwnd, msg, wParam, lParam)
        # there should probably be a better way to dispatch messages
        if msg == win32con.WM_DESTROY:
            app = application()
            app.remove(window)
            if not app._windows:
                win32gui.PostQuitMessage(0)
        if msg == win32con.WM_CLOSE:
            return window._WM_CLOSE(hwnd, msg, wParam, lParam)
        if msg == win32con.WM_SIZE:
            return window._WM_SIZE(hwnd, msg, wParam, lParam)
        if msg == win32con.WM_COMMAND:
            #log("Dispatching command to %s"%window)
            return window._WM_COMMAND(hwnd, msg, wParam, lParam)
        return win32gui.DefWindowProc(hwnd, msg, wParam, lParam)
        
    def _mainloop(self):
        win32gui.PumpMessages()

################################################################

# FIXME: Part of temporary fix earlier in file. (Search for xyzzy42)
del anygui.Defaults # Imported earlier

if __name__ == '__main__':
    from anygui import *

    app = Application()
    win = Window(title = "A Standard Window",
                 width = 300, height = 200)
    win.show()
    application().run()



