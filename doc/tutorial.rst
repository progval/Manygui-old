********************
The Manygui tutorial
********************

Introduction
============

The Python standard library currently does not contain any
platform-independent GUI packages. It is the goal of the Manygui
project to change this situation. There are many such packages
available, but none has been defined as standard, so when writing GUI
programs for Python, you cannot assume that your user has the right
package installed.

The problem is that declaring a GUI package as standard would be quite
controversial. There are some packages that are quite commonly
available, such as Tkinter; but it would not be practical to require
all installations to include it, nor would it be desirable to require
all Python GUI programs to use it, since there are many programmers
who prefer other packages.

Manygui tries to solve this problem in a manner similar to the standard
anydbm package. There is no need to choose one package at the expense
of all others. Instead, Manygui gives generic access to several popular
packages through a simple API, which makes it possible to write GUI
applications that work with all these packages. Thus, one gets a
platform-independent GUI module which is written entirely in Python.

To get the latest Manygui distribution, or to get in touch with the
developers, please visit the `Manygui repository`_

.. _Manygui repository: https://github.com/ProgVal/Manygui

Design Goals
------------

#. Manygui should be an easy to use GUI package which may be used to
   create simple graphical programs, or which may serve as the basis for
   more complex application frameworks.

#. Manygui should be a pure Python package which serves as a front-end
   for as many as possible of the GUI packages available for Python, in a
   transparent manner.

#. Manygui should include functionality needed to perform most GUI
   tasks, but should remain as simple and basic as possible.

Warning
-------

The Manygui API is currently very much in flux as the Manygui team keeps
experimenting with it. Because of that, incompatibilities may occur
between releases. The current release (0.1.1) should be regarded as a
prototype.

Tutorial
--------

There is also a short tutorial available, which is included in the
installation (doc/quick_start.rst) and is available from the `website`_.

.. _website: https://github.com/ProgVal/Manygui

Installation
============

The Manygui package comes in the form of a gzip compressed tar archive.
To install it you will first have to uncompress the archive. On
Windows this can be done with WinZip. in Mac OS, you can use StuffIt
Expander. In Unix, first move to a directory where you'd like to put
Manygui, and then do something like the following::

      foo:~/python$ tar xzvf manygui-0.1.1.tar.gz

If your version of tar doesn't support the z switch, you can do
something like this::

      foo:~/python$ zcat manygui-0.1.1.tar.gz | tar xvf

Another possibility is::

      foo:~/python$ gunzip manygui-0.1.1.tar.gz
      foo:~/python$ tar -xvf manygui-0.1.1.tar

No matter which version you choose, you should end up with a directory
named manygui-0.1.1.

Running setup.py
----------------

The simple way of installing Manygui is to use the installation script
that's included in the distribution. This requires Distutils
(http://www.python.org/sigs/distutils-sig), which is included in
Python distributions from version 2.0. To install the Manygui package
in the default location, simply run the setup script with the install
command::

      foo:~$ python setup.py install

This will install Manygui in your standard Python directory structure.
If you don't have access to this directory (e.g. because Python was
installed by a sysadmin, and you don't have root access) you can
install it somewhere else with the --prefix option::

      foo:~$ python setup.py install --prefix=${HOME}/python

Doing it Manually
-----------------

Since Manygui consists of only Python code, nothing needs to be
compiled. And the only thing needed to install Python code is to
ensure that the packages and modules are found by your Python
interpreter. This is as simple as including the lib directory of the
Manygui distribution in your PYTHONPATH environment variable. In bash
(http://www.gnu.org/manual/bash/), you could do something like this::

      foo:~$ export PYTHONPATH=$PYTHONPATH:/path/to/manygui/lib

To make this permanent, you should put it in your .bash_profile file,
or something equivalent. If you don't want to mess around with this,
and already have a standard directory where you place your Python
modules, you can simply copy (or move) the manygui package (found in
manygui-0.1.1/lib) there, or possibly place a symlink in that directory
to the manygui package.

Making Sure You Have a Usable GUI Package
-----------------------------------------

Once you have Manygui installed, you'll want to make sure you have a
usable GUI package. This is easy to check: Simply start an interactive
Python interpreter and try to execute the following:

.. code-block:: pycon

      >>> from manygui import *
      >>> backend()

The backend function will return the name of the backend in use. If it
is neither 'curses' nor 'text' you should be all set for making GUI
programs with Manygui. (The 'curses' and 'text' backends use plain text
to emulate graphical interfaces on platforms that don't have them.)
Manygui currently supports the following packages::

      PyQt       (qtgui)     http://www.thekompany.com/projects/pykde
      PythonWin  (mswgui)    http://starship.python.net/crew/mhammond/win32
      Tkinter    (tkgui)     http://www.python.org/topics/tkinter
      wxPython   (wxgui)     http://www.wxpython.org
      Java Swing (javagui)   http://www.jython.org
      PyGTK      (gtkgui)    http://www.daa.com.au/~james/pygtk
      Bethon     (beosgui)   http://www.bebits.com/app/1564
      Curses     (cursesgui) -- used when no GUI package is available
      Plain text (textgui)   -- used if curses is not available

Add gui to name returned by the backend function to get the full name
of the backend module (in the manygui.backends package). For instance,
the msw backend is found in manygui.backends.mswgui module.

In general, if you end up with a text-based solution, cursesgui will
be preferred over textguiif your Python-installation has a wrorking
curses module. The exception is if you are using Manygui in the
interactive interpreter, in which textgui will be preferred, to avoid
interfering with the terminal and locking up the interpreter prompt.
(If you'd like to, for some reason, you can override this behaviour
with the environment variable MANYGUI_FORCE_CURSES; see the API
Reference below.)

BeOS Note: The BeOS backend (beosgui) is currently not fully
functional, but is included nonetheless.

Of these, Tkinter is compiled in by default in the MS Windows
distribution of Python (available from http://www.python.org),
PythonWin (as well as Tkinter) is included in the ActiveState
distribution, ActivePython (available from
http://www.activestate.com), and Java Swing is automatically available
in Jython, the Java implementation of Python.

.. note::

        In Mac OS 9, Manygui (using Tkinter) works with with Python
        Classic and recent versions of Python Carbon, but older versions have
        problems with Tkinter.

Using Manygui
=============

.. note::

        For some examples of working Manygui code, see the test and demo
        directories of the distribution. Remember that the test scripts are
        written to test certain features of Manygui, not to represent
        recommended coding practices.

Using Manygui is simple; it's simply a matter of importing the classes
and functions you need from the manygui module, e.g.:

.. code-block:: python

      from manygui import *

After doing this you must create an Application object, at least one
Window, and probably a few components such as Buttons and TextFields.
The Windows are added to the Application (through its add method), and
the various components are added to the Window. When you have done
this, you call the run method of your Application instance.

.. code-block:: python

      # Make components here
      win = Window()
      # Add components to the Window
      app = Application()
      app.add(win)
      app.run()

Avoiding Namespace Pollution
----------------------------

Importing everything from Manygui (as in from manygui import \*) is fine
for small programs, where you're certain that there will be no name
clashes. You may also simply import the names you need:

.. code-block:: python

      from manygui import Application, Window

The preferred way to use modules like this is usually to avoid
cluttering your namespace, by using simply import manygui. However, if
you are going to create a lot of widgets, the manygui prefix may be
cumbersome. Therefore, I suggest renaming it to gui, either with a
simple assignment...

.. code-block:: python

      import manygui; gui = manygui

... or, in recent versions of Python:

.. code-block:: python

      import manygui as gui

Then you can instantiate widgets like this:

.. code-block:: python

      win = gui.Window()

The examples in this documentation use the starred import, for
simplicity.

Importing the Backends Directly
-------------------------------

If you wish to import a backend directly (and "hardwire it" into your
program), you may do so. For instance, if you wanted to use the
wxPython backend, wxgui, you'd replace

.. code-block:: python

      from manygui import *

with

.. code-block:: python

      from manygui.backends.wxgui import *

This way you may use Manygui in standalone executables built with tools
like py2exe (http://starship.python.net/crew/theller/py2exe/) or the
McMillan installer (http://www.mcmillan-inc.com/install1.html), or
with jythonc with the --deep option or equivalent.

.. note::

        Compiling jar files of Manygui programs with Jython may not work
        in the current version.

Note that the namespace handling still works just fine:

.. code-block:: python

      import manygui.backends.tkgui as gui

Adding a Label
--------------

Simple labels are created with the Label class:

.. code-block:: python

      lab = Label(text='Hello, again!', position=(10,10))

Here we have specified a position just for fun; we don't really have
to. If we add the label to our window, we'll see that it's placed with
its left topmost corner at the point (10,10):

.. code-block:: python

      w.add(lab)

Layout: Placing Widgets in a Frame
----------------------------------

This section goves a simple example of positioning Components; for
more information about the Manygui layout mechanism, please refer to
the API Reference (below).

.. code-block:: python

      win.add(lab, position=(10,10))
      win.add(lab, left=10, top=10)
      win.add(lab, top=10, right=10)
      win.add(lab, position=(10,10), right=10, hstretch=1)

In the last example hstretch is a Boolean value indicating whether the
widget should be stretched horizontally (to maintain the other
specifications) when the containing Frame is resized. (The vertical
version is vstretch.)

Just like in component constructors, you can use Options objects in
the add method, after the component to be added:

.. code-block:: python

      win.add(lab, opt, left=10)

Placing More Than One Widget

The add method can also position a sequence of widgets. The first
widget will be placed as before, while the subsequent ones will be
placed either to the right, to the left, above (up), or below (down),
according to the direction argument, at a given distance (space):

.. code-block:: python

      win.add((lab1, lab2), position=(10,10),
              direction='right', space=10)

.. note::

        Remember to enclose your components in a sequence (such as a
        tuple or a list), since add allows you to use more positional
        arguments, but will treat them differently. If you want to use Options
        objects, place them outside (after) the sequence. For more information
        see the section about the Frame class in the API Reference below.

Buttons and Event Handling
--------------------------

Buttons (as most components) work more or less the same way as Labels.
You can set their size, their position, their text, etc. and then add
them to a Frame (such as a Window). The thing that makes them
interesting is that they emit events. Each time the user clicks a
button, it sends out a click event. You can catch these events by
linking your button to one or more event handlers. It's really simple:

.. code-block:: python

      btn = Button(text='Greet Environment')
      def greeting(**args):
          print 'Hello, World!'
      link(btn, greeting)

The event handling is taken care of by the call to link. An event
handler may receive several keyword arguments, and if you're not
particularly interested in any of them, simply use something like
**args above. (For more information about this, see the section about
global functions in the API Reference below.)

About Models, Views, and Controllers
------------------------------------


Using CheckBoxes
----------------

A CheckBox is a toggle button, a button which can be in one of two
states, "on" or "off". Except for that, it works more or less like any
other button in that you can place it, set its text, and link an event
handler to it.

Whether a CheckBox is currently on or off is indicated by its on
attribute.

RadioButtons and RadioGroups
----------------------------

RadioButtons are toggle buttons, just like CheckBoxes. The main
differences are that they look slightly different, and that they
should belong to a RadioGroup.

A RadioGroup is a set of RadioButtons where only oneRadioButton is
permitted to be "on" at one time. Thus, when one of the buttons in the
group is turned on, the others are automatically turned off. This can
be useful for selecting among different alternatives.

RadioButtons are added to a RadioGroup by setting their group
property:

.. code-block:: python

      radiobutton.group = radiogroup

This may also be done when constructing the button:

.. code-block:: python

      grp = RadioGroup()
      rbn = RadioButton(group=grp)

.. note::

        The behaviour of a RadioButton when it does not belong to a
        RadioGroup is not defined by the Manygui API, and may vary across
        backend. Basically, a RadioButton without a RadioGroup is meaningless;
        use a CheckBox instead.

RadioGroups also support an add method, as all other Manygui
container-like objects:

.. code-block:: python

   add(button)

Adds the button to the group, including setting button.group to the
group. As with the other add methods, the argument may be either a
single object, or a sequence of objects.

ListBox
-------

A ListBox is a vertical list of items that can be selected, either by
clicking on them, or by moving the selection up and down with the
arrow keys. (For the arrow keys to work, you must make sure that the
ListBox has keyboard focus. In some backends this requires using the
tab key.)

.. note::

        When using Manygui with Tkinter, using the arrow keys won't
        change the selection, only which item is underlined. You'll have to
        use the arrow keys until the item you want to select is underlined;
        then select it by pressing the space bar.

A ListBox's items are stored in its attribute items, a sequence of
arbitrary objects. The text displayed in the widget will be the result
of applying the built-in Python function str to each object.

.. code-block:: python

      lbx = ListBox()
      lbx.items = 'This is a test'.split()

The currently selected item can be queried or set through the
selection property (an integer index, counting from zero). Also, when
an item is selected, a select event is generated, which is the default
event type for a ListBox. This means that you can either do

.. code-block:: python

      link(lbx, 'select', handler)

or

.. code-block:: python

      link(lbx, handler)

with the same result. (This is similar to the click event, which is
default for Buttons; for more information, see the API Reference
below.)

TextField and TextArea
----------------------

Manygui's two text widgets, TextField and TextArea are quite similar.
The difference between them is that TextField permits neither newlines
or tab characters to be typed, while TextArea does. Typing a tab in a
TextField will simply move the focus to another widget, while pressing
the enter key will send an enterkey event (which is the TextField's
default event type).

The text in a text component is stored in its text property (a string
or equivalent), and the current selection is stored in its selection
property (a tuple of two integer indices).
