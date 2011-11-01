*********************************
Base classes and common behaviour
*********************************

All components are subclasses of corresponding abstract components
which implement behaviour common to all the backends. So, for
instance, Button subclasses AbstractButton. These abstract components,
again, subclass AbstractComponent, which implements behaviour common
to all components.

Perhaps the most important behaviour is attribute handling (inherited
from the Attrib mixin), which means that setting a components
attributes may trigger some internal method calls. For instance,

.. code-block:: python

      win.size = 300, 200

will automatically resize the component win.

Attributes common to all components
===================================

      x         -- x-coordinate of upper left corner
      y         -- y-coordinate of upper left corner
      position  -- equivalent to (x, y)
      width     -- component width
      height    -- component height
      size      -- equivalent to (width, height)
      geometry  -- equivalent to (x, y, width, height)
      visible   -- whether the component is visible
      enabled   -- whether the component is enabled
      text      -- text associated with the component

These can all be set as keyword arguments to the component
constructors. Also, Options objects (with similar constructors) can be
used as positional arguments in the constructor, with all the
Options's attributes being set in the component as well.

Common to Application, Window, and Frame is the contents attribute, as
well as the add and remove methods. These will be described with the
individual classes below.

All Attrib subclasses (including components, Application, and
RadioGroup) share the following methods:

set(*args, **kwds)
------------------

Used to set attributes. Works like the Attrib constructor, setting
attributes, and optionally using Options objects.

modify(*args, **kwds)
---------------------

Works like the set method, except that the attributes are modified in
place. That means the following (for an attribute named foo): (1) If
there exists an internal method (implemented in Manygui) for modifying
the attribute inplace (called _modify_foo), use that; otherwise (2)
try to use slice assignment to change the value (will work for lists
and ListModels etc.); if that doesn't work, (3) assign to the value's
value attribute (used to modify Models. If neither of these approaches
work, simply rebind the attribute (equivalent to using the set
method).

As with set and ordinary attribute assignment, the refresh method will
automatically be called when you use modify.

refresh()
---------

When an attribute of a Component (or Application, RadioGroup, or an
instance of another Attrib subclass) is assigned a value, the
Component is automatically updated to reflect its new state. For
instance, if you have a Labellbl, assigning a value to lbl.geometry
would immediately change the Label's geometry, and assigning to
lbl.text would change its text.

This is good enough for most cases, but sometimes an attribute can
contain a mutable value, such as a list, and changing that will not
update the Component. For instance, if you use a list to hold the
items of a ListBox, you could end up in the following situation:

.. code-block:: python

        lbx = ListBox()
        lbx.items = 'first second third'.split()
        # More code...
        lbx.items.append('fourth')

After performing this code, nothing will have happened to the ListBox,
because it has no way of knowing that the list has changed. To fix
that, you can simply call its refresh method:

.. code-block:: python

        lbx.refresh()

This method checks whether any attributes have changed, and make sure
that the Component us up to date.

Updating Automatically
======================

Updating Components explicitly can be useful, but sometimes you would
want it to be done for you, automatically, each time you modify an
object that is referred to by a Component attribute. This can be taken
care of by link and send. If your object uses send every time it's
modified, and you link the object to your Component's refresh method,
things will happen by themselves:

.. code-block:: python

      class TriggerList:
          def __init__(self):
              self.list = []
          def append(self, obj):
              self.list.append(obj)
              send(self)
          def __getitem__(self, i):
              return self.list[i]

      lbx = ListBox()
      lbx.items = TriggerList()
      link(lbx.items, lbx.refresh)

Now, if we call lbx.items.append('fourth'), lbx.refresh will
automatically be called. To make your life easier, Manygui already
contains some classes that send signals whend they are modified; these
classes are called Models.

Model and Assignee
==================

The Manygui models (BooleanModel, ListModel, TextModel, and
NumberModel) are objects that call send (with the 'default' event)
when they are modified.

An Assignee (part of the Manygui Model-View-Controller mechanism) is an
object that supports the methods assigned and removed. These are
automatically called (if present) when the object is assigned to one
of the attributes of an Attrib object (such as a Component). Models
use this behaviour to automatically call link and unlink, so when the
Model is modified, the refresh method of the Attrib object is called
automatically.

All models have a value attribute, which contains a "simple" version
of its state (such as a number for NumberModel, a list for ListModel,
etc.) Assigning to this attribute is a simple way of modifying the
model in place.
