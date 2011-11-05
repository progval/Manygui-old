*************************
Manygui quick start guide
*************************


Introduction
============

Manygui is a GUI package for Python that lets you write GUI programs
that will run in any Python installation, using the available
backend packages (such as Tkinter or wxPython) and resort to
text-based GUI emulation (using curses or plain standard
input/output) when no known GUI backend is available.

This tutorial will show you how to use Manygui to build a simple
application which has a single window with a text field and a
button.  Pressing the button will insert a random sentence into the
text field.

To follow this tutorial, you'll need a Python interpreter and the
latest Manygui distribution. Python can be downloaded from the
`Python website`_ and Manygui can be downloaded from the
`Manygui repository`_

.. _Python website: http://python.org
.. _Manygui repository: https://github.com/ProgVal/Manygui

Creating Random Sentences
=========================

Before we make the GUI, we'll need some functionality. Let's keep
it simple:

.. code-block:: python

        from random import choice

        nouns = ['can of spam', 'cardinal', 'machine that goes "ping"']
        adjectives = ['big', 'little', 'pink', 'tasty']
        verbs = ['ate', 'got', 'imitated']

        def sentence():
          words = ['the',
                   choice(adjectives),
                   choice(nouns),
                   choice(verbs),
                   'the',
                   choice(adjectives),
                   choice(nouns)]
          return ' '.join(words)

To customise this, simply edit the word lists to taste. With the
current setup, it works like this:

.. code-block:: pycon

        >>> sentence()
        'the big cardinal got the tasty machine that goes "ping"'

Creating a Window and Running the Application
=============================================

Now we need an application with a single window. How do we do that?
It's really intuitive:

.. code-block:: python

      from manygui import *
      
      win = Window()
      app = Application()
      app.add(win)

There; we've created a Window object, an Application object, and
added the Window to the Application (otherwise it wouldn't show up
anywhere).

This won't do anything by itself; we need to tell the Application
to start running, which will "freeze" the script and start up a
GUI:

.. code-block:: python

      app.run()
      print "We're done!"

I just added the print statement to show how this works. If you run
the script, you will see that an empty window appears, and that's
about it. But when you close that window, the Application stops
running the GUI, and the run() method will return, and finally the
program will print "We're done!"

Adding a Button and a TextField
===============================

Now that you've seen me add a Window to the Application, I'm sure
you can guess how to add a Button and a TextField to the Window,
but I'll show you anyway:

.. code-block:: python

      btn = Button()
      win.add(btn)
      
      txt = TextField()
      win.add(txt)

Nothing fancy here. However, if you actually use this code, you'll
probably notice a two things:

#. The button will simply be called "Button"

#. The positioning will be really stupid

So what do we do to change that?

Attributes
==========

The clue to customising objects in Manygui is attributes. Most
properties of any object can be modified simply by setting an
attribute; for instance, to set the text of our Button object, we
can simply do

.. code-block:: python

      btn.text = 'Click Me'

Simple, huh? Similarly, we can set the components' size and
position:

.. code-block:: python

      btn.x = 10
      btn.y = 10
      btn.width = win.width - 20

      txt.x = 10
      txt.y = btn.height + 20
      txt.width = btn.width

Similarly we could set the window size and position etc. Feel free
to experiment to make the application look more sensible.

There are a few shortcuts that makes specifying position and
geometry a bit easier:

.. code-block:: python

      btn.geometry = x, y, width, height

is equivalent to setting x, y, width, height separately; similarly
we have

.. code-block:: python

      btn.position = x, y

and

.. code-block:: python
   
      btn.size = width, height

If you don't want to set all the attributes separately, you can
also supply them as keyword arguments to the object's constructor:

.. code-block:: python

      btn = Button(text='Click Me', x=10, y=10, ...)

Advanced Layout
===============

Specifying the size and position of the components can be a bit
tedious, but it is also a technique with one serious limitation: If
you resize the window, the components' geometry won't change. To

To use a layout manager, simply assign it to a Window's layout
attribute:

.. code-block:: python

      win.layout = SomeLayoutManager()

The default layout manager is Placer, and we'll only look at that
here (which means that you can leave your Window's layout property
alone).

(Note: Layout managers can be used with any Frame, not just
Windows. Frames in general aren't discussed in this tutorial.)

To give the layout manager something to work with, simply use some
keyword arguments in the add method. You can combine this with
setting the component geometry in any way you like; the layout
manager simply updates the geometry when the surrounding Window (or
Frame) is resized.

Let's say we want the following placement:

#. The text field is placed on top, with a 10 point margin

#. The text field should be resized to fill the window
   horizontally

#. The button should have a fixed size, but be moved to keep it
   10 points from the right edge of the window

We can do that like this:

.. code-block:: python

      win.add(txt, top=10, left=10, right=10, hstretch=1)

Here we are simply telling the layout manager that the top, left,
and right margins (the distance to the surrounding window) of the
text field should be set to 10, and that the text field should be
stretched horizontally (hstretch) to keep these margins. (There is
also a vstretch argument for vertical stretching.)

The button is placed like this:

.. code-block:: python

      win.add(btn, top=(txt,10), right=10, hmove=1)

Here we say that it should be positioned with its top 10 points
below the text field by setting top to the tuple (txt,10). We also
say that it should be positioned 10 points from the right edge of
the window, and that it should be moved horizontally to keep that
distance (hmove=1).

Try it out. Change it and see what happend. Oh, yeah; there is also
a keyword argument called bottom <wink>.

(Note: TextField is meant to contain a single line of text and
therefore isn't meant to be resized vertically. If you want to
experiment with vstretch, you could use TextArea instead, which is
meant to contain arbitrary text.)

Handling Events
===============

When certain events occur, Manygui may send a signal to your program
which you can choose to react to. (We also call this "sending an
event".)

For instance, when the user clicks a button, an event of the type
:class:`manygui.events.LeftClickEvent` is sent automatically, with
the button as the source. To respond to it, you just have to write
a function (or method) containing the action to be performed
(called the "event handler") and link it to the button:

.. code-block:: python

      def handler(**kw):
          txt.text = sentence()

      link(btn, events.LeftClickEvent, handler)

Here we have explicitly said that the handler should be called when
an event of type LeftClickEvent occurs. This is the default event type of
buttons, which means that we could also have omitted it:

.. code-block:: python

      link(btn, handler)

Try it; when you click the button, the text field will be filled
with a random sentence. Click it again, and a new sentence appears.
Cool, huh?

.. note:

        Event handlers receive information about the event through
        keyword arguments, such as event type, the time when the event
        occurred etc. We simply ignore all that here, using the **kw syntax
        to allow any keywords.)

Further Exploration
===================

After this short tutorial you should be able to write quite complex
Manygui programs. To aid you in your exploration here is some more
information:

Common attributes::

        x
                x-coordinate of upper left corner
        y
                y-coordinate of upper left corner
        position
                equivalent to (x, y)
        width
                component width
        height
                component height
        size
                equivalent to (width, height)
        geometry
                equivalent to (x, y, width, height)
        visible
                whether the component is visible
        enabled
                whether the component is enabled
        text
                text associated with the component


Some component types
--------------------

Button
^^^^^^

clickable button

CheckBox
^^^^^^^^

toggle button

cbx.on
        the state of the CheckBox

Frame
^^^^^

"container" for other components

frm.add()
        similar to win.add()

Label
^^^^^

a simple one-line text label

ListBox
^^^^^^^

selectable list of strings

lbx.items
        the items in the ListBox
lbx.selection
        the currently selected item

RadioButton
^^^^^^^^^^^

a toggle button (should be in a RadioGroup)

rbn.group
        the RadioGroup of the RadioButton

RadioGroup
^^^^^^^^^^

group of RadioButtons

grp.add()
        used for adding RadioButtons

TextArea
^^^^^^^^

multiline text component

txt.selection
        tuple (start, end) containing selection

TextField
^^^^^^^^^

single-line text component

txt.selection
        tuple (start, end) containing selection

Window
^^^^^^
a top-level window

win.title
        the title of the window

For more information about these classes, and about such things as
the Manygui Model-View-Controller mechanism, please consult the
Manygui Reference Manual, available in the disribution or from the
Manygui website[2].

The Program
===========

.. code-block:: python

   from random import choice
   from manygui import *

   nouns = ['can of spam', 'cardinal', 'machine that goes "ping"']
   adjectives = ['big', 'little', 'pink', 'tasty']
   verbs = ['ate', 'got', 'imitated']

   def sentence():
       words = ['the',
                choice(adjectives),
                choice(nouns),
                choice(verbs),
                'the',
                choice(adjectives),
                choice(nouns)]
       return ' '.join(words)

   win = Window()

   btn = Button(text='Click Me')
   txt = TextField()

   win.add(txt, top=10, left=10, right=10, hstretch=1)
   win.add(btn, top=(txt,10), right=10, hmove=1)

   win.height = txt.height + btn.height + 30

   def handler(**kw):
        txt.text = sentence()
   link(btn, events.LeftClickEvent, handler)

   app = Application()
   app.add(win)
   app.run()
