**************************
Models, Views, Controllers
**************************

The Manygui MVC mechanism (based on the refresh method and the Assignee
protocol) is described in the API Reference below. Here is a short
overview on how to use it.

A model is an object that can be modified, and that can notify other
objects, called views, when it has been modified. A controller is an
object that can modify the model, in particular as a direct response
to a user action (such as clicking the mouse or typing some text). In
Manygui, Components double as both views (showing a model's state to
the user) and controllers (letting the user modify the model). Even
though Manygui supports using models this way, you can also create
complete application without using them.

Models are in general instances of some subclass of the Model class,
although they don't have to be; see the API Reference below for a
description of how they work. (The Model class is currently internal
to the Manygui package, but it can be found int he manygui.Models
module.) The Models that are included in Manygui are::

      BooleanModel     -- represents a Boolean value
      ListModel        -- behaves like a list
      NumberModel      -- represents a numerical value
      TextModel        -- acts like a mutable string

These all have a value attribute which may be used to change their
internal value. They also support other operations, such as indexing
and slicing etc. for ListModel. These are very easy to use: Just
assign them to an attribute of a Component:

.. code-block:: python

      # You'll learn about CheckBoxes in a minute
      cbx = CheckBox(text='Simple model test')
      state = BooleanModel(value=1)
      cbx.on = state

Now, if you change state (e.g. with the statement state.value=0) this
will automatically be reflected in the CheckBox (which will be acting
like a view). If the user clicks the CheckBox, the model will be
changed.

To keep a view up-to-date manually you can call its refresh method.
This can be useful if you use a simple (non-Model) mutable value such
as a list in an attribute:

.. code-block:: python

      btn = Button()
      rect = [0, 0, 10, 10]
      btn.geometry = rect
      rect[3] = 20
      btn.refresh()

After modifying rect, the button will not have changed, since it can't
detect the change by itself. (That's only possible when you use a real
model.) Therefore, you call btn.refresh to tell it to update itself.

If you assign a value to an attribute, the refresh method will be
called automatically, so another way of doing the same thing is:

.. code-block:: python

      btn = Button()
      rect = [0, 0, 10, 10]
      btn.geometry = rect
      rect[3] = 20
      btn.geometry = rect

.. warning::

        Because of the controller behaviour of Components, if the
        Button is resized, rect will be modified. If you don't want this
        behaviour, use a tuple instead of a list, since tuples can't be
        modified.

If you want another object to monitor a model, you can simply use the
link method, since all models generate an event (of the type default)
when they are modified.

Example:

.. code-block:: python

      from manygui import *
      >>> mdl = BooleanModel()
      >>> mdl.value = 1
      >>> def model_changed(**kw):
      >>>     print 'The model has changed!'

      >>> link(mdl, model_changed)
      >>> mdl.value = 0
      The model has changed
      >>> mdl.value = 0
      The model has changed

Note the last two lines: We haven't really changed the model, but the
event handler is called nonetheless. If you want to know whether the
model really changed, you must retain a copy of its state, and compare
the new value.

