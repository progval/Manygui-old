from manygui.backends import *
__all__ = manygui.__all__

######################################################
from weakref import ref as wr
from PyQt4.QtCore import *
from PyQt4.QtGui import *

QString = str # Python 3 rules

TRUE = 1
FALSE = 0

from manygui import DEBUG
TMP_DBG = 1

class Fifo:
    """Basic reimplementation of queue.Queue, as Qt does not like it."""
    def __init__(self):
        self._queue1 = []
        self._queue2 = []
        self._lock = False
    def put(self, obj):
        if self._lock and self._queue1 == []:
            self._queue1, self._queue2, self._lock = self._queue2, [], False
        if self._lock:
            self._queue2.append(obj)
        else:
            self._queue1.append(obj)
    def getQueue(self):
        queue = self._queue1
        self._queue1, self._queue2 = self._queue1, []
        return queue

class ComponentMixin:
    _qt_comp = None
    _qt_style = None

    def _is_created(self):
        return self._qt_comp is not None

    def _ensure_created(self):
        if DEBUG: print('in _ensure_created of: ', self)
        if not self._qt_comp:
            if self._container:
                parent = self._container._qt_comp
            else:
                parent = None
            new_comp = self._qt_class(parent)
            if self._qt_class == QWindow:
                new_comp.setWindowTitle(self._get_qt_title())
            if hasattr(new_comp, 'set_container'):
                new_comp.set_container(self)
            self._qt_comp = new_comp
            return 1
        return 0

    def _ensure_events(self):
        pass

    def _ensure_geometry(self):
        if self._qt_comp:
            if DEBUG: print('in _ensure_geometry of: ', self._qt_comp)
            self._qt_comp.setGeometry(self._x,self._y,self._width,self._height)

    def _ensure_visibility(self):
        if self._qt_comp:
            if DEBUG: print('in qt _ensure_visibility: ', self._qt_comp)
            if self._visible:
                self._qt_comp.show()
            else:
                self._qt_comp.hide()

    def _ensure_enabled_state(self):
        if self._qt_comp:
            if DEBUG:
                print('in qt _ensure_enabled_state: ', self._qt_comp)
            self._qt_comp.setEnabled(self._enabled)

    def _ensure_destroyed(self):
        if self._qt_comp:
            if DEBUG: print('in qt _ensure_destroyed: ', self._qt_comp)
            try: self._connected = 0
            except: pass
            self._qt_comp.destroy()
            self._qt_comp = None

    def _backend_set_container(self, new):
        if self._qt_comp:
            self._qt_comp.setParent(new)

class EventFilter(QObject):
    _comp = None
    _events = {}

    def __init__(self, parent, events):
        QObject.__init__(self, parent._qt_comp)
        self._comp = wr(parent)
        self._events = events

    def eventFilter(self, object, event):
        #if DEBUG: print 'in eventFilter of: ', self._window_obj()._qt_comp
        type = event.type()
        if not type in list(self._events.keys()):
            return 0
        return self._events[type](self._comp(), event)

#########################################################

class QPaintableWidget(QWidget):
    _container = None

    def set_container(self, container):
        assert not self._container
        self._container = container

    _paint_callbacks = Fifo()

    def paintEvent(self, event):
        if DEBUG: print('in paintEvent of: ', self)
        painter = QPainter()
        painter.begin(self)
        try:
            for callback in self._paint_callbacks.getQueue():
                callback(painter)
        finally:
            painter.end()

    def mousePressEvent(self, event):
        if DEBUG: print('in mousePressEvent of: ', self)
        send(self._container, 'click', x=event.x(), y=event.y())

class Canvas(ComponentMixin, AbstractCanvas):
    _qt_class  = QPaintableWidget

    def drawPolygon(self, pointlist, edgeColor = None, edgeWidth=None,
            fillColor=None, closed=True):
        if DEBUG: print('in drawPolygon of: ', self)
        if edgeColor is None:
            edgeColor = self.defaultLineColor
        if edgeWidth is None:
            edgeWidth = self.defaultLineWidth
        if fillColor is None:
            fillColor = self.defaultFillColor
        pointlist = [QPointF(*x) for x in pointlist]

        def callback(painter):
            # Draw the shape
            pen = QPen()
            pen.setColor(QColor(edgeColor.red*255, edgeColor.green*255,
                    edgeColor.blue*255, edgeColor.alpha*255))
            pen.setWidth(edgeWidth)
            painter.setPen(pen)
            if not closed:
                # The only way is to move the pen backward to the first point
                reversed_pointlist = pointlist[:]
                reversed_pointlist.reverse()
                pointlist.extend(reversed_pointlist)
            polygon = QPolygonF(pointlist)
            painter.drawPolygon(polygon)

            # Fill the shape
            painter_path = QPainterPath()
            painter_path.addPolygon(polygon)
            if fillColor is not None or fillColor is not Colors.transparent:
                painter.fillPath(painter_path,
                        QColor(fillColor.red*255, fillColor.green*255,
                        fillColor.blue*255, fillColor.alpha*255))
        self._qt_class._paint_callbacks.put(callback)
        if self._qt_comp:
            self._qt_comp.update() # Calls self._qt_comp.paintEvent

    def _ensure_enabled_state(self):
        pass

#########################################################

class Label(ComponentMixin,AbstractLabel):
    _qt_class = QLabel
    _qt_style = Qt.AlignLeft | Qt.AlignVCenter

    def _ensure_created(self):
        result = ComponentMixin._ensure_created(self)
        if result:
            self._qt_comp.setAlignment(self._qt_style)
        return result

    def _ensure_text(self):
        if self._qt_comp:
            self._qt_comp.setText(self._get_qt_text())

    def _get_qt_text(self):
        return self._text

##########################################################

class ListBox(ComponentMixin, AbstractListBox):
    _qt_class = QListWidget
    _connected = 0

    def _backend_selection(self):
        if self._qt_comp:
            return int(self._qt_comp.currentItem())

    def _ensure_items(self):
        if self._qt_comp:
            self._qt_comp.clear()
            for item in self._items:
                self._qt_comp.insertItem(QString(str(item)),-1)

    def _ensure_selection(self):
        if self._qt_comp:
            self._qt_comp.setCurrentItem(int(self._selection))

    def _ensure_events(self):
        if DEBUG: print('in _ensure_events of: ', self)
        if self._qt_comp and not self._connected:
            qApp.connect(self._qt_comp, SIGNAL('highlighted(int)'),\
                         self._qt_item_select_handler)
            self._connected = 1

    def _qt_item_select_handler(self, index):
        if DEBUG: print('in _qt_item_select_handler of: ', self._qt_comp)
        self._selection = self._backend_selection()
        #send(self,'select',index=self._qt_comp.index(item),text=str(item.text()))
        send(self,'select')


################################################################

class ButtonBase(ComponentMixin):
    _connected = 0

    def _ensure_events(self):
        if self._qt_comp and not self._connected:
            if DEBUG: print('in _ensure_events of: ', self._qt_comp)
            self._qt_comp.clicked.connect(self._qt_click_handler)
            self._connected = 1

    def _ensure_text(self):
        if self._qt_comp:
            if DEBUG: print('in _ensure_text of: ', self._qt_comp)
            self._qt_comp.setText(self._get_qt_text())

    def _get_qt_text(self):
        if DEBUG: print('in _get_qt_text of: ', self)
        return QString(str(self._text))

class Button(ButtonBase, AbstractButton):
    _qt_class = QPushButton

    def _qt_click_handler(self):
        if DEBUG: print('in _qt_btn_clicked of: ', self._qt_comp)
        send(self,'click')

class ToggleButtonBase(ButtonBase):

    def _ensure_state(self):
        if DEBUG: print('in _ensure_state of: ', self._qt_comp)
        if self._qt_comp:
            if not self._qt_comp.isChecked() == self._on:
                self._qt_comp.setChecked(self._on)

class CheckBox(ToggleButtonBase, AbstractCheckBox):
    _qt_class = QCheckBox

    def _qt_click_handler(self):
        if DEBUG: print('in _qt_click_handler of: ', self._qt_comp)
        val = self._qt_comp.isChecked()
        if self.on == val:
            return
        self.modify(on=val)
        send(self, 'click')

class RadioButton(ToggleButtonBase, AbstractRadioButton):
    _qt_class = QRadioButton

    def _qt_click_handler(self):
        if DEBUG: print('in _qt_click_handler of: ', self._qt_comp)
        val = self._qt_comp.isChecked()
        if self._on == val:
            return
        if self.group is not None:
            self.group.modify(value=self.value)
        send(self, 'click')

################################################################

class TextBase(ComponentMixin, AbstractTextField):
    _connected = 0

    def _ensure_events(self):
        if self._qt_comp and not self._connected:
            events = {QEvent.KeyRelease: self._qt_key_press_handler.__func__,\
                      QEvent.FocusIn:    self._qt_got_focus_handler.__func__,\
                      QEvent.FocusOut:   self._qt_lost_focus_handler.__func__}
            self._event_filter = EventFilter(self, events)
            self._qt_comp.installEventFilter(self._event_filter)
            self._connected = 1

    def _ensure_text(self):
        if self._qt_comp:
            if DEBUG: print('in _ensure_text of: ', self._qt_comp)
            self._qt_comp.setText(self._get_qt_text())

    def _ensure_editable(self):
        if DEBUG: print('in _ensure_editable of: ', self._qt_comp)
        if self._qt_comp:
            self._qt_comp.setReadOnly(not self._editable)

    def _backend_text(self):
        if self._qt_comp:
            try:
                return str(self._qt_comp.text())
            except AttributeError:
                return str(self._qt_comp.toPlainText())

    def _get_qt_text(self):
        return QString(str(self._text))

    def _qt_key_press_handler(self, event):
        if DEBUG: print('in _qt_key_press_handler of: ', self._qt_comp)
        self._text = self._backend_text()
        #self.modify(text=self._backend_text())
        if int(event.key()) == 0x1004: #Qt Return Key Code
            send(self, 'enterkey')
        return 1

    def _qt_lost_focus_handler(self, event):
        if DEBUG: print('in _qt_lost_focus_handler of: ', self._qt_comp)
        return 1
        #   send(self, 'lostfocus')

    def _qt_got_focus_handler(self, event):
        if DEBUG: print('in _qt_got_focus_handler of: ', self._qt_comp)
        return 1
        #   send(self, 'gotfocus')

    def _qt_calc_start_end(self, text, mtxt, pos):
        start, idx = 0, -1
        for n in range(text.count(mtxt)):
            idx = text.find(mtxt, idx+1)
            if idx == pos or idx == pos - len(mtxt):
                start = idx
                break
        end = start + len(mtxt)
        if DEBUG: print('returning => start: %s | end: %s' %(start,end))
        return start,  end

class TextField(TextBase):
    _qt_class = QLineEdit

    def _ensure_selection(self):
        if self._qt_comp:
            if DEBUG: print('in _ensure_selection of: ', self._qt_comp)
            start, end = self._selection
            self._qt_comp.setSelection(start, end-start)
            self._qt_comp.setCursorPosition(end)

    def _backend_selection(self):
        if self._qt_comp:
            if DEBUG: print('in _backend_selection of: ', self._qt_comp)
            pos = self._qt_comp.cursorPosition()
            if self._qt_comp.hasSelectedText():
                text = self._backend_text()
                mtxt = str(self._qt_comp.markedText())
                return self._qt_calc_start_end(text,mtxt,pos)
            else:
                return pos, pos

class TextArea(TextBase):
    _qt_class = QTextEdit

    def _ensure_selection(self):
        #QTextEdit.setSelection is yet to be implemented...
        #Hacked it so that it will work until the proper method can be used.
        if self._qt_comp:
            if DEBUG: print('in _ensure_selection of: ', self._qt_comp)
            start, end = self._selection
            cursor = self._qt_comp.textCursor()
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.KeepAnchor)
            self._qt_comp.setTextCursor(cursor)

    def _backend_selection(self):
        if self._qt_comp:
            cursor = self._qt_comp.textCursor()
            return (cursor.position(), cursor.anchor())

    def _qt_get_lines(self):
        return self._qt_comp.toPlainText()

    def _qt_translate_row_col(self, pos):
        if DEBUG: print('translating pos to row/col...')
        row, col, curr_row, tot_len = 0, 0, 0, 0
        for ln in self._qt_get_lines():
            if pos <= len(str(ln)) + tot_len:
                row = curr_row
                col = pos - tot_len
                if DEBUG: print('returning => row: %s| col: %s' %(row,col))
                return row, col
            else:
                curr_row += 1
                tot_len += len(str(ln))
        if DEBUG: print('returning => row: %s| col: %s' %(row,col))
        return row, col

    def _qt_translate_position(self, row, col):
        if DEBUG: print('translating row/col to pos...')
        lines = self._qt_get_lines()
        pos = 0
        for n in range(len(lines)):
            if row != n:
                pos += len(lines[n])
            else:
                pos += col
                break
        if DEBUG: print('returning pos => ', pos)
        return pos

################################################################

class Frame(ComponentMixin, AbstractFrame):
    _qt_class = QFrame
    _qt_style = QFrame.Plain

################################################################

class QWindow(QWidget): pass #Alias for clarity

class Window(ComponentMixin, AbstractWindow):
    _qt_class = QWindow
    _qt_style = None #Check on this...
    _qt_frame = None
    _layout = None
    _connected = 0
    _destroying_self = 0

    def _ensure_title(self):
        if self._qt_comp:
            if DEBUG: print('in _ensure_title of: ', self._qt_comp)
            self._qt_comp.setWindowTitle(self._get_qt_title())

    def _ensure_events(self):
        if DEBUG: print('in _ensure_events of: ', self._qt_comp)
        if self._qt_comp and not self._connected:
            events = {QEvent.Resize: self._qt_resize_handler.__func__,\
                      QEvent.Move:   self._qt_move_handler.__func__,\
                      QEvent.Close:  self._qt_close_handler.__func__}
            self._event_filter = EventFilter(self, events)
            self._qt_comp.installEventFilter(self._event_filter)
            self._connected = 1

    def _ensure_destroyed(self):
        if self._qt_comp and not self._destroying_self:
            if DEBUG: print('in qt _ensure_destroyed: ', self._qt_comp)
            self._connected = 0
            self._qt_comp.destroy()
            self._qt_comp = None

    def _get_qt_title(self):
        return self._title

    def _get_panel(self):
        return self._qt_frame

    def _qt_resize_handler(self, event):
        if DEBUG: print('in _qt_resize_handler of: ', self._qt_comp)
        w = self._qt_comp.width()
        h = self._qt_comp.height()
        dw = w - self._width
        dh = h - self._height
        #self.modify(width=w, height=h)
        self._width = w
        self._height = h
        self.resized(dw, dh)
        for item in self._contents:
            item._ensure_geometry()
        return 1

    def _qt_move_handler(self, event):
        if DEBUG: print('in _qt_move_handler of: ', self._qt_comp)
        nx = self._qt_comp.x()
        ny = self._qt_comp.y()
        dx = nx - self._x
        dy = ny - self._y
        self._x = nx
        self._y = ny
        #self.modify(x=nx, y=ny)
        #self.moved(dx, dy)
        return 1

    def _qt_close_handler(self, event):
        if DEBUG: print('in _qt_close_handler of: ', self._qt_comp)
        # What follows is a dirty hack, but PyQt will seg-fault the
        # interpreter if a call onto QWidget.destroy() is made after
        # the Widget has been closed. It is also necessary to inform
        # the front-end of self being closed.
        self._destroying_self = 1
        self.destroy()
        self._destroying_self = 0
        self._connected = 0
        self._comp = None
        return 0

################################################################

class Application(AbstractApplication, QApplication):
    _created = False

    def __init__(self, *argv):
        AbstractApplication.__init__(self)
        if Application._created:
            return
        Application._created = True
        if not argv:
            argv = list(argv)
            QApplication.__init__(self,argv)
        else:
            QApplication.__init__(*(self,)+argv)
        self.connect(qApp, SIGNAL('lastWindowClosed()'), qApp, SLOT('quit()'))

    def _mainloop(self):
        qApp.exec_()

################################################################
