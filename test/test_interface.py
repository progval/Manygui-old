# TODO: Use unittest
from manygui.Utils import log

import manygui

backends = []

log("Checking backend __all__ attributes:")

for b in manygui._backends:
    try:
        mod = manygui._dotted_import('manygui.backends.%sgui' % b)
        backends.append((mod, b))
    except:
        log("[%sgui ignored]" % b)

for mod, name in backends:
    assert mod.__all__ == manygui.__all__, ('%sgui should export the same API as manygui' % name)
    log("%sgui OK" % name)
