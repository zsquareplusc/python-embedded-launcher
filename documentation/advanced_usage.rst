================
 Advanced Usage
================

``bdist_launcher`` is easy to get started. But it is also possible to apply
the steps to create a distribution manually, which gives more control
over how the distribution will look like.

Distribution types
==================

Extract all Python modules
    This is what ``bdist_launcher`` does and it is the most compatible
    solution. It works with extensions that have binary code / DLLs / PYD
    files.

    It has the drawback that it generates a lot of individual files.

Keep dependencies zipped
    Python can load modules from ZIP files, so for pure Python modules, it
    is possible to put the modules in one or more ZIP files.

    For example, it is possible to:

    - put all the modules in the ZIP file at the end of the exe
    - put all in a separate ZIP file (e.g. useful if there are multiple
      exes with common libraries)
    - use wheel files directly

A mix of those
    It is also possible to mix extracted modules and ZIP files.


Examples
========
The ``example`` directory has demos where these steps are written in a batch
file that is ready to run. The description here explains the steps.

On Windows, once Python 3 is installed, the Python Launcher ``py`` is
available, this is what is used here. Otherwise replace ``py -2``/``py -3``
with ``python``/``python3``. When packaging an application, the same Python
version that is packaged, should be used to run the steps here (using ``py -2``
or ``py -3`` accordingly).


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


Using Wheels directly
=====================
.. note::

    Note that using zipimport on wheels is not officially supported by the
    wheel standard. It will work with many pure Python modules though.

Wheels (``*.whl``) are zip files and most pure Python packages can be kept
zipped in the wheel file, which is added to ``sys.path``. 

Advantages are:

- each dependency has its own wheel file, just one file
- dependencies can be updated to newer versions without rebuilding the app
  (depends on how the launcher was created, e.g. with
  ``--extend-sys-path=*.whl``)

As mentioned, this does not work for binary extensions. It may work with some
modules that the wheels are kept and only the .PYD and .DLL files are extacted.
But it may also be needed to extract the entire module.

There are also pure Python modules that read data files from their package. If
it is using ``pkgutil`` this is not problem. If it is accessing the files
directly, it is also needed to extract these modules.

``*.egg`` files are also ZIP files containing Python modules. They were
designed to be put in ``sys.path`` directly, without extaction. Otherwise
the information from this section should also be applicable to these eggs.


Using pip within the distribution
=================================
It is also possible to install pip within the embedded Python distribution
and use that distribution itself to install packages. Pip is not available
by default but ``get-pip.py`` is provided in the Python 3 embedded
distribution::

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


Python's zipapp
===============
Python 3's ``zipapp`` module can be used to package the application::

    py -3 -m zipapp myapp.py -o myapp.pyz
    py -3 -m launcher_tool -o myapp.exe --run-path myapp.pyz

This setup is useful for cross platform applications. The .pyz file can
be run directly on systems that have Python installed, e.g. GNU/Linux. While
on windows the exe can be used. Note that starting the .pyz file uses the
systems Python installation without any efforrts to separate the application
from the system. So different versions of dependencies may be available etc.


Virtualenv
==========
Virtualenv also has the idea to separate Python installations from each other.
But it's meanto for the local machine / developer etc, not as a means to
distribute applications.

Virtualenvs are not designed to be moved around on the disk (though there is a
command line switch to make them movable). They are not suitable
to create a distribution in combination with the launcher.


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


Cross platform support
======================
With two notable exceptions, all the tools can also be run on non-Windows
machines.

- ``launcher_tool.resource_editor`` uses the Windows API to perform
  modifications, so it can only be run on Windows. This limitation also
  applies to ``bdist_launcher`` which uses this tool, depending on the
  command line switches. (Untested: Wine may support this).

- ``launcher_tool.create_python27_minimal`` copies from an installed Python
  2.7 and therefore needs to be run on Windows (Use Python 3 to avoid this).
  
Though there may be workarounds for that by doing these things only once on
a Windows machine and making the results available to the build machine under
a different OS.

Also note that it may be needed to explicitly state --32/--64 and the Python
Python version instead of using the autodetection. Also if modules are
installed / extracted with ``pip install`` a wrong architecture may be used
(especially for binary extensions where pip would install the version
compatible with the host and not the one for Windows).
  
    

Other Resources
===============
- See http://www.lfd.uci.edu/~gohlke/pythonlibs for a cache of many prebuilt
  wheels for Windows of modules with binary components.

- User guide for ``pip``: https://pip.pypa.io/en/stable/
