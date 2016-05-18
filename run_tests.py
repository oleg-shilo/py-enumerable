__author__ = 'Viralogic Software'

import sys
sys.path.append('./py_linq')
import unittest

testclasses = [
    'tests.Constructor',
    'tests.Functions'
]

suite = unittest.TestLoader().loadTestsFromNames(testclasses)
unittest.TextTestRunner(verbosity=2).run(suite)
