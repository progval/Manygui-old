#from Mixins import Action
from .Exceptions import UnimplementedMethod
from .Mixins import Attrib
from .Utils import flatten
import manygui

class AbstractApplication(Attrib):

    _running = 0

    # Needed by Attrib:
    def refresh(self, **ignore): pass

    def __init__(self):
        """
        To instantiate Windows, you must have an Application to manage them.
        You typically instantiate an application at the beginning of your
        program:

        .. code-block:: python

              app = Application()
              # Build GUI and run application

        In some cases subclassing Application might be a useful way of
        structuring your program, but it is in no way required.
        """
        self._windows = []
        manygui._application = self

    def _get_contents(self):
        return tuple(self._windows)

    def add(self, win):
        """
        Adds a :class:`manygui.Window` to the Application, in the same way Components can be
        added to Frames (see below). A Window will not be visible until it has
        been added to the current Application object, and that Application is
        running. When constructing new Windows after Application.run has been
        called, you should ensure that you add your Window to your running
        Application after all the Components have been added to your Window;
        otherwise, you may see them appearing and moving about as Manygui takes
        care of the layout. (Before Application.run is called, this is not an
        issue, since no Windows will be appear before that time.)

        The parameter win can be either a single Window, or a sequence of
        Windows.
        """
        for w in flatten(win):
            self._windows.append(w)
        if self._running:
            win.ensure_created()


    def remove(self, win):
        """
        Removes a :class:`manygui.Window` from the application. This will make the Window
        disappear.
        """
        try:
            self._windows.remove(win)
        except: pass
    # FIXME: Temporary(?) fix to cover problem in mswgui _wndproc
        # FIXME: Destroy the window?

    #def _add_window(self, win):
    #    self._windows.append(win)

    #def _remove_window(self, win):
    #    if win in self._windows:
    #        self._windows.remove(win)

    #def windows(self):
    #    """Return a list of all the currently existing window objects."""
    #    # XXX Or should ApplicationImp also derive from Attrib,
    #    # and implement a _get_windows method?
    #    return self._windows

    def run(self):
        """
        Starts the main event loop of the graphical user interface. Usually
        called at the end of the program which set up the interface:

        .. code-block:: python

              app = Application()
              # Set up interface
              app.run()
        """
        self._running = 1
        if not self._windows:
            return
        for win in self._windows:
            win.ensure_created()
        self._mainloop()
        self._running = 0

    def _mainloop(self):
        raise UnimplementedMethod(self, "_mainloop")
