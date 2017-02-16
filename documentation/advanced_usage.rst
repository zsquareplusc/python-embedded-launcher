================
 Advanced Usage
================

Advanced
========
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


.. _variations:

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

A 3rd party tool would be resourcehacker_. It can even edit exe files with
attached zip data without destroying them.

Alternatively use the sources here to recompile the binaries, it really just
needs a mingw gcc (which is only a few dozens of megabytes large). In that case
the ``launcher*.rc`` within the ``src/python*`` directory are edited with a
text editor and ``compile.bat`` is used to recreate the exe.

.. _resourcehacker: http://www.angusj.com/resourcehacker/


Other Resources
===============
- See http://www.lfd.uci.edu/~gohlke/pythonlibs for a cache of many prebuilt
  wheels for Windows of modules with binary components.

- User guide for ``pip``: https://pip.pypa.io/en/stable/
