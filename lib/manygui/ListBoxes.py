from manygui.Components import AbstractComponent
from manygui.Exceptions import UnimplementedMethod
from manygui.Models import ListModel
from collections import UserList
from manygui import Defaults

class ManyguiList(UserList):

    def __init__(self,items=[]):
        UserList.__init__(self,items)

    def _set_value(self,items):
        self.data = items

class AbstractListBox(AbstractComponent, Defaults.ListBox):

    def __init__(self, *args, **kw):
        """
        Shows a list of options, of which one may be selected. The ListBox has
        two special attributes: items, a sequence of items to display, and
        selection, the currently selected (as an index in the items sequence).

        The selection property will be automatically modified (as per the MVC
        mechanism) when the user makes a selection. This will also cause the
        ListBox to send a select and a defaultevent.
        """
        AbstractComponent.__init__(self, *args, **kw)

    def _get_items(self):
        return self._items

    def _set_items(self, items):
        self._items = items

    def _get_selection(self):
        selection = self._backend_selection()
        if selection is not None:
            self._selection = selection
        return self._selection
    
    def _set_selection(self, selection):
        self._selection = selection
        # self._ensure_selection()
        
    def _finish_creation(self): # FIXME: Hm...
        AbstractComponent._finish_creation(self)
        # self._ensure_items()
        # self._ensure_selection()

    def _ensure_items(self):
        raise UnimplementedMethod(self, '_ensure_items')

    def _ensure_selection(self):
        raise UnimplementedMethod(self, '_ensure_selection')
