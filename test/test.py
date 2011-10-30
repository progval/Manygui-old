#!/usr/bin/env python3
from glob import glob
import sys, os

if hasattr(sys, 'registry'):
    # Jython:
    sys.registry.setProperty('MANYGUI_WISHLIST', _backends, 'dummy')
else:
    # CPython:
    os.environ['MANYGUI_WISHLIST'] = 'dummy'

import manygui
from manygui.Utils import log

assert manygui.backend() == 'dummy'

try:
    skip_tests = os.environ['ANYGUI_SKIP'].split()
except:
    skip_tests = []
skip_tests.sort()
if skip_tests:
    log('skipping %d tests:'%len(skip_tests),)
    for test in skip_tests:
        log(test,)
    print()

run_tests = [test for test in glob('test_*.py') if test not in skip_tests]
run_tests.sort()
log('running %d tests:'%len(run_tests),)
for test in run_tests:
    log(test,)
print()

for filename in run_tests:
    log("Running", filename)
    exec(compile(open(filename).read(), filename, 'exec'), {})
