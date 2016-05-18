__version__ = '0.3.0'

# Nice explanation of importing problems with Python 3
# http://python-notes.curiousefficiency.org/en/latest/python_concepts/import_traps.html
# The file has been renamed to allow unit tests   
# as an interesting work around this file can be still used for unit testing but only
# with this change 'from py_linq.py_linq import Enumerable'. This is because the 
# current directory of (location run_tests.py) shadows the actual directory of __init__.py

from py_linq import Enumerable