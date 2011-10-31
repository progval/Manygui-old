from manygui.GenericButtons import AbstractGenericButton
from manygui import Defaults

class AbstractButton(AbstractGenericButton, Defaults.Button):
    def __init__(self, *args, **kwargs):
        """
        A component which, when pressed, generate a 'click' event, as well as
        a 'default' event. Thus, in the following example, both handler1 and
        handler2 will be called when the button is pressed:

        .. code-block:: python

              btn = Button()
              def handler1(**kw): print 'Handler 1'
              def handler2(**kw): print 'Handler 2'
              link(btn, 'click', handler1)
              link(btn, handler2)
              class Toto:
                  pass
        """
        AbstractGenericButton.__init__(self, *args, **kwargs)
