"""txtgui.py is the curses/text binding for Anygui <http://www.anygui.org>.
"""
import sys
import os

from anygui.backends import *
from anygui.Exceptions import Error
from anygui.Utils import log

# Some useful event codes.
DOWN_ARROW=258
UP_ARROW=259
LEFT_ARROW=260
RIGHT_ARROW=261
ESCAPE=27
BACKSPACE=127
LEFT_BRACKET=91
WINMENU_EVENT=990
FOCUS_FORWARD_EVENT=991
FOCUS_BACKWARD_EVENT=992
REFRESH_EVENT=997
QUIT_EVENT=998
HELP_EVENT=999
COMMAND_EVENT=1000
SCROLL_LEFT=951
SCROLL_RIGHT=952
SCROLL_UP=953
SCROLL_DOWN=954
SELECT_BEGIN_EVENT=955
SELECT_END_EVENT=956

# Map of character codes to names.
_charnames = {ord(' '):'space',
              DOWN_ARROW:'down arrow',
              UP_ARROW:'up arrow',
              LEFT_ARROW:'left arrow',
              RIGHT_ARROW:'right arrow',
              ESCAPE:'ESC',
              BACKSPACE:'backspace',
              HELP_EVENT:'ESC-?',
              COMMAND_EVENT:'ESC-ESC',
              QUIT_EVENT:'ESC-q-u-i-t',
              SCROLL_LEFT:'ESC-leftarrow',
              SCROLL_RIGHT:'ESC-rightarrow',
              SCROLL_UP:'ESC-uparrow',
              SCROLL_DOWN:'ESC-downarrow',
              WINMENU_EVENT:'ESC-w',
              SELECT_BEGIN_EVENT:'ESC-s',
              SELECT_END_EVENT:'ESC-e',
              1:'^A',
              2:'^B',
              3:'^C',
              4:'^D',
              5:'^E',
              6:'^F',
              7:'^G',
              8:'^H',
              9:'^I',
              10:'linefeed (^J)',
              11:'^K',
              12:'^L',
              13:'return (^M)',
              14:'^N',
              15:'^O',
              16:'^P',
              17:'^Q',
              18:'^R',
              19:'^S',
              20:'^T',
              21:'^U',
              22:'^V',
              23:'^W',
              24:'^X',
              25:'^Y',
              26:'^Z'
              }

# Screen-management package.
_scr = None

_refresh_all_flag = 0
def _refresh_all():
    global _refresh_all_flag
    _refresh_all_flag = 1

_all_components = [] # List of all controls. Used for focus management.
_focus_control = None
_focus_capture_control = None
_focus_dir = 1
def _discard_focus():
    global _focus_control
    old_fc = _focus_control
    _focus_control = None
    old_fc._focus_lost()

def _add_to_focus_list(comp):
    """ Add comp to _all_components in the proper focus-visit position. """
    prev_comp = None
    if comp._container:
        # Find last control in the container in _all_components
        # that is not comp.
        c = comp._container
        prev_comp = c # Insert after container by default.
        rcs = c._contents[:]
        rcs.reverse()
        for cc in rcs:
            if cc is not comp:
                prev_comp = cc
                break
    if prev_comp and prev_comp in _all_components:
        ii = _all_components.index(prev_comp)
        _all_components.insert(ii+1,comp)
        return
    _all_components.append(comp)

def _remove_from_focus_list(comp):
    #_scr.dbg("Removing from focus list",comp,'\n')
    if _focus_control is comp:
        _app._change_focus()
    if _focus_control is comp:
        _discard_focus()
    try:
        _all_components.remove(comp)
    except ValueError:
        pass

def _in_focus_purview(comp):
    if _focus_capture_control is None:
        return 1
    return _contains(_focus_capture_control,comp)

def _contains(cont,comp):
    while comp:
        if comp == cont: return 1
        try:
            comp = comp._container
        except AttributeError:
            return 0
    return 0

def _set_scale(x,y):
    ComponentMixin._horiz_scale = float(x)/640.0
    ComponentMixin._vert_scale = float(y)/480.0

class ComponentMixin:
    """ Mixin class for components.
    We're really only using curses as a screen-addressing
    library, since its implementation of "windows" isn't
    really very much like a GUI window. """

    # We'll map coordinates according to these scaling factors.
    # This lets normal anygui programs run under curses without
    # having to scroll the screen. This might not be such a
    # good idea, but it's worth a try.
    _horiz_scale = 80.0/640.0
    _vert_scale = 24.0/480.0
    #_horiz_scale = 1.0
    #_vert_scale = 1.0

    # If true for a particular class or component, we'll draw
    # a border around the component when it's displayed.
    _border = 1 # For debugging.
    #_visible = 1
    _needs_container = 0
    #_title = "txtgui"
    _gets_focus = 1
    #_text = "txtgui"
    _use_text = 1
    _textx = 1
    _texty = 1
    _tiny_LLCORNER = ord('<')
    _tiny_LRCORNER = ord('>')

    # Event-handler maps.
    _event_map = {}
    _event_range_map = {}

    def _get_control_help(self):
        helpstr = ""
        if hasattr(self,"_help"):
            helpstr = helpstr + self._help + '\n\n'
        if type(self.__class__.__doc__) == type(""):
            helpstr = helpstr + self.__class__.__doc__
        return helpstr

    def _get_event_help(self):
        items = []
        evmap = self._event_map
        kk = list(evmap.keys())
        kk.sort()
        for ch in kk:
            f = evmap[ch]
            if f == ComponentMixin._ignore_event:
                continue
            doc = f.__doc__
            try:
                c = _charnames[ch]
            except KeyError:
                try:
                    c = chr(ch)
                except (TypeError,ValueError):
                    c = str(ch)
            if doc is not None:
                item = c+": "+str(doc)
                items += item.split('\n')
                items.append(' ')
        try:
            if self._container:
                items += self._container._get_event_help()
        except:
            a,b,c = sys.exc_info()
            items.append("*** Exception gathering help data!"+str(b))
        return items

    def __init__(self,*args,**kws):
        ##_scr.dbg("Creating %s"%self)
        self._curses_created = 0
        self._cpos = 1,1 # Cursor position when in focus.
        # Border characters:
        self._LVLINE = _scr.SCR_LVLINE
        self._RVLINE = _scr.SCR_RVLINE
        self._UHLINE = _scr.SCR_UHLINE
        self._LHLINE = _scr.SCR_LHLINE
        self._ULCORNER = _scr.SCR_ULCORNER
        self._URCORNER = _scr.SCR_URCORNER
        self._LLCORNER = _scr.SCR_LLCORNER
        self._LRCORNER = _scr.SCR_LRCORNER
        self._attr = _scr.ATTR_NORMAL

    def _is_visible(self):
        if self._visible: return self._container._is_visible()

    def _focus_gained(self):
        pass

    def _focus_lost(self):
        pass

    def _set_focus(self,val):
        #self._ensure_enabled_state()
        global _focus_control
        if val:
            _focus_control = self
            #_scr.dbg("_set_focus:",self._gets_focus,self._is_visible(),self._curses_created,_in_focus_purview(self),self)
            if self._gets_focus and self._is_visible() and self._curses_created \
               and _in_focus_purview(self):
                self._focus_gained()
                return
            else:
                _app._change_focus(_focus_dir)
        else:
            if _focus_control is self:
                _discard_focus()

    def _set_focus_capture(self,val):
        global _focus_capture_control
        if val:
            _focus_capture_control = self
            _app._change_focus()
        else:
            if _focus_capture_control is self:
                _focus_capture_control = None

    def _scale_xy(self,x,y):
        return (int(x*self._horiz_scale),int(y*self._vert_scale))
    def _scale_yx(self,y,x):
        nx,ny = self._scale_xy(x,y)
        return ny,nx

    def _screen_height(self):
        w,h = self._scale_xy(self.width,self.height)
        if h<1: h=1
        return h

    def _screen_width(self):
        w,h = self._scale_xy(self.width,self.height)
        if w<2: w=2
        return w

    def _effective_texty(self):
        return min(self._texty,self._screen_height()-1)

    def _get_screen_coords(self):
        if not self._curses_created: return 0,0
        #if self._needs_container and not self._container: return 0,0
        x,y = self._scale_xy(self.x,self.y)
        ##_scr.dbg("_gsc: %s,%s: %s"%(x,y,self._text))
        if not self._container:
            return x,y
        cx,cy = self._container._get_screen_coords()
        return x+cx, y+cy

    def _container_intersect(self,x,y,w,h):
        # Get the screen rectangle representing the intersection of
        # the component and its container.
        if not self._curses_created: return 0,0,0,0
        #if self._needs_container and not self._container: return 0,0,0,0
        if not self._container:
            return x,y,w,h
        cx,cy,cw,ch = self._container._get_bounding_rect()
        ix = max(x,cx)
        iy = max(y,cy)
        ix2 = min(x+w,cx+cw)
        iy2 = min(y+h,cy+ch)
        iw = ix2-ix
        ih = iy2-iy
        if iw<0: iw=0
        if ih<0: ih=0
        ##_scr.dbg("_container_intersect (%s,%s) %s,%s,%s,%s: %s"%(x,y,ix,iy,iw,ih,self))
        return ix,iy,iw,ih

    def _addstr(self,x,y,str,attr=0):
        if attr == 0:
            attr = self._attr
        sx,sy,w,h = self._get_bounding_rect()
        if y>=h: return
        x += sx
        y += sy
        _scr.addstr(x,y,str,sx+w-x,attr)

    def _get_bounding_rect(self):
        # Get the screen x,y,w,h of the visible portion of the component.
        # If the control is invisible or completely clipped, w and h
        # are both 0.
        if not self._visible or not self._curses_created:
            return 0,0,0,0
        x,y = self._get_screen_coords()
        ##_scr.dbg("%s,%s: %s"%(x,y,self))
        w,h = self._screen_width(), self._screen_height()
        x,y,w,h = self._container_intersect(x,y,w,h)
        return x,y,w,h

    def _redraw(self):
        ##_scr.dbg("Redrawing (%d) %s"%(self.refresh,self))
        if not self._curses_created: return
        ##_scr.dbg("Visible: %s"%self)
        #x,y = self._get_screen_coords()
        if self._visible:
            self._erase()
            self._draw_border()
            self._draw_contents()
            ety = self._effective_texty()
            #_scr.dbg("ety ",ety,self,self._height*self._vert_scale)
            if self._use_text:
                self._addstr(self._textx,ety,str(self._text))

    def _erase(self):
        if not self._curses_created: return
        x,y,w,h = self._get_bounding_rect()
        ##_scr.dbg("Erasing %s"%self)
        _scr.erase(x,y,w,h)

    def _draw_border(self):
        if not self._curses_created: return
        if not self._border: return
        x,y = self._get_screen_coords()
        w,h = self._screen_width(), self._screen_height()
        ##_scr.dbg("Screen coords %s for %s"%((x,y,w,h),self))
        x,y,w,h = self._container_intersect(x,y,w,h)
        if w == 0 or h == 0: return
        ##_scr.dbg("Container intersect %s for %s"%((x,y,w,h),self))

        llcorner = self._LLCORNER
        lrcorner = self._LRCORNER
        if self._screen_height() < 2:
            llcorner = self._tiny_LLCORNER
            lrcorner = self._tiny_LRCORNER
        else:
            for xx in range(x+1,x+w-1):
                _scr.addch(y,xx,self._UHLINE)
                _scr.addch(y+h-1,xx,self._LHLINE)
            for yy in range(y+1,y+h-1):
                _scr.addch(yy,x,self._LVLINE)
                _scr.addch(yy,x+w-1,self._RVLINE)
            _scr.addch(y,x,self._ULCORNER)
            _scr.addch(y,x+w-1,self._URCORNER)

        _scr.addch(y+h-1,x,llcorner)
        _scr.addch(y+h-1,x+w-1,lrcorner)

    def _draw_contents(self):
        if not self._curses_created: return
        pass

    def _ensure_focus(self):
        if not self._curses_created: return
        x,y = self._get_screen_coords()
        ##_scr.dbg("Ensuring focus %s,%s on %s"%(x,y,self))
        if _focus_control is self:
            ##_scr.dbg("Ensuring focus on ",self)
            ##_scr.dbg("   HAS FOCUS!")
            ety = self._effective_texty()
            #_scr.dbg("focus ety ",ety,self,self._height*self._vert_scale)
            _scr.move_cursor(x+self._textx,y+ety)

    def _handle_event(self,ev):
        handled = self._event_handler(ev)
        if handled: return 1
        if self._container:
            # Propagate unhandled events to container.
            return self._container._handle_event(ev)
        return 0

    def _event_handler(self,ev):
        try:
            handled = self._event_map[ev](self,ev)
            return handled
        except KeyError:
            for (lo,hi) in list(self._event_range_map.keys()):
                if ev>=lo and ev<=hi:
                    handled = self._event_range_map[(lo,hi)](self,ev)
                    return handled
        return 0

    def _ignore_event(self,ev):
        return 0

    # backend api

    def _is_created(self):
        return self._curses_created

    def _ensure_created(self):
        ##_scr.dbg("_ensure_created(): %s"%self)
        if self._curses_created:
            return 0
        if self._needs_container and not self._container:
            return 0
        self._curses_created = 1
        _add_to_focus_list(self)
        return 1

    def _ensure_geometry(self):
        ##_scr.dbg("Ensuring geometry",self.geometry,self)
        #_refresh_all()
        self._redraw()

    def _ensure_visibility(self):
        self._redraw()

    #def _ensure_visible(self):
    #    self._redraw()

    def _ensure_enabled_state(self):
        #_scr.dbg("ENSURING ENABLED",self)
        # UNTESTED!
        if not self._enabled:
            #_scr.dbg("   NOT ENABLED")
            self._gets_focus = 0
            if _focus_control is self:
                _app._change_focus()
        else:
            #_scr.dbg("   ENABLED")
            self._gets_focus = self.__class__._gets_focus

    def _ensure_destroyed(self):
        _scr.dbg("Ensuring destroyed: %s"%self)
        self.focus_capture = 0
        _remove_from_focus_list(self)
        self._erase()
        self._curses_created = 0

    def _ensure_events(self):
        pass

    def _ensure_editable(self):
        pass

    def _ensure_text(self):
        self._ensure_editable()
        #self._redraw()

class ContainerMixin(ComponentMixin):
    """ Special handling for containers. These are mostly the
    same, presentation-wise, as regular components, but they
    manage their focus differently. """

    def __init__(self,*args,**kws):
        ComponentMixin.__init__(self,*args,**kws)

    def _is_visible(self):
        if self._container:
            return ComponentMixin._is_visible(self)
        if self._visible: return 1
        return 0

    def _redraw(self):
        if not self._curses_created: return
        ComponentMixin._redraw(self)
        for comp in self._contents:
            comp._redraw()

    def _ensure_destroyed(self):
        _scr.dbg("Ensuring destroyed ",self)
        self.focus_capture = 0
        _remove_from_focus_list(self)
        for comp in self._contents:
            comp._ensure_destroyed()
        ##_scr.dbg("Focus on ",_focus_control,"after dtoy",self)
        self._erase()
        self._curses_created = 0

    def _ensure_focus(self):
        ##_scr.dbg("Ensuring focus in %s"%self)
        ComponentMixin._ensure_focus(self)
        for win in self._contents:
            win._ensure_focus()

    def _remove(self, comp):
        # Curses components MUST have a valid container
        # in order to destroy themselves. Since the
        # comp.destroy() call in Frame._remove() dissociates
        # the component from the container, we must
        # override Frame._remove().
        try:
            # Fix the focus.
            if _focus_control is self:
                _app._change_focus()

            comp._ensure_destroyed()
            self._contents.remove(comp)
            comp._set_container(None)

            ##_scr.dbg("Refreshing %s"%self)
            self._redraw()
        except ValueError:
            pass

class Label(ComponentMixin, AbstractLabel):

    _gets_focus = 0
    _texty = 0

    def __init__(self,*args,**kws):
        ComponentMixin.__init__(self,*args,**kws)
        AbstractLabel.__init__(self,*args,**kws)
        self._LVLINE = ord(' ')
        self._RVLINE = ord(' ')
        self._UHLINE = ord(' ')
        self._LHLINE = ord(' ')
        self._ULCORNER = ord(' ')
        self._URCORNER = ord(' ')
        self._LLCORNER = ord(' ')
        self._LRCORNER = ord(' ')

class ListBox(ComponentMixin, AbstractListBox):

    _use_text = 0

    def __init__(self,*args,**kws):
        ComponentMixin.__init__(self,*args,**kws)
        AbstractListBox.__init__(self,*args,**kws)
    
    def _ensure_items(self):
        pass

    def _ensure_selection(self):
        pass

    def _backend_selection(self):
        if self._curses_created:
            return self._selection

    def _draw_contents(self):
        lh = self._screen_height()-2
        start = 0
        if lh<len(self._items):
            start = self._selection - lh + 1
            if start<0: start = 0

        x=2;y=1
        for ii in range(start,len(self._items)):
            item = str(self._items[ii])
            if self._selection == ii:
                self._addstr(x-1,y,'>')
            self._addstr(x,y,item)
            y+=1
            if y>lh: return

    def _select_down(self,ev):
        """Move listbox selection down."""
        self._selection += 1
        if self._selection >= len(self._items):
            self.modify(selection=0)
        self._redraw()
        return 1

    def _select_up(self,ev):
        """Move listbox selection up."""
        self._selection -= 1
        if self._selection < 0:
            self.modify(selection=len(self._items)-1)
        self._redraw()
        return 1

    def _do_click(self,ev):
        """Click on selected item."""
        send(self,'select')

    _event_map = { DOWN_ARROW:_select_down,
                   UP_ARROW:_select_up,
                   ord(' '):_do_click }

from .bmpascii import *
from anygui.Colors import black,white
class Canvas(ComponentMixin, AbstractCanvas):
    #_text = "Canvas not supported in text mode."
    _gets_focus = 0
    _use_text = 0

    def __init__(self,*args,**kws):
        ComponentMixin.__init__(self,*args,**kws)
        AbstractCanvas.__init__(self,*args,**kws)
        self._must_render = 1
        w,h = self._screen_width(),self._screen_height()
        self._bmpw = w*4
        self._bmph = h*6
        line = [0] * (self._bmpw+1)
        self._bitmap = []
        for ll in range(self._bmph+1):
            self._bitmap.append(line[:])
        self._scalew = float(self._bmpw)/float(self._width)
        self._scaleh = float(self._bmph)/float(self._height)
        #log("w,h = ",self._width,self._height)
        #log("bmpw,bmph = ",self._bmpw,self._bmph)
        #log("scalew,scaleh = ",self._scalew,self._scaleh)

    def _draw_line(self,point1,point2,color=None):
        if color is None:
            color = self.defaultLineColor
        if color != white:
            color = 1
        else:
            color = 0
        x1,y1 = point1
        x2,y2 = point2
        #log("_draw_line",x1,y1,"->",x2,y2)
        if x1 == x2:
            if y1>y2: y2,y1 = y1,y2
            for y in range(y1,y2+1):
                ey = int(y*self._scaleh)
                ex = int(x1*self._scalew)
                #log("Setting x,y --> ez,ey",x1,y,ex,ey)
                try:
                    self._bitmap[ey][ex] = color
                except:
                    pass
            return
        if x1<0 or x1>self._width or x2<0 or x2>self._width:
            return
        if y1<0 or y1>self._height or y2<0 or y2>self._height:
            return

        if x1>x2:
            #x1,y1,x2,y2 = x2,y2,x1,y1
            x1,x2 = x2,x1
            y1,y2 = y2,y1
        # y = mx+b, so
        # y1 = m*x1+b
        # y2 = m*x2+b
        # y1-y2 = m*x1 - m*x2
        # y1-y2 = m(x1-x2)
        m = (float(y1)-float(y2))/(float(x1)-float(x2))
        # and
        b = float(y1)-m*float(x1)
        for x in range(x1,x2+1):
            y = m*x+b
            ey = int(y*self._scaleh)
            ex = int(x*self._scalew)
            #log("Setting x,y --> ez,ey",x,y,ex,ey)
            try:
                self._bitmap[ey][ex] = color
            except:
                pass
            #self._bitmap[ey][ex] = not self._bitmap[ey][ex]
    
    def drawLine(self, x1, y1, x2, y2, color=None, width=None):
        "Draw a straight line between x1,y1 and x2,y2."
        self._draw_line((x1,y1),(x2,y2),color)

    def drawPolygon(self, pointlist,
                    edgeColor=None, edgeWidth=None, fillColor=None, closed=0):
        #log("FILLING, fillColor is",fillColor)
        self._fillColor = fillColor
        for ip in range(len(pointlist)-1):
            self._draw_line(pointlist[ip],pointlist[ip+1],edgeColor)
        if closed:
            #log("CLOSED POLY",pointlist)
            self._draw_line(pointlist[-1],pointlist[0],edgeColor)
            self._fillPoly(pointlist)
        self._must_render = 1

    def _fillPoly(self,ps):
        if self._fillColor is None:
            return
        if self._fillColor != white:
            color = 1
        else:
            color = 0
        #log("FILLING, fillColor is",self._fillColor)
        x1 = 9999
        y1 = 9999
        x2 = 0
        y2 = 0
        for p in ps:
            if p[0]<x1:
                x1 = p[0]
            if p[0]>x2:
                x2 = p[0]
            if p[1]<y1:
                y1=p[1]
            if p[1]>y2:
                y2=p[1]
        #log("FILLING in rect",x1,y1,"x",x2,y2)
        for x in range(x1+1,x2-1):
            for y in range(y1+1,y2-1):
                if self._pnpoly(ps,x,y):
                    #log(x,y,"is in poly",ps)
                    ey = int(y*self._scaleh)
                    ex = int(x*self._scalew)
                    #log("Clearing x,y --> ez,ey",x,y,ex,ey)
                    try:
                        self._bitmap[ey][ex] = color
                    except:
                        pass
                    #self._bitmap[ey][ex] = not self._bitmap[ey][ex]

    def _render(self):
        if not self._must_render: return
        self._must_render = 0
        self._str = bmp2ascii(self._bitmap)

    def _draw_contents(self):
        self._render()
        strs = self._str.split('\n')
        y = 0
        for line in strs:
            self._addstr(0,y,line)
            y += 1
        
    def _pnpoly(self,ps, x, y):
        i=0
        j=0
        c=0
        npol = len(ps)
        for i,j in zip(list(range(0,npol)),list(range(-1,npol-1))):
            if ((((ps[i][1]<=y) and (y<ps[j][1])) or
                 ((ps[j][1]<=y) and (y<ps[i][1]))) and
                (x < (ps[j][0] - ps[i][0]) * (y - ps[i][1]) / (ps[j][1] - ps[i][1]) + ps[i][0])):
                c = not c
        return c

class Button(ComponentMixin, AbstractButton):

    def __init__(self,*args,**kws):
        ComponentMixin.__init__(self,*args,**kws)
        AbstractButton.__init__(self,*args,**kws)
        #self._LVLINE = ord('<')
        #self._RVLINE = ord('>')
        #self._UHLINE = ord(' ')
        #self._LHLINE = ord(' ')
        #self._ULCORNER = ord('<')
        #self._URCORNER = ord('>')
        #self._LLCORNER = ord('<')
        #self._LRCORNER = ord('>')
        self._attr = _scr.ATTR_UNDERLINE

    #def __str__(self): return "Button "+self._text

    def _do_click(self,ev):
        """Click on button."""
        send(self,'click')

    _event_map = { ord(' '):_do_click }

class ToggleButtonMixin(ComponentMixin):

    _textx = 2
    _on_ind = '+'
    _off_ind = '-'

    def __init__(self,value=0,*args,**kws):
        ComponentMixin.__init__(self,*args,**kws)
        self.modify(value=value)

    def _curs_clicked(self,ev):
        """Click on button."""
        self.modify(on=not self.on) # FIXME: ??
        self._redraw()
        send(self, 'click')

    _event_map = { ord(' '):_curs_clicked }

    def _ensure_state(self):
        pass
        #self._redraw()

    def _draw_contents(self):
        ind = self._off_ind
        if self.on:
            ind = self._on_ind
        ety = self._effective_texty()
        self._addstr(self._textx-1,ety,ind)

class CheckBox(ToggleButtonMixin, AbstractCheckBox):

    _border = 0

    def __init__(self,*args,**kws):
        ToggleButtonMixin.__init__(self,*args,**kws)
        AbstractCheckBox.__init__(self,*args,**kws)
    
class RadioButton(ToggleButtonMixin, AbstractRadioButton):

    _on_ind = '*'
    _off_ind = '.'
    _border = 0

    def __init__(self,*args,**kws):
        ToggleButtonMixin.__init__(self,*args,**kws)
        AbstractRadioButton.__init__(self,*args,**kws)

    def _curs_clicked(self,ev):
        """Click on button."""
        if self.group is not None:
            self.group.modify(value=self.value)
        send(self, 'click')

    _event_map = { ord(' '):_curs_clicked }

class DisabledTextBindings: pass

import string
class TextMixin(ComponentMixin):

    _use_text = 0 # Prevent naive text presentation.

    def __init__(self,*args,**kws):
        ComponentMixin.__init__(self,*args,**kws)
        self._tpos=0
        self._cur_pos=(1,1)
        self._cur_line = 0
        self._cur_col = 0
        self._startline = 0
        self._startcol = 0
        #self._curs_selection = (0,0)
        self._curs_text = str(self._text)

    def _ensure_editable(self):
        #_scr.dbg("ENSURING EDITABLE",self)
        # UNTESTED!
        if not self._editable:
            #_scr.dbg("   NOT EDITABLE")
            self._gets_focus = 0
            if _focus_control is self:
                _app._change_focus()
        else:
            #_scr.dbg("   EDITABLE")
            self._gets_focus = self.__class__._gets_focus

    def _ensure_focus(self):
        if not self._curses_created: return
        x,y = self._get_screen_coords()
        ##_scr.dbg("Ensuring focus %s,%s on %s"%(x,y,self))
        if _focus_control is self:
            ##_scr.dbg("Ensuring focus on ",self)
            ##_scr.dbg("   HAS FOCUS!")
            #ety = self._effective_texty()
            #_scr.dbg("focus ety ",ety,self,self._height*self._vert_scale)
            tx,ty = self._cur_pos
            _scr.move_cursor(x+tx+1,y+ty+1)

    def _ensure_selection(self):
        pass
        #st,en = self._selection
        #self._curs_selection = (st,en)

    def _ensure_text(self):
        self._curs_text = str(self._text)
        self._redraw()

    def _backend_selection(self):
        _scr.dbg("BACKEND_SELECTION",self._selection)
        #return self._curs_selection
        if self._curses_created:
            return self._selection

    def _ensure_editable(self):
        pass

    def _backend_text(self):
        if self._curses_created:
            return str(self._curs_text)

    def _focus_lost(self):
        self.modify(text=self._curs_text)

    ### Event handlers ###
    def _backspace(self,ev):
        """Erase character before cursor."""
        if not self._editable: return
        if self._tpos < 1: return 1
        #self.modify(text=self._text[:self._tpos-1] + self._text[self._tpos:])
        self._curs_text=self._curs_text[:self._tpos-1] + self._curs_text[self._tpos:]
        self._tpos -= 1
        self._redraw()
        return 1

    def _insert(self,ev):
        """Insert character before cursor."""
        if not self._editable: return
        if not chr(ev) in string.printable:
            return 0
        #self.modify(text=self._text[:self._tpos] + chr(ev) + self._text[self._tpos:])
        self._curs_text=self._curs_text[:self._tpos] + chr(ev) + self._curs_text[self._tpos:]
        self._tpos += 1
        self._redraw() # FIXME: only really need to redraw current line.
        return 1

    def _back(self,ev):
        """Move cursor back one character."""
        self._tpos -= 1
        if self._tpos<0: self._tpos=0
        self._redraw()
        return 1

    def _fwd(self,ev):
        """Move cursor forward one character."""
        self._tpos += 1
        if self._tpos>len(self._curs_text): self._tpos=len(self._curs_text)
        self._redraw()
        return 1

    def _change_focus(self,ev):
        """Focus on the next control."""
        _app._change_focus()
        return 1

    def _down_line(self,ev):
        """Move cursor down one line."""
        self._move_line(1)
        return 1
        
    def _up_line(self,ev):
        """Move cursor up one line."""
        self._move_line(-1)
        return 1

    def _select_start(self,ev):
        """Set the start of the selection to the current
        cursor location."""
        st,en = self._selection
        _scr.dbg("SELECTION START 1:",st,en)
        st = self._tpos
        if en<st: en = st
        #self._curs_selection=(st,en)
        self.modify(selection=(st,en))
        _scr.dbg("SELECTION START:",st,en)
        self._redraw()
        return 1

    def _select_end(self,ev):
        """Set the end of the selection to the current
        cursor location."""
        st,en = self._selection
        _scr.dbg("SELECTION END 1:",st,en)
        en = self._tpos
        if en<st: st = en
        #self._curs_selection=(st,en)
        self.modify(selection=(st,en))
        _scr.dbg("SELECTION END:",st,en)
        self._redraw()
        return 1

    _event_map = {BACKSPACE:_backspace,
                  8:_backspace, #^H
                  DOWN_ARROW:_down_line,
                  UP_ARROW:_up_line,
                  #27:_change_focus,
                  LEFT_ARROW:_back,
                  RIGHT_ARROW:_fwd,
                  SELECT_BEGIN_EVENT:_select_start,
                  SELECT_END_EVENT:_select_end,
                  15:ComponentMixin._ignore_event
                  }
    _event_range_map = {(8,255):_insert}

    ### Event handler end ###

    def _move_line(self,n):
        lines = str(self._curs_text).split('\n')
        nlines = len(lines)
        self._cur_line += n
        cur_line_not_0 = 1
        if self._cur_line <= 0:
            self._cur_line = 0
            cur_line_not_0 = 0
        if self._cur_line >= nlines:
            self._cur_line = nlines-1
        lline = len(lines[self._cur_line])
        if lline<self._cur_col:
            self._cur_col = lline
        trunc_lines = lines[:self._cur_line]
        self._tpos = len(string.join(trunc_lines,'\n'))+self._cur_col+cur_line_not_0
        self._redraw()

    def _adjust_start(self):
        pass

    def _draw_contents(self):
        if self._screen_height()<3: return
        
        t = str(self._curs_text)
        x=1;y=1
        try:
            lines = t.split('\n')
        except:
            lines = "COULD NOT RENDER TEXT IN CONTROL"
        line,col = self._find_cursor_pos(lines)

        startline,startcol = self._find_relative_cpos(line,col,len(lines),len(lines[line]))
        sh = self._screen_height()-2

        #st,en = self._curs_selection
        st,en = self._selection
        st_line,st_col = self._find_lc_pos(lines,st)
        en_line,en_col = self._find_lc_pos(lines,en)
        self._selection_lc = st_line,st_col,en_line,en_col

        for li in range(0,min(sh,len(lines)-startline)):
            #_scr.dbg("start,line:",startline,li,self)
            line = lines[startline+li]
            parts = self._partition_line(line,startline+li,startcol)
            xx = x
            for (txt,attr) in parts:
                self._addstr(xx,y,txt,attr)
                xx += len(txt)
            y+=1

    def _partition_line(self,txt,line,startcol):
        st_line,st_col,en_line,en_col = self._selection_lc
        if line<st_line or line>en_line: return ((txt[startcol:],_scr.ATTR_NORMAL),)
        if line>st_line and line<en_line: return ((txt[startcol:],_scr.ATTR_SELECTED),)
        if line == st_line and line == en_line:
            # Case 1: entire selection off left.
            if en_col < startcol:
                return ((txt[startcol:],_scr.ATTR_NORMAL),)
            # Case 2: select start off left, select end in view.
            if st_col < startcol and en_col >= startcol:
                return ((txt[startcol:en_col],_scr.ATTR_SELECTED),
                        (txt[en_col:],_scr.ATTR_NORMAL))
            # Case 3: start and end in view.
            if st_col >= startcol and en_col >= startcol:
                return ((txt[startcol:st_col],_scr.ATTR_NORMAL),
                        (txt[st_col:en_col],_scr.ATTR_SELECTED),
                        (txt[en_col:],_scr.ATTR_NORMAL))
        if line == st_line:
            if st_col<startcol: return ((txt[startcol:],_scr.ATTR_SELECTED),)
            return ((txt[startcol:st_col],_scr.ATTR_NORMAL),
                    (txt[st_col:],_scr.ATTR_SELECTED))
        if line == en_line:
            if en_col<startcol: return ((txt[startcol:],_scr.ATTR_NORMAL),)
            return ((txt[startcol:en_col],_scr.ATTR_SELECTED),
                    (txt[en_col:],_scr.ATTR_NORMAL))


    def _find_relative_cpos(self,line,col,nlines,nchars):
        # Take the line,col position of the cursor in self._curs_text
        # and convert it, based on window size, into the window-
        # relative cursor position, which is stored in self._cpos.
        # Then return the line and column of the character that
        # should appear at the top-left corner.
        lh = self._screen_height()-3
        lw = self._screen_width()-3

        tl_line,tl_col,rline,rcol = (self._startline,
                                     self._startcol,
                                     line-self._startline,
                                     col-self._startcol)

        if rline<0: self._startline += rline
        if rline>=lh: self._startline += rline-lh
        if rcol<0: self._startcol += rcol
        if rcol>=lw: self._startcol += rcol-lw

        tl_line,tl_col,rline,rcol = (self._startline,
                                     self._startcol,
                                     line-self._startline,
                                     col-self._startcol)

        self._cur_pos = (rcol, rline)
        return tl_line,tl_col

    def _find_lc_pos(self,lines,tp):
        # Find line/col position of absolute text position.
        ll = 0
        tt = 0
        tl = len(lines)
        lastlen = 0
        line = 0
        while tt<=tp and ll<tl:
            lastlen = len(lines[ll])+1
            line = ll
            tt += lastlen
            ll += 1
        col=lastlen-(tt-tp)
        return line,col

    def _find_cursor_pos(self,lines):
        # Find line/col position of cursor.
        tp = self._tpos
        line,col = self._find_lc_pos(lines,tp)
        self._cur_line = line
        self._cur_col = col
        return line,col

class TextField(TextMixin, AbstractTextField):

    def __init__(self,*args,**kws):
        AbstractTextField.__init__(self,*args,**kws)
        TextMixin.__init__(self,*args,**kws)

    _event_map = {}
    _event_map.update(TextMixin._event_map)
    del _event_map[UP_ARROW] # No line control in TextFields.
    del _event_map[DOWN_ARROW]
    _event_map[ord('\n')] = TextMixin._change_focus

class TextArea(TextMixin, AbstractTextArea):

    def __init__(self,*args,**kws):
        AbstractTextArea.__init__(self,*args,**kws)
        TextMixin.__init__(self,*args,**kws)

class Frame(ContainerMixin, AbstractFrame):

    _gets_focus = 0
    _texty = 0
    _text = ""

    def __init__(self,*args,**kws):
        ContainerMixin.__init__(self,*args,**kws)
        AbstractFrame.__init__(self,*args,**kws)
        self.modify(text="")

class Window(ContainerMixin, AbstractWindow):
    """To move or resize a window, use Esc-W to open
the window menu, then type h,j,k, or l to move, and
H,J,K, or L to resize."""

    _needs_container = 0
    _texty = 0
    _use_text = 0

    def __init__(self,*args,**kws):
        ContainerMixin.__init__(self,*args,**kws)
        AbstractWindow.__init__(self,*args,**kws)
        self.modify(text="")
        ##_scr.dbg("%s:%s"%(self._title,self.geometry))

    def _ensure_destroyed(self):
        _scr.dbg("Ensuring destroyed: %s"%self)
        ContainerMixin._ensure_destroyed(self)
        _app.remove(self)
        _app._window_deleted()

    def _move_to_top(self):
        _app._move_to_top(self)

    def _redraw(self):
        if not self._curses_created: return
        ContainerMixin._redraw(self)
        self._addstr(2,0,self._title)

    def _ensure_title(self):
        #_scr.dbg("TITLE",self._title)
        #self._redraw()
        pass

    def _present_winmenu(self,ev):
        """Open window menu"""
        x,y = self._x,self._y
        w,h = int(round(12.1/self._horiz_scale)),int(round(4.1/self._vert_scale))
        self._omenu = WinMenuWindow(title="?Window")
        self._omenu._pwin = self
        self._omenu.geometry=(x,y,w,h)
        self._omenu._gets_focus=0

        x,y = int(round(1.1/self._horiz_scale)),int(round(1.1/self._vert_scale))
        w,h = int(round(10.1/self._horiz_scale)),int(round(1.1/self._vert_scale))
        self._canbtn = MenuButton(geometry=(x,y,w,h),text="Cancel")
        self._omenu.add(self._canbtn)
        link(self._canbtn,self._cancel_close)

        x,y = int(round(1.1/self._horiz_scale)),int(round(2.1/self._vert_scale))
        self._clbtn = MenuButton(geometry=(x,y,w,h),text="Close")
        self._omenu.add(self._clbtn)
        link(self._clbtn,self._close)

        _app.add(self._omenu)
        self._omenu.focus_capture = 1
        
    _event_map = {WINMENU_EVENT:_present_winmenu}

    def _curs_resized(self,dw,dh):
        self.resized(dw,dh)

    def _handle_wm_event(self,ch):
        hinc = int(round(1.1/self._horiz_scale))
        vinc = int(round(1.1/self._vert_scale))
        
        if ch == ord('h'):
            self.x -= hinc
            self._omenu.x -= hinc
            return 1
        if ch == ord('l'):
            self.x += hinc
            self._omenu.x += hinc
            return 1
        if ch == ord('j'):
            self.y += vinc
            self._omenu.y += vinc
            return 1
        if ch == ord('k'):
            self.y -= vinc
            self._omenu.y -= vinc
            return 1

        if ch == ord('H'):
            self.width -= hinc
            self._curs_resized(-hinc,0)
            return 1
        if ch == ord('L'):
            self.width += hinc
            self._curs_resized(hinc,0)
            return 1
        if ch == ord('J'):
            self.height += vinc
            self._curs_resized(0,vinc)
            return 1
        if ch == ord('K'):
            self.height -= vinc
            self._curs_resized(0,-vinc)
            return 1
        return 0

    def _close(self,*args,**kws):
        ##_scr.dbg("CLOSING %s"%self)
        self._omenu._pwin = None
        self._omenu.destroy()
        self.destroy()

    def _cancel_close(self,*args,**kws):
        self._omenu.destroy()
        self.focus = 1

class WinMenuWindow(Window):

    _gets_focus = 0

    def _handle_wmove_event(self,ev):
        """Move the window."""
        _scr.dbg("MOVE",chr(ev))
        return self._pwin._handle_wm_event(ev)

    def _handle_wconfig_event(self,ev):
        """Resize the window."""
        _scr.dbg("RESIZE",chr(ev))
        return self._pwin._handle_wm_event(ev)

    _event_map = {ord('h'):_handle_wmove_event,
                  ord('j'):_handle_wmove_event,
                  ord('k'):_handle_wmove_event,
                  ord('l'):_handle_wmove_event,
                  ord('H'):_handle_wconfig_event,
                  ord('J'):_handle_wconfig_event,
                  ord('K'):_handle_wconfig_event,
                  ord('L'):_handle_wconfig_event,
                  }
    
class MenuButton(Button):

    _texty = 0

    def __init__(self,*args,**kws):
        Button.__init__(self,*args,**kws)
        self._LLCORNER = ord('<')
        self._LRCORNER = ord('>')
        self._UHLINE = ' '
        self._LHLINE = ' '

class HelpWindow(Window):

    def __init__(self,*args,**kws):
        Window.__init__(self,*args,**kws)
        self._prev_ctrl = _focus_control
        self._prev_focus_capture = _focus_capture_control
        self._title = "INFORMATION (press 'Q' to dismiss)"
        self.modify(x=0)
        self.modify(y=0)
        self.modify(width=600)
        self.modify(height=400)
        lb = ListBox(geometry=(10,10,580,380))
        self.add(lb)
        self._populate_lb(lb)
        _app.add(self)
        self.focus_capture = 1

    def _populate_lb(self,lb):
        """Add docstrings for _prev_ctrl event handlers to lb."""
        items = ["---------------------------------------------------------------------",
                 "This is txtgui, the text/curses binding for Anygui.",
                 ""]
        if self._prev_ctrl:
            cls = self._prev_ctrl.__class__.__name__
            items += ["The current control is a "+cls+".",""]
            items += self._prev_ctrl._get_control_help().split('\n')
            items += ["","This " + cls +" responds to the following key bindings:",""]
            items += self._prev_ctrl._get_event_help()
        items += ["You can get this context-sensitive help screen at",
                  "any time by typing ESC-?. You can exit the",
                  "application by typing ESC, followed by the word",
                  "'quit' in lower-case, or by closing all the",
                  "application's windows.",
                  
                  "",
                  
                  "The main difference between the curses binding and",
                  "the text binding is that curses responds to characters",
                  "as soon as they are typed, whereas if the text binding is",
                  "used, you must press the <Return> key in order for",
                  "the application to respond to input. You may type",
                  "ESC-m if you need to send a return character",
                  "to the application.",

                  "",
                  
                  "ESC-f and ESC-b move forward and backward, respectively,",
                  "among the application's controls. Up and down arrow",
                  "move between controls, except in text controls,",
                  "where they move between lines. Z and z can be used",
                  "to zoom the presentation in and out. ESC-arrows",
                  "may be used to scroll the entire screen.",
                  
                  "",

                  "Some terminal emulation programs may not display the",
                  "borders of windows properly when using curses. If",
                  "borders are drawn using strange characters, set",
                  "the environment variable ANYGUI_ALTERNATE_BORDER",
                  "to a non-zero value."
                  
                  ]
        lb.items = items

    def _dismiss(self,ev):
        """Exit help and return to the previous window."""
        self.focus_capture = 0
        self.destroy()
        if self._prev_focus_capture:
            self._prev_focus_capture.focus_capture = 1
        if self._prev_ctrl:
            self._prev_ctrl.focus = 1

    #def _event_handler(self,ev):
    #    if ev == ord('q'): self._dismiss(ev)

    _event_map = {ord('q'):_dismiss,
                  ord('Q'):_dismiss,}

# If false, present an initial help window.
_inithelp = 0

# Character escape sequences, and the events we transform them
# into.
_escape_sequence_map = {
    (LEFT_BRACKET,65):UP_ARROW,
    (LEFT_BRACKET,66):DOWN_ARROW,
    (LEFT_BRACKET,67):RIGHT_ARROW,
    (LEFT_BRACKET,68):LEFT_ARROW,

    (LEFT_ARROW,):SCROLL_LEFT,
    (RIGHT_ARROW,):SCROLL_RIGHT,
    (UP_ARROW,):SCROLL_UP,
    (DOWN_ARROW,):SCROLL_DOWN,

    (ord('?'),):HELP_EVENT,

    (ord('q'),ord('u'),ord('i'),ord('t')):QUIT_EVENT,

    (ord('r'),):REFRESH_EVENT,

    (ord('w'),):WINMENU_EVENT,

    (ord('f'),):FOCUS_FORWARD_EVENT,
    (ord('b'),):FOCUS_BACKWARD_EVENT,

    # Convert ESC-m into Return, for textgui's benefit.
    (ord('m'),):ord('\n'),

    (ord('s'),):SELECT_BEGIN_EVENT,
    (ord('e'),):SELECT_END_EVENT,

    }

for seq in list(_escape_sequence_map.keys()):
    for i in range(1,len(seq)):
        _escape_sequence_map[seq[:i]] = None

class Application(AbstractApplication):
    def __init__(self):
        AbstractApplication.__init__(self)
        self._quit = 0
        _scr.scr_init()
        _set_scale(_scr._xsize,_scr._ysize)
        global _app
        _app = self

    def _window_deleted(self):
        ##_scr.dbg("WINDOW DELETED")
        if not self._windows:
            self._quit = 1
        else:
            _refresh_all()
            self._change_focus()

    def run(self):
        try:
            AbstractApplication.run(self)
        except:
            # In the event of an error, restore the terminal
            # to a sane state.
            _scr.scr_quit()

            # Pass the exception upwards
            (exc_type, exc_value, exc_traceback) = sys.exc_info()
            if hasattr(exc_value,"value"):
                print("Exception value:",exc_value.value)
            raise exc_type(exc_value).with_traceback(exc_traceback)
        else:
            # In the event of an error, restore the terminal
            # to a sane state.
            _scr.scr_quit()
            
    def _mainloop(self):
        # Present the initial help screen, without which the
        # UI remains forever mysterious.
        global _inithelp
        if not _inithelp and not os.getenv('ANYGUI_CURSES_NOHELP', 0):
            HelpWindow()
            _inithelp = 1

        # Establish the initial focus.
        self._change_focus()

        # Redraw the screen.
        _refresh_all()
        self._redraw_all()

        # The main event loop:
        while (not self._quit) and self._check_for_events():
            self._redraw_all()

    def _app_event_handler(self,ch):
        #_scr.dbg("APP_EVENT_HANDLER",ch)
        if ch == HELP_EVENT: # ESC-?
            HelpWindow()
        if ch == QUIT_EVENT: # ESC-quit
            wins = self._windows[:]
            for win in wins:
                win.destroy()
            return 0
        if ch == FOCUS_FORWARD_EVENT or ch == DOWN_ARROW:  # ^F,down
            self._change_focus(1)
        if ch == FOCUS_BACKWARD_EVENT or ch == UP_ARROW:  # ^B,up
            self._change_focus(-1)
        if ch == REFRESH_EVENT:
            _refresh_all()
        if ch == SCROLL_LEFT:
            ox,oy = _scr.get_origin()
            ox-=10
            _scr.set_origin(ox,oy)
            _refresh_all()
        if ch == SCROLL_RIGHT:
            ox,oy = _scr.get_origin()
            ox+=10
            _scr.set_origin(ox,oy)
            _refresh_all()
        if ch == SCROLL_UP:
            ox,oy = _scr.get_origin()
            oy-=10
            _scr.set_origin(ox,oy)
            _refresh_all()
        if ch == SCROLL_DOWN:
            ox,oy = _scr.get_origin()
            oy+=10
            _scr.set_origin(ox,oy)
            _refresh_all()

        if ch == ord('z'):
            ComponentMixin._horiz_scale /= 2.0
            ComponentMixin._vert_scale /= 2.0
            _refresh_all()
        
        if ch == ord('Z'):
            ComponentMixin._horiz_scale *= 2.0
            ComponentMixin._vert_scale *= 2.0
            _refresh_all()
        
        return 1

    def _translate_escape(self,ch):
        if ch != ESCAPE:
            return ch
        done=0
        chtuple=()
        while not done:
            ch = self._translate_escape(_scr.get_char())
            try:
                chtuple = chtuple + (ch,)
                result = _escape_sequence_map[chtuple]
                if type(result) == type(0):
                    return result
            except:
                # Invalid escape sequence.
                return ch

    def _check_for_events(self):
        ch = _scr.get_char()
        ch = self._translate_escape(ch)
        handled = 0
        if _focus_control is not None:
            handled = _focus_control._handle_event(ch)
        if not handled:
            return self._app_event_handler(ch)
        return 1

    def _redraw_all(self):
        global _refresh_all_flag
        if _refresh_all_flag:
            _scr.erase_all()
            for win in self._windows:
                win._redraw()
            _refresh_all_flag = 0
        ##_scr.dbg("redraw_all: %s"%self._windows)
        self._ensure_focus()
        _scr.refresh()

    def _change_focus(self,dir=1):
        #_scr.dbg("**** CHANGING FOCUS",dir)
        global _focus_dir
        _focus_dir = dir
        
        # If no focus, establish focus.
        if not _focus_control:
            for win in _all_components:
                win.focus = 1
                if _focus_control:
                    self._raise_focus_window()
                    return
            #_scr.dbg("NOFOCUS: FOCUS NOW ON",_focus_control,"\n")
            return
        
        # Move focus to the next control that can accept it.
        aclen = len(_all_components)
        #_scr.dbg("aclen:",aclen)
        tried = 0

        fc = _focus_control
        ii = _all_components.index(fc)
        _discard_focus()

        while not _focus_control and tried <= aclen:
            tried += 1
            ii += dir
            if ii>=aclen: ii = 0
            if ii<0: ii = aclen-1
            _all_components[ii].focus = 1

        #_scr.dbg("FOCUS NOW ON",_focus_control,"\n")
        self._raise_focus_window()

    #def _window_lost_focus(self,win):
    #    try:
    #        ii = self._windows.index(win)
    #        ii += 1
    #        if ii >= len(self._windows):
    #            ii = 0
    #    except ValueError:
    #        ii = 0
    #    try:
    #        self._windows[ii].focus = 1
    #    except IndexError:
    #        self._quit = 1

    def _ensure_focus(self):
        for win in self._windows:
            win._ensure_focus()

    def _raise_focus_window(self):
        if not _focus_control: return
        for win in self._windows:
            if _contains(win,_focus_control):
                self._move_to_top(win)

    def _move_to_top(self,win):
        if self._windows[-1] == win: return
        self._windows.remove(win)
        self._windows.append(win)
        _refresh_all()
