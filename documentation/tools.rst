=======
 Tools
=======

launcher_tool
=============
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
- ``--run-module MODULE``: execute module (similar to ``python -m``)
- ``--main FILE``: use this as ``__main__.py`` instead of built-in code.


launcher_tool.create_python27_minimal
=====================================
Used to create a python27-minimal distribution. It copies the Python
installation from the system.

There is no official "embedded" distribution for Python 2.x so this tool
packages a local copy of Python. It does not package tkinter.


launcher_tool.download_python3_minimal
======================================
Unpack a Python 3 embedded distribution. The data is downloaded from
https://www.python.org/downloads/windows/
and cached locally (so that for repeated runs, it does not need to use
the Internet again). Command line options can be used to select the
desired Python version and architecture.


launcher_tool.copy_launcher
===========================
Copy the ``launcher.exe`` to a file. Used e.g. for customizations using
``launcher_tool.resource_editor``.


launcher_tool.resource_editor
=============================
A small Windows resource editor that can modify the launcher. It uses
Windows API functions to read and write the data (and therefore can
only be run under Windows).

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
