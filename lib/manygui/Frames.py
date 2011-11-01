from manygui.Components import AbstractComponent
from manygui.Exceptions import ArgumentError, UnimplementedMethod
from manygui.Utils import flatten
from manygui import Defaults
from manygui.LayoutManagers import Placer

class AbstractFrame(AbstractComponent, Defaults.Frame):

    def __init__(self, *args, layout=None, **kw):
        """
        Frame is a component which can contain other components. Components
        are added to the Frame with the add method.

        `layout` is the :class:`manygui.LayoutManager` instance used for placing
        components in the Frame. It defaults to :class:`manygui.Placer`.
        """
        if layout is None:
            layout = Placer()
        self._contents = []
        AbstractComponent.__init__(self, *args, **kw)
        self._layout = None
        self.layout = layout

    def ensure_created(self):
        if self._ensure_created():
            for item in self._contents:
                item.ensure_created()
                # Redundant:
                #if item.ensure_created():
                #    item._finish_creation()
            self._finish_creation()
            return 1
        return 0

    def _get_contents(self):
        return tuple(self._contents)
        
    def add(self,items,options=None,**kws):
        """
        Adds one or more components. The parameter comp may be either a single
        component, or a sequence of components. In the latter case, all the
        components will be added.

        The opts parameter containes an Options object (see below) which gives
        information about how the object should be laid out. These options can
        be overridden with keyword arguments, and all this information will be
        passed to the LayoutManager (see below) of the Frame, if any. This
        LayoutManager is stored in the layout property.

        Note that different layout managers may have different
        expectations about **kwds, and may impose restrictions on the
        contents of items
        """

        items = flatten(items)

        # Now add to self._contents.
        for component in items:
            # _set_container() adds component to self._contents.
            # layout manager may have already called it, though.
            if component not in self._contents:
                component._set_container(self)

        # Inform the layout manager, if any.
        if self._layout:
            self._layout.add(items,options,**kws)

    def remove(self, component):
        "If the given component is among the contents of this Frame, removes it."
        if component in self._contents:
            component._set_container(None)
            self.layout.remove(component)
            self.layout.resized(0,0)

    def destroy(self):
        while self._contents:
            self._contents[0].destroy()
        AbstractComponent.destroy(self)

    def resized(self, dw, dh):
        try:
            self.layout.resized(dw,dh)
            for item in self._contents:
                try:
                    item.resized(dw,dh)
                except:
                    pass
        except:
            pass

    def _add(self, comp):
        self._contents.append(comp)
        if self._is_created():
            comp.ensure_created()
            # Redundant:
            #if comp.ensure_created():
            #    comp._finish_creation()

    def _remove(self, comp):
        try:
            self._contents.remove(comp)
            comp.destroy()
        except ValueError:
            pass

    def _set_layout(self,lo):
        if self._layout:
            self._layout._container = None
            ct = self._contents
            for item in ct:
                self._remove(item)
        self._layout = lo
        lo._container = self

    def _get_layout(self):
        return self._layout
