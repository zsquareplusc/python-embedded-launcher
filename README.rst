==========================
 python-embedded-launcher
==========================

For Windows only.

The launcher is a small C program that loads the Python DLL and calls
``Py_Main`` with itself as parameter, loading a zipped Python application
appended to the exe.

Yes it is yet an other tool to make standalone Windows applications with
Python.

See also py2exe_, pyinstaller_, cx_Freeze_.
I guess the basic idea is different from these tools, as we try to combine
complete packages with a Python minimal distribution: Python + wheel files.
There is no attempt made to search together all the required files, there is
no scan for ``import`` statements etc.

See also pex_, which can grab dependencies from pypi and make a zipped
applications, but that does not bundle the Python interpreter.

.. _py2exe: http://www.py2exe.org/
.. _pyinstaller: http://www.pyinstaller.org/
.. _cx_Freeze: http://cx-freeze.sourceforge.net/
.. _pex: https://github.com/pantsbuild/pex


Scenarios
=========

Distribute an application
    Bundle Python with an application so that users can use it without having
    to install Python.
    
    In ``launcher27.rc`` set ``IDS_PYTHONHOME`` to
    ``"%SELF%\\python27-minimal"``. This way, the Python distribution is
    exepcted at the location of the executable. The environment variable
    ``SELF`` is set automatically by the launcher itself (*dirname* of
    *abspath* of *exe*).


Common python-minimal package
    Multiple tools can use a common copy of Python. e.g. with a package
    manager. Python can be provided as one package and separate application
    packages can use that Python distribution to run.
    
    In ``launcher27.rc`` set ``IDS_PYTHONHOME`` to
    ``"%PACKAGE_ROOT%\\python27-minimal"``. This way, the Python distribution
    is exepcted to be at a fixed location, where the ``PACKAGE_ROOT`` variable
    points at, it is exepcted to be set by the package manager.


Build
=====

for Python 2.7
--------------
In the ``python27`` directory:

- run ``compile.bat`` to create ``launcher27.exe``
- run ``create_python_minimal.py`` to create a Python distribution (see
  examples for usage)


Usage
=====
for Python 2.7
--------------
In the ``python27`` directory has some examples, e.g. try ``python27/demo1``,
the batch file builds an exe.

- run ``create_python_minimal.py`` to create a Python distribution (see
  examples for usage)
- use ``pip`` to download and install dependencies
- use ``launcher_tool.py`` to create exe.


for Python 3
------------
later..

Starting with Python 3.5, an embedded Python distribution is already available
for download at https://www.python.org/downloads/windows/
https://docs.python.org/3/using/windows.html#embedded-distribution


Tools
=====
``python27/create_python_minimal.py``
    Used to create a python27-minimal distribution.

``python27/launcher_tool.py``
    A tool to combine scripts with the launcher27.exe.
    A script is added with the name ``__main__.py`` to a zip file.
    ``launcher.py`` a helper module for the boot script is also appended
    to the zip. This zip file is appended to the exe.


Ideas
=====
The launcher should be customizable. To not require an external file or a
compiler, use Windows resource in the exe. There are resource editor tools
that can be used to change these.


Requirements
============
To build the launcher exe:

- mingw(-64) GCC compiler, e.g. http://tdm-gcc.tdragon.net/ has one.

To build applications:

- ``pip`` and ``wheel``
- tools from this repo
