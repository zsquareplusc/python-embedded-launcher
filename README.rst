==========================
 python-embedded-launcher
==========================

For Windows only.

The launcher is a small C program that loads the Python DLL and calls
``Py_Main`` with itself as parameter, loading a zipped Python application
appended to the exe.

Yes it is yet an other tool to make standalone Windows applications with Python.

See also py2exe_, pyinstaller_, cx_Freeze_.
I guess the basic idea is different from these tools, as we try to combine
complete packages with a python minimal distribution: Python + wheel files.
There is no attempt made to search together all the required files, there is
no scan for ``import`` statements etc.

.. _py2exe: http://www.py2exe.org/
.. _pyinstaller: http://www.pyinstaller.org/
.. _cx_Freeze: http://cx-freeze.sourceforge.net/


Scenarios
=========

Distribute an application
    Bundle Python with an application so that users can use it without having
    to install Python.

Common python-minimal package
    Multiple tools can use a common copy of Python. e.g. with a package manager.
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

- run ``compile.bat`` to create ``launcher27.exe``

Usage
=====
for Python 2.7
--------------
In the ``python27`` directory has some examples, e.g. try ``python27/demo1``,
the batch file builds an exe.

Tools
=====
``python27/create_python_minimal.py``
    Used to create a python27-minimal distribution.

``python27/launcher_tool.py``
    A tool to combine scripts with the launcher27.exe.
    A script is added with the name ``__main__.py`` to a zip file. This zip
    file is appended to the exe.

Ideas
=====
The launcher should be customizable. To not require an external file or a
compiler, use Windows resource in the exe. There are resource editor tools
that can be used to change these.

