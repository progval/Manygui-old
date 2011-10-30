from manygui.Mixins import Attrib, DefaultEventMixin
from manygui.Exceptions import UnimplementedMethod
from manygui.LayoutManagers import LayoutData


class AbstractComponent(Attrib, DefaultEventMixin):
    """AbstractComponent is an abstract base class representing a visual 
    component of the graphical user interface. A Component owns a rectangular
    region of screen space defined by its x, y, width and height properties.
    It may be contained within another Component, in which case it is clipped
    to the boundaries of its container.
    """

    # AMLAC20011212: note most _ensure_* methods are now auto-called via
    # Attrib's mechanisms (except _ensure_created and _ensure_destroyed!)
    # so the _ensure_* calls are commented out here and in fact several
    # of the getters/setters (except those for geometry, probably) can
    # also be eventually removed (and backends fixed accordingly)
    
    _inhibit_refresh = 1         # Components start out refresh-inhibited
    _container = None

    def __init__(self, *args, **kw):
        self.layout_data = LayoutData()
        DefaultEventMixin.__init__(self)
        Attrib.__init__(self, *args, **kw)

    def destroy(self):
        self._set_container(None)
        self._ensure_destroyed()

    def ensure_created(self):
        if self._ensure_created():
            self._finish_creation()

    def _finish_creation(self):
        self._ensure_events()
        self._inhibit_refresh = 0
        self.refresh()

    def _set_visible(self, value):
        """Set the visibility."""
        if value == self._visible:
            return
        self._visible = value

    def _set_enabled(self, value):
        """Enable or disable the component."""
        if value == self._enabled:
            return
        self._enabled = value

    def _get_visible(self):
        """Return whether the component is currently visible."""
        return self._visible

    def _set_x(self, x):
        """Set a new horizontal position."""
        if x == self._x:
            return
        self._x = x

    def _get_x(self):
        "Return the current horizontal position."""
        return self._x

    def _set_y(self, y):
        """Set a new vertical position."""
        if y == self._y:
            return
        self._y = y

    def _get_y(self):
        "Return the current vertical position."""
        return self._y

    def _set_width(self, w):
        """Set a new width."""
        if w == self._width:
            return
        self._width = w

    def _get_width(self):
        "Return the current width."""
        return self._width

    def _set_height(self, h):
        """Set a new height."""
        if h == self._height:
            return
        self._height = h

    def _get_height(self):
        "Return the current height."""
        return self._height

    def _set_size(self, xxx_todo_changeme):
        """Set a new size."""
        (w, h) = xxx_todo_changeme
        if (w, h) == (self._width, self._height):
            return
        self._width = w
        self._height = h

    def _get_size(self):
        """Return the current size."""
        return self._width, self._height

    def _set_position(self, xxx_todo_changeme1):
        """Set a new position."""
        (x, y) = xxx_todo_changeme1
        if (x, y) == (self._x, self._y):
            return
        self._x = x
        self._y = y

    def _get_position(self):
        """Return the current position."""
        return self._x, self._y

    def _set_geometry(self, xxx_todo_changeme2):
        """Set new position and size."""
        (x, y, w, h) = xxx_todo_changeme2
        if (x, y, w, h) == (self._x, self._y, self._width, self._height):
            return
        self._x = x
        self._y = y
        self._width = w
        self._height = h

    def _get_geometry(self):
        """Return position and size."""
        return self._x, self._y, self._width, self._height

    def _set_container(self, v):
        p = self._container
        if p != v and p:
            p._remove(self)
        self._backend_set_container(v)
        self._container = v
        if v is not None:
            v._add(self)

    def _backend_set_container(self, new):
        pass

    def _get_container(self):
        return self._container

    def container_resized(self, cdw, cdh):
        """Called whenever the component's container changes size.
        Adjusts the component's size according to its moving and
        stretching options."""
        dx = 0
        dy = 0
        dw = 0
        dh = 0
        if self._hmove:
            dx = cdw
        elif self._hstretch:
            dw = cdw
        if self._vmove:
            dy = cdh
        elif self._vstretch:
            dh = cdh
        if dx != 0 or dy != 0 or dw != 0 or dh != 0:
            self.geometry = (self._x + dx, self._y + dy,
                             self._width + dw, self._height + dh)

    # backend api

    def _is_created(self):
        raise UnimplementedMethod(self, "_is_created")

    def _ensure_created(self):
        raise UnimplementedMethod(self, "_ensure_created")

    def _ensure_geometry(self):
        raise UnimplementedMethod(self, "_ensure_geometry")

    def _ensure_visibility(self):
        raise UnimplementedMethod(self, "_ensure_visibility")

    def _ensure_enabled_state(self):
        raise UnimplementedMethod(self, "_ensure_enabled_state")

    def _ensure_destroyed(self):
        raise UnimplementedMethod(self, "_ensure_destroyed")

    def _ensure_events(self):
        raise UnimplementedMethod(self, "_ensure_events")
