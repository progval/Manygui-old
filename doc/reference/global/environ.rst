*********************
Environment Variables
*********************

Some environment variables affect the behaviour of the Manygui package.
These must be set in the environment of the program using Manygui. They
may either be set permanently through normal operating system channels
(check your OS documentation for this), or possibly just set
temporarily when running your program. In Unix shells like bash, you
can set the variables on the command line before your comand, like
this::

      foo:~$ MANYGUI_SOMEVAR='some value' python someprogram.py

where MANYGUI_SOMEVAR is some environment variable used by Manygui.

Since Jython doesn't support OS environment variables, you'll have to
supply them with the command-line switch -D::

      foo:~$ jython -DMANYGUI_SOMEVAR='some value' someprogram.py

You can also set these environment variables in your own program, by
using code like the following before you import Manygui:

.. code-block:: python

      import os
      os.environ['MANYGUI_SOMEVAR'] = 'some value'

This will probably not work well in Jython, though.

The environment variables used by Manygui are:

MANYGUI_WISHLIST
================

A whitespace separated list of backend names in the
order you wish for Manygui to try to use them. The backends are
identified with a short prefix such as wx for wxgui, or tk for tkgui.
For a full list of available backends, see the section "Making Sure
You Have a GUI Backend" above. Only the backends in this list will be
tried; if you don't set MANYGUI_WISHLIST, then the following is the
default::

      'msw gtk java wx tk beos qt curses text'

If you insert an asterisk in the wishlist, it will be interpreted as
"the rest of the backends, in default order". So, for instance::

      MANYGUI_WISHLIST='tk wx * text curses'

is equivalent to::

      MANYGUI_WISHLIST='tk wx msq gtk java beos qt text curses'

Example::

      foo:~$ MANYGUI_WISHLIST='tk wx qt' python someprogram.py

MANYGUI_DEBUG
=============

When Manygui tries to import a backend, it hides all
exceptions, assuming they are caused by the fact that a given backend
doesn't work in your installation (because you don't have it installed
or something similar). However, at times this may not be the reason;
it may simple be that a given backend contains a bug. To track down
the bug, set the MANYGUI_WISHLIST to some true (in a Python sense)
value. (If the value supplied can be converted to an integer, it will.
Otherwise, it will be treated as a string.) This will make Manygui
print out the stack traces from each backend it tries to import.

There is one exception to this rule: If the true value supplied is the
name of one of the backends (such as tk or curses) only the traceback
caused by importing that backend will be shown. This can be useful to
make the output somewhat less verbose.

Example::

      foo:~$ MANYGUI_DEBUG=1 python someprogram.py

MANYGUI_ALTERNATE_BORDER
========================

This Boolean variable affects cursesgui,
making it use the same border-drawing characters as textgui ('+', '-',
and '|'). This may be useful if your terminal can't show the special
curses box-drawing characters properly.

MANYGUI_SCREENSIZE
==================

Affects textgui. Gives the terminal ("screen")
dimensions, in characters. This should be in the format widthxheight,
e.g. 80x24. If this environment variable is not supplied, the standard
Unix variables COLUMNS and LINES will be used. If neither is provided,
the default size 80x23 will be used.

MANYGUI_FORCE_CURSES
====================

Normally, cursesgui will not be selected if you
are in the interactive interpreter. If you want to force the normal
selection order (trying to use cursesgui before resorting to textgui)
you can set this variable to a true value. Note that this is not the
same as setting MANYGUI_WISHLIST to 'curses', since that will ignore
all other backends.

MANYGUI_CURSES_NOHELP
=====================

If you don't want the help-screen that appears
when an Manygui application is started using cursesgui (or textgui),
you can set this variable to a true value.
