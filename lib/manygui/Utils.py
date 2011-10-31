'Manygui utilities.'

import sys

# To be phased out with the place() method
def flatten(seq):
    '''Flatten a sequence. If seq is not a sequence, return [seq].
    If seq is empty, return [].'''
    try:
        if len(seq) > 0:
            seq[0]
    except:
        return [seq]
    result = []
    for item in seq:
        result += flatten(item)
    return result


class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

class Options(Bunch):
    def __init__(self, **kwargs):
        """
        Options is a very simple class. It is simply used to store a bunch of
        named values; basically a dictionary with a different syntax. (For
        more information about the bunch class, see
        http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52308.)

        You can set the attributes of an Options object and then supply it as
        an optional first parameter to the constructors of widgets:

        .. code-block:: python

              opt = Options()
              opt.width = 100
              opt.height = 50
              opt.x = 10
              btn = Button(opt, y=10)
              lbl = Label(opt, y=70)

        Here btn and lbl will have the same width, height, and x attributes,
        but differing y attributes.

        You can also set the attributes of an Options object through its
        constructur, just like with components:

        .. code-block:: python

              opt = Options(width=100, height=50, x=10)

        Options objects can also be used when supplying arguments to the add
        method of Frame:

        .. code-block:: python

              # Assuming a Placer LayoutManager:
              opt = Options(left=10, right=10, hstretch=1)
              win.add(lbl, opt, top=10)
              win.add(btn, opt, top=(lbl,10))
        """
        Bunch.__init__(self, **kwargs)

import sys
class Log:

    def __init__(self,fileobj=None):
        if fileobj is None:
            fileobj = sys.stderr
        self._f = fileobj

    def log(self,*items):
        for i in items:
            self._f.write(str(i))
            self._f.write(' ')
        self._f.write('\n')

    def setLogFile(self,fileobj):
        if type(fileobj) == type(""):
            self._f = open(fileobj,"w")
        else:
            self._f = fileobj

_logger = Log()

def log(*items):
  _logger.log(*items)

def setLogFile(fileobj):
    _logger.setLogFile(fileobj)
    
_jython = sys.platform[:4] == 'java'

if _jython:
    import java
    generic_hash = java.lang.System.identityHashCode
    del java
else:
    generic_hash = id
    
class IdentityStack:
        def __init__(self):
            self._stk = []

        def pop(self):
            self._stk.pop()

        if _jython:
            def append(self,obj):
                self._stk.append(obj)
            def __contains__(self,obj):
                for cand in self._stk:
                    if cand is obj: return 1
                return 0
        else:
            def append(self,obj):
                self._stk.append(id(obj))
            def __contains__(self,obj):
                return id(obj) in self._stk
