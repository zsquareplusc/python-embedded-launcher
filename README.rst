==========================
 python-embedded-launcher
==========================

An other tool to make standalone Windows applications with Python.
For Windows only.

The launcher is a small C program that loads the Python DLL and calls
``Py_Main`` with itself as parameter, loading a zipped Python application
appended to the exe. It isolates the execution from the environment (e.g. other
Python installations on the same machine).

Dependencies are installed with pip. There is no automatic detection or
scanning of source files. Instead, ``setup.py`` (with setuptools'
``install_requires``) or ``requirements.txt`` is used.


Quick Start
===========
- make a ``setup.py`` for your application, use ``scripts`` and/or
  ``entry_points`` for ``console_scripts``
- run ``python setup.py bdist_launcher``

Done. See result in ``dist/launcher*``.


Usage
=====
The simplest way to use this tool is to add a ``setup.py`` to the application
that should be distributed.

::

    setup(
        name="sample_application",
        description="Small sample application for python-embedded-launcher",
        # ...
        packages=[...]
        setup_requires=[...]
        # ...
        entry_points={
            'console_scripts': [
                'app1 = app.core:main',
            ],
        },
        scripts=['scripts/app2'],
    )

Then running ``python setup.py bdist_launcher`` will do the following steps:

- Run ``bdist_wheel`` and then ...
- use that wheel file to install the application and all dependencies to
  a subdirectory within the ``dist`` directory.
- Create executables for all ``scripts`` and ``console_scripts`` entries.  When
  the ``--icon`` option is given, the provided icon will be applied to all
  executables. When the option ``--python-minimal`` is used, then the location
  of the python-minimal directory is overridden and the following step to
  create a copy is skipped.
- Finally, copy/download a ``pythonX-minimal`` distribution to the ``dist``
  directory (that is, unless ``--python-minimal`` was used).

Options for ``bdist_launcher`` command::

    --icon                  filename of icon to use (.ico format)
    --python-minimal        change the location of the python-minimal directory
    --extend-sys-path (-p)  add search pattern(s) for files added to sys.path
                            (separated by ";")
    --wait-at-exit          do not close console window automatically
    --wait-on-error         wait if there is an exception

These options apply to all created launchers (if more than one is generated).

All those options can also be specified in the ``setup.cfg`` file (replace
``-`` with ``_`` in all option names, drop the leading ``--``).

The section that applies globally is called ``[bdist_launcher]`` but for
customization of single files, it is also possible to make such a section per
file, e.g. if an ``example.exe`` is generated, the corresponding section
would be ``[bdist_launcher.example.exe]``.

Note that ``requirements.txt`` is currently not automatically handled. To
install this list of packages, use::

    python -m pip install --prefix=%DIST% --ignore-installed -r ../requirements.txt

with ``%DIST%`` pointing to the folder where the created exe is located.
Optionally, to avoid internet access when using ``pip install``, make a local
cache of wheel files using ``pip wheel ...`` and use
``--find-links=wheels --no-index`` when installing (see "Variations" below).


Advanced Usage
==============
It is also possible to apply the steps to create a distribution manually.

The ``example`` directory has demos where these steps are written in a batch
file that is ready to run. The description here explains the steps.
On Windows, once Python 3 is installed, the Python Launcher ``py`` is
available, this is what is used here. Otherwise replace ``py -2``/``py -3`` with
``python``/``python3``. When packaging an application, the same Python version
that is packaged, should be used to run the steps here (using ``py -2`` or ``py
-3`` accordingly).


Assuming your own project has a ``setup.py``, install to a ``dist`` directory::

    py -m pip install --prefix=dist --ignore-installed /path/to/your/project

Install dependencies::

    py -m pip install --prefix=dist --ignore-installed -r requirements.txt

Create a Python distribution::

    py -2 create_python27_minimal.py -d dist

Or for Python 3::

    py -3 -m launcher_tool.download_python3_minimal -d dist

Use the launcher tool to write the exe, calling your app::

    py -m launcher_tool -o dist/myapp.exe -e mymodule:main


.. note:: pip will also install scripts in a subdirectory called ``Scripts``.
          this usually not needed for a packaged app, so this can be deleted.


Variations
----------
Instead of ``--prefix=dist`` it is also possible to use ``--user`` when the
environment variable ``PYTHONUSERBASE`` is set to ``dist``. This will install
into a slightly different subdirectory of ``dist`` but ``lanucher.py`` also
searches this one.

It is also possible download all dependencies as wheels first, so that
subsequent runs to create a distribution do not need to download from the
Internet (recommended).

Fetch the dependencies once::

    py -m pip wheel -w wheels -r requirements.txt

Then use these with ``--find-links`` and ``--no-index`` options::

    py -m pip install --isolated --prefix=dist --ignore-installed --find-links=wheels --no-index -r requirements.txt


Alternatives
------------
It is also possible to install pip within the embedded Python distribution
and use that distribution itself to install packages::

    py -3 -m launcher_tool.download_python3_minimal
    cd python3-minimal
    python get-pip.py
    python -m pip install --find-links=/path/to/wheels --no-index -r requirements.txt
    cd ..
    py -3 -m launcher_tool -o myapp.exe -e mymodule:main

First we use ``py -3`` to use the systems Python 3, then ``python`` to call
the local version in the directory. The first step is installing pip with
`get-pip.py`_. Then using this to install more packages. Installing from
source may not work, it is recommended to only use wheels for this step.

.. _get-pip.py: https://bootstrap.pypa.io/get-pip.py:


Python 3's ``zipapp`` module can be used to package the application::

    py -3 -m zipapp myapp.py -o myapp.pyz
    py -3 -m launcher_tool -o myapp.exe --run-path myapp.pyz


Tools
=====
``launcher_tool``
    A tool to combine scripts with the ``launcher27.exe`` or ``launcher3.exe``.
    A script is added with the name ``__main__.py`` to a zip file.
    ``launcher.py`` a helper module for the boot script is also appended
    to the zip. This zip file is appended to the exe. Optionally it can also
    include other files too.

    Options to specify the entry point:

    - ``--entry-point MODULE:FUNC``: import given module and call function
    - ``--run-path FILE``: execute given file (e.g. ``.py``, ``.zip``). The
      path is processed using ``os.path.expandvars()``, e.g. ``%SELF%`` will
      be expanded to the directory of the executable.
    - ``--run-module MODULE``: execute module (similar to python -m)
    - ``--main FILE``: use this as ``__main__.py`` instead of built-in code.

``launcher_tool.create_python27_minimal``
    Used to create a python27-minimal distribution. It copies the Python
    installation from the system.

``launcher_tool.download_python3_minimal``
    Unpack a Python 3 embedded distribution. The data is downloaded from
    https://www.python.org/downloads/windows/
    and cached locally (so that for repeated runs, it does not need to use
    the Internet again).

``launcher_tool.copy_launcher``
    Copy the ``launcher.exe`` to a file. Used e.g. for customizations using
    ``launcher_tool.resource_editor``.

``launcher_tool.resource_editor``
    A small Windows resource editor that can modify the launcher. It uses
    Windows API functions to read and write the data.

    - adding and editing strings
    - retrieving and writing icons
    - export resources as (binary) blob
    - removing any resource type
    - adding any resource type is supported partially (currently limited by
      data input possibilities)
    - dump resources
    - dump decoded string table

    Attention!
    It will strip debug data and remove the attached ZIP file! So this tool
    must be used before the application is appended to the launcher.


Customization
=============
The texts and the location of Python is stored as Windows resource in the
``launcher*.exe``. It is possible to use resource editor tools to patch the
exe.

Using ``launcher_tool.resource_editor`` it is possible to make small edits
on the command line, but it does not support all resource types.

E.g. if there was a common Python package installed under ``%LOCALAPPDATA%``
a series of commands like this would create a modified launcher::

    python -m launcher_tool.copy_launcher -o %DIST%/myapp.exe
    python -m launcher_tool.resource_editor %DIST%/myapp.exe edit_strings --set 1:^%LOCALAPPDATA^%\python27-minimal
    python -m launcher_tool.resource_editor %DIST%/myapp.exe write_icon newicon.ico
    python -m launcher_tool --append-only %DIST%/myapp.exe -e mymodule:main

Note that ``^`` is the escape character of ``cmd.exe`` when used interactively
and makes that the ``%`` is not treated specially but as normal text (and the
variable is thus not expanded). For some reason ``%%`` must be used instead of
``^%`` when these lines are put in a ``.bat`` file.

An 3rd party tool would be resourcehacker_. It can even edit exe files with
attached zip data without destroying them.

Alternatively use the sources here to recompile the binaries, it really just
needs a mingw gcc (which is only a few dozens of megabytes large). In that case
the ``launcher*.rc`` within the ``src/python*`` directory are edited with a
text editor and ``compile.bat`` is used to recreate the exe.

.. _resourcehacker: http://www.angusj.com/resourcehacker/


Scenarios
---------
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
    points at. It is expected to be set by the package manager.


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

``launcher.patch_sys_path()``
    Add directories (relative to executable, if existing) to ``sys.path``.

    - the directory of the executable
    - ``Python{py.major}{py.minor}/site-packages``
    - ``Python{py.major}{py.minor}/Lib/site-packages``
    - ``Lib/site-packages``

    These locations are also scanned for ``.pth`` files.

``launcher.extend_sys_path_by_pattern(pattern)``
    Add files matching a pattern (e.g. ``*.zip``, ``*.whl``, ``*.egg``) to
    ``sys.path``. The pattern is prefixed with the location of the executable.
    In case of wheel files, it only works for pure Python wheels and only if
    they do no access the file system to load data on their own (should use
    pkgutil_). This function is used if the command line option
    ``--extend-sys-path`` is used.

``launcher.restore_sys_argv()``
    Get original command line via Windows API. Restores ``sys.argv`` (which is
    used by the launcher to pass the location of Python). This function is
    called by the default boot code (``__main__``).

    Note: Python 2 usually has ``str`` elements in ``sys.argv``, but this
    function sets them to be ``unicode``.

``launcher.close_console()``
    Useful for GUI applications, it closes a separate console window if there
    is one, e.g. when the exe was started by a double click.
    Note that ``sys.stdout``, ``sys.stderr`` and ``sys.stdin`` are replaced
    with a dummy object that ignores ``write()``/``flush()`` and returns
    empty strings on ``read()``.

    Note: some functions may access the std streams, bypassing ``sys.stdXXX```,
    those will fail due to the closed steams.

``launcher.is_separate_console_window()``
    Return true if the console window was opened with this process (e.g.
    the console was opened because the exe was started from the file Explorer).

``hide_console(hide=True)``
    Hides the console window, if one was opened for the process. The function
    can also be called to show the window again. This function is used
    by ``hide_console_until_error()``

``launcher.hide_console_until_error()``
    Hides the console window, if one was opened for the process, but shows the
    console window again when a traceback is printed. ``sys.excepthook`` is
    set by this function and it calls the previous value.

``launcher.wait_at_exit()``
    Wait at exit, but only if console window was opened separately.
    This function is called automatically if the command line option
    ``--wait`` is used.

``launcher.wait_on_error()``
    Wait if the program terminates with an exception, but only if console
    window was opened separately.
    This function is called automatically if the command line option
    ``--wait-on-error`` is used.

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

Starting with Python 3.5, an embedded Python distribution is already available
(and used here) for download, see
https://docs.python.org/3/using/windows.html#embedded-distribution

While Python 3 has a ``python3.dll``, which would be nice to use, as it would
make the launcher independent of the Python version -- it won't work.
``Py_SetPath`` is not exposed by that library. As a workaround, the name
(e.g. ``python35``) is in the resources of ``launcher3.exe`` so that it can
be changed without recompiling.

Python is loaded dynamically via ``LoadLibrary``. The launcher is not linked
against the DLL. This has the advantage that the location of the DLL can be
different to the one of the exe and that the DLL name can be provided and
edited as resource (only in ``launcher.exe``). The separation would also allow
to check if the VC runtime is installed and direct the user to the download
if it is not, but this is not implemented yet.

Why put Python in a subdirectory? Because someone could add the directory
containing the exe to the ``PATH`` and then the system would potentially find
multiple ``python.exe`` and ``pythonXY.dll``...

``pip install --user`` installs the packages into a subdirectory
``PythonXY/site-packages`` named after the Python version.

``pip install --prefix=dist`` installs the packages to a subdirectory
``Lib/site-packages``.


Other Tools
-----------
See also py2exe_, pyinstaller_, cx_Freeze_.
I guess the basic idea is different from these tools, as we try to combine
complete packages with a Python minimal distribution: Python + wheel files.
There is no attempt made to search together all the required files, there is
no scan for ``import`` statements etc.

See also pex_, which can grab dependencies from pypi_ and make zip
applications, but that does not bundle the Python interpreter.

.. _py2exe: http://www.py2exe.org/
.. _pyinstaller: http://www.pyinstaller.org/
.. _cx_Freeze: http://cx-freeze.sourceforge.net/
.. _pex: https://github.com/pantsbuild/pex
.. _pypi: https://pypi.python.org/pypi


Other Resources
===============
- See http://www.lfd.uci.edu/~gohlke/pythonlibs for a cache of many prebuilt
  wheels for Windows of modules with binary components.

- User guide for ``pip``: https://pip.pypa.io/en/stable/
