==========================
 python-embedded-launcher
==========================

For Windows only.

The launcher is a small C program that loads the Python DLL and calls
``Py_Main`` with itself as parameter, loading a zipped Python application
appended to the exe.

Yes, it is yet an other tool to make standalone Windows applications with
Python.

See also py2exe_, pyinstaller_, cx_Freeze_.
I guess the basic idea is different from these tools, as we try to combine
complete packages with a Python minimal distribution: Python + wheel files.
There is no attempt made to search together all the required files, there is
no scan for ``import`` statements etc.

See also pex_, which can grab dependencies from pypi_ and make a zipped
applications, but that does not bundle the Python interpreter.

.. _py2exe: http://www.py2exe.org/
.. _pyinstaller: http://www.pyinstaller.org/
.. _cx_Freeze: http://cx-freeze.sourceforge.net/
.. _pex: https://github.com/pantsbuild/pex
.. _pypi: https://pypi.python.org/pypi


Scenarios
=========

Distribute an application
    Bundle Python with an application so that users can use it without having
    to install Python.

    In ``launcher27.rc`` set ``IDS_PYTHONHOME`` to
    ``"%SELF%\\python27-minimal"`` (this is already the default). This way,
    the Python distribution is expected at the location of the executable. The
    environment variable ``SELF`` is set automatically by the launcher itself
    (*dirname* of *abspath* of *exe*).


Common python-minimal package
    Multiple tools can use a common copy of Python. e.g. with a package
    manager. Python can be provided as one package and separate application
    packages can use that Python distribution to run.

    In ``launcher27.rc`` set ``IDS_PYTHONHOME`` to
    ``"%PACKAGE_ROOT%\\python27-minimal"``. This way, the Python distribution
    is expected to be at a fixed location, where the ``PACKAGE_ROOT`` variable
    points at, it is expected to be set by the package manager.


Usage
=====
The ``example`` directory has demos where these steps are written in a batch
file that is ready to run. The description here explains the steps.
On windows, once Python 3 is installed, the Python Launcher ``py`` is
available, this is what is used here. Otherwise replace ``py -2``/``py -3`` with
``python``/``python3``. When packaging an app, the same Python version that
is packaged, should be used to run the steps here (using ``py -2`` or
``py -3`` accordingly).

Create a Python distribution::

    py -2 create_python27_minimal.py -d dist

or for Python 3::

    py -3 -m launcher_tool.download_python3_minimal -d dist

Use ``pip`` to download and install dependencies, e.g. using a requirements
file (using ``py -2`` or ``py -3``)::

    set PYTHONUSERBASE=dist
    py -m pip install --user --ignore-installed -r requirements.txt

Alternatively, download all dependencies as wheels first, so that subsequent
runs to create a distribution do not need to download from the Internet.

Fetch dependencies once (using ``py -2`` or ``py -3``)::

    py -m pip wheel -r requirements.txt

Then use these with ``--find-links`` and ``--no-index`` options (using
``py -2`` or ``py -3``)::

    set PYTHONUSERBASE=dist
    py -m pip install --user --ignore-installed --find-links=wheelhouse --no-index -r requirements.txt


Write a regular ``setup.py`` script for your application and install it (using
``py -2`` or ``py -3``)::

    set PYTHONUSERBASE=dist
    py setup.py install --user --ignore-installed

Use the launcher tool to write the exe, calling your app (using ``py -2`` or
``py -3``)::

    py launcher_tool.py -o dist/myapp.exe -e mymodule:main


.. note:: pip will also install scripts in a subdirectory called ``Scripts``.
          this usually not needed for a packaged app, so this can be deleted.


Tools
=====
``launcher_tool``
    A tool to combine scripts with the ``launcher27.exe`` or ``launcher3.exe``.
    A script is added with the name ``__main__.py`` to a zip file.
    ``launcher.py`` a helper module for the boot script is also appended
    to the zip. This zip file is appended to the exe.

``launcher_tool.create_python27_minimal``
    Used to create a python27-minimal distribution. It copies the Python
    installation from the system.

``launcher_tool.download_python3_minimal``
    Unpack a Python 3 embedded distribution. The data is downloaded from
    https://www.python.org/downloads/windows/
    and cached locally (so that for repeated runs, it does not need to use
    the Internet again).


Customization
=============
The texts and the location of Python is stored as Windows resource in the
``launcher*.exe``. It is possible to use resource editor tools to patch the
exe. For example resourcehacker_ is such a tool.

Alternatively use the sources here to recompile the binaries, it really just
needs a mingw gcc (which is only a few dozens of megabytes large). In that case
the ``launcher*.rc`` within the ``src/python*`` directory are edited with a
text editor and ``compile.bat`` is used to recreate the exe.

.. _resourcehacker: http://www.angusj.com/resourcehacker/


Build
=====

Requires a mingw gcc compiler (see Requirements_).

Run ``compile_all.bat`` in the ``src`` directory.


The ``python27`` and ``python3`` directories contain the sources and a batch
file. The ``compile_all.bat`` file runs both of them.

The resulting binaries will be placed in the ``launcher_tool`` directory so
that they are available as data files for the Python tool.


Requirements
============
To build applications:

- ``pip`` and ``wheel``
- ``requests`` (for ``download_python3_minimal``)

Running ``pip install -r requirements.txt`` will install these.

To build the launcher exe:

- mingw(-64) GCC compiler, e.g. http://tdm-gcc.tdragon.net/ has one.

The either ``PATH`` must be set so that ``gcc`` can be found or the
``compile*.bat`` files have to be edited (they set ``PATH``).


API
===
A small helper module called ``launcher`` is automatically packaged with the
exe. It contains a few helper functions.

``launcher.patch_sys_path(relative_dirs=('.',))``
    Add directories (relative to exe) to ``sys.path``. The default is to add
    the directory of the exe.

``launcher.add_wheels()``
    Add all ``.whl`` files in the directory ``wheels`` to sys.path. Only works
    for pure Python wheels and only if they do no access the file system to
    load data on their own (should use pkgutil_).

``launcher.restore_sys_argv()``
    Get original command line via Windows API. Restores sys.argv (which is used
    by the launcher to pass the location of Python). This function is called
    by the default boot code (``__main__``).

``launcher.close_console()``
    Useful for GUI applications, it closes a separate console window if there
    is one, e.g. when the exe was started by a double click.

.. _pkgutil: https://docs.python.org/3/library/pkgutil.html


Implementation Details
======================
Some random notes...

Python 2 uses "ASCII API" while Python 3 uses "Unicode API". Thats why separate
code for the two launchers exists.

The launcher is compiled as console application, so it opens a console window
when started from the explorer. However it is easily closed with a Windows API
call and ``launcher.py``, which is added to the application, has a function for
that. The advantage is, that applications can be started in a console and one
can see the output - and wait for the program to terminate etc.

There are currently no 64 bit versions of the launcher. Though compiling them
should be no more than adding a switch to the compiler...

Starting with Python 3.5, an embedded Python distribution is already available
(and used here) for download, see
https://docs.python.org/3/using/windows.html#embedded-distribution

While Python 3 has a ``python3.dll``, which would be nice to use, as it would
make the launcher independent of the Python version -- it won't work.
``Py_SetPath`` is not exposed by that library.

Python is loaded dynamically via ``LoadLibrary``. The launcher is not linked
against the DLL. This has the advantage that the location of the DLL can be
different to the one of the exe and that the DLL name can be provided and
edited as resource (only in ``launcher.exe``). The separation would also allow
to check if the VC runtime is installed and direct the user to the download
if it is not, but this is not implemented yet.

Why put Python in a subdirectory? Because someone could add the directory
containing the exe to the ``PATH`` and then the system would find multiple
``python.exe`` and ``pythonXY.dll``...

``pip --user`` installs the packages into a subdirectory ``PythonXY`` named
after he Python version. We would not need that directory structure, but on the
other side, it's easier that way, so that we do not have to write our own
install/extract code.
