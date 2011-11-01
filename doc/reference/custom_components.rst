*********************************************
Making your own Components and LayoutManagers
*********************************************

Currently, you can create your own components by combining others in
Frames, and wrapping the whole thing up as a class. One of the main
reasons for doing this would be to emulate a feature (such as a tabbed
pane) available in some backends, but not in others. One could then
actually use the native version in the backends where it is available
(such as wx, in this case), and use the "emulation" in the others.
There is some limited support for this in the backend function (which
will allow you to check whether you are currently using the correct
backend), but in the future, a more complete API will be developed for
this, allowing you access to the coolest features of your favorite GUI
package, while staying "package independent".

You can already create your own layout managers, by properly
supporting the methods add, remove, and resized. The simplest way of
doing this is to subclass LayoutManager, which gives you the add and
remove methods for free. You can then concentrate on the method
resized which takes two positional arguments, dw, and dh (change in
width and change in height) and is responsible for changing the
geometries of all the components in the Frame the LayoutManager is
managing. (This frame is available through the private attribute
self._container.)

To get more control over things, you should probably also override the
two internal methods add_components and remove_component:

.. code-block:: python

   add_components(self, *items, **kws)

Should add all the components in items, and associate them with the
options in kws, for later resizing.

.. code-block:: python

   remove_component(self, item)

Should remove the given item.
