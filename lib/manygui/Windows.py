from manygui import application
from manygui.Frames import AbstractFrame
from manygui.Exceptions import UnimplementedMethod
from manygui import Defaults
#import inspect

class AbstractWindow(AbstractFrame, Defaults.Window):

    def __init__(self, *args, **kw):
        """
        A window, plain and simple. Window is a type of Frame, so you can add
        components to it and set its layout property etc. To make your window
        appear, you must remember to add it to your Application, just like you
        add other components to Frames and Windows:

        .. code-block:: python

              win = Window()
              app = Application()
              app.add(win)
              app.run()

        Windows have a title attribute which may be used by the operating
        system or window manager to identify the window to the user in various
        ways.
        """
        AbstractFrame.__init__(self, *args, **kw)

        # Window staggering code:
        # FIXME: Should be offset from current top window, if any
        self._x = Defaults.Window._x
        self._y = Defaults.Window._y
        Defaults.shift_window()
        
        #application()._add_window(self) # Now done explicitly

        """
        Commented out, because it was deemed too magical and unportable.
        Left for its entertainment value ;)
        
        # If we are inside a function call, set up a CreationSentinel
        # in surrounding local scope -- otherwise, just call
        # ensure_created:                               (mlh20011110)
        stack = inspect.stack()
        if len(stack) > 2: # Is this check correct?
            scope = stack[1][0].f_locals
            name = 0
            while scope.has_key(`name`): name += 1
            scope[`name`] = self.CreationSentinel(self)
        else:
            pass
        del stack
        """
        
    def destroy(self):
        self._ensure_destroyed()
        try:
            application().remove(self)
        except ValueError:
            # Already removed
            pass

    def _set_title(self, text):
        if self._title != text:
            self._title = text
            # self._ensure_title()

    def _get_title(self):
        return self._title

    def _ensure_title(self):
        raise UnimplementedMethod(self, "_ensure_title")
