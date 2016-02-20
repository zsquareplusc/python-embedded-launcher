==========================
 python-embedded-launcher
==========================

The launcher is a small C program that loads the Python DLL and calls
``Py_Main`` with itself as parameter, loading a zipped Python application
appended to the exe.


Scenarios
=========

Distribute an application
    Bundle Python with an application so that users can use it without having
    to install Python.

Common python-minimal package
    Multiple tools can use a common copy of Python. e.g. with a package manager
    Python can be provided as one package and separate application packages
    can use that python to run.
    => The launcher has the path to the Python installation configurable.