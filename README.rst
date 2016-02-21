==========================
 python-embedded-launcher
==========================

For Windows only.

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
    can use that Python to run.
    => The launcher has the path to the Python installation configurable.


Build
=====
Requirements
------------
mingw(-64) GCC compiler, e.g. http://tdm-gcc.tdragon.net/ has one.

for Python 2.7
--------------
In the ``python27`` directory:

- run ``create_python_minimal.py`` to create a python27-minimal distribution
- run ``compile.bat`` to create ``launcher27.exe`` the ``ziptool.py`` will
  be used to append ``bootstrap27.py`` (zipped) to the exe.


Ideas
=====
The launcher should be customizable. To not require an external file or a
compiler, use Windows resource in the exe. There are resource editor tools
that can be used to change these.

