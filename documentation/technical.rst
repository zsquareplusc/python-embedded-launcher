===================
 Technical Details
===================

Implementation Details
======================
Some random notes...

ASCII/Unicode
-------------
Python 2 uses "ASCII API" while Python 3 uses "Unicode API". That's why
separate code for the two launchers exists.

Console Application
-------------------
The launcher is compiled as console application, so it opens a console window
when started from the explorer. However it is easily closed with a Windows API
call and ``launcher.py``, which is added to the application, has a function for
that. The advantage is, that applications can be started in a console and one
can see the output - and wait for the program to terminate etc.

Python embedded distribution
----------------------------
Starting with Python 3.5, an embedded Python distribution is already available
(and used here) for download, see
https://docs.python.org/3/using/windows.html#embedded-distribution
``launcher_tool.download_python3_minimal`` downloads these.

``Python3.DLL``
---------------
While Python 3 has a ``python3.dll``, which would be nice to use, as it would
make the launcher independent of the Python version -- it won't work.
``Py_SetPath`` is not exposed by that library. As a workaround, the name
of the DLL is searched using the ``FindFirstFile`` Windows function.
Actually the ZIP file is searched (``python3?.zip``) as there is only one
match while ``python3?.dll`` matches ``python3.dll`` and ``python3x.dll``.

Loading Python DLL
------------------
Python is loaded dynamically via ``LoadLibrary``. The launcher is not linked
against the DLL. This has several advantages:

- The launcher does not need to be recompiled for different Python versions,
  current and future (though, it still requires separate launchers for 32/64
  bit and Python 2.x/3.x).
- The location of the DLL can be different to the one of the exe, see
  Subdirectory_ below.
- The separation would also allow to check if the VC runtime is installed and
  direct the user to the download if it is not, but this is not implemented
  yet.

Subdirectory
------------
Why put Python in a subdirectory? Because someone could add the directory
containing the exe to the ``PATH`` and then the system would potentially find
multiple ``python.exe`` and ``pythonXY.dll``...

Resources
---------
Windows resources are used to store settings in the launcher exe. This has the
advantage that these settings can be changed relatively easy with a resource
editor and no compiler is required.

These settings need to be read by the C code of the launcher. So they need
to be easy accessible (to not make the launcher code unnecessarily
complicated). Resources can be accessed via Windows API.

Compiler
--------
GCC is used as its C runtime does not need to be installed first, at least I
never had such a problem. Unlike tools compiled with MSVC, where the exe can
not be loaded if the runtime is not installed so it's not even possible to give
the user directions to fix it or download automatically. A workaround would of
course be, for any compiler, to statically link the C runtime. An other is to
use an installer that takes care if installing the runtime. However the idea
of this tool is, that it is possible to create and use exes without installers.


Other notes
===========
``pip install --user`` installs the packages into a subdirectory
``PythonXY/site-packages`` named after the Python version.

``pip install --prefix=dist`` installs the packages to a subdirectory
``Lib/site-packages``.
