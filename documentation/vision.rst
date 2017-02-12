========
 Vision
========

What's this tool and what it's not
==================================

Distibuting applications on Windows systems usually requires some exe. One may
not wat to burden the user with installing Python and the required extension
modules. So we need a way to package applications with a bundled Python
installation. This is not new... Python's own freeze, py2exe, pyinstaller,
cx_Freeze are examples for tools to do so.

However some of them aim at collecting the minimal set of dependencies on a
file level. While giving small distributions, this also has the problem that
not always all dependencies are identified correctly (dynamic imports, plugin
systems etc.).

Some of them do not fully isolate the distribution from a Python installtion
already present on the system. This is often a problem for the developer, as
finding a suitable test machine required with not Python installed. It may
also lead to import errors on the users system but not on the developers
machine due to this.

Handling the licenses of all dependencies is also not so easy if the tool
just collected the files "randmoly". Identifying which modules were used
may get tricky and sometimes additional modules are collected just because of
some test code or dynamic choice of a package, even if that module is not
required for the application that is packaged.


So the solution is to not scan automatically for dependencies... Today, most
modules specify their dependencies in their ``setup.py`` or in a
``requirements.txt`` file. Disk space is also no issue today so it makes
sense to install dependencies as a whole. PyPi, pip and wheels make this an
easy task nowdays.

This tool does not require a C/C++ compiler to build executables.

It should be possible to run this tool under other operating systems
(currently partially possible, the resource editor is using the windows API
and bundling Python 2.7 uses an existing installation). 


It is
-----
The main purpose is to create an exe that loads Python and then runs a
Python function or module.

It also provides a way to get a minimal Python distribution.

It is not
---------
An installer creator. It only creates a directory with an exe and required
files, not an installer.


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



Scenarios
=========
Distribute an application
    Bundle Python with an application so that users can use it without having
    to install Python.

    By default the launcher searches ``"%SELF%\\python27-minimal"``, so the
    Python distribution is expected at the location of the executable. The
    environment variable ``SELF`` is set automatically by the launcher itself
    (*dirname* of *abspath* of *exe*).


Common python-minimal package
    Multiple tools can use a common copy of Python. e.g. with a package
    manager. Python can be provided as one package and separate application
    packages can use that Python distribution to run.

    The reosurce in the launcher exe needs to be patched to override the
    python location to e.g. ``"%PACKAGE_ROOT%\\python-minimal"``.
    
    This can be done with any resource editor or the included one::

        python -m launcher_tool.resource_editor %DIST%/myapp.exe edit_strings --set 1:^%PACKAGE_ROOT^%\python-minimal
    
    ``bdist_launcher`` has the ``--python-minimal`` command line option to
    override this setting.

