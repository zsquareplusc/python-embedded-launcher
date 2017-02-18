==========================
 python-embedded-launcher
==========================

An other tool to make standalone Windows applications with Python.

The launcher is a small C program that loads the Python DLL and calls
``Py_Main`` with itself as parameter, loading a zipped Python application
appended to the exe. It isolates the execution from the environment (e.g.
other Python installations on the same machine).

Dependencies are installed with pip. There is no automatic detection or
scanning of source files. Instead, ``setup.py`` (with setuptools'
``install_requires``) or ``requirements.txt`` is used.


Quick Start
===========
- make a ``setup.py`` for your application, use ``scripts`` and/or
  ``entry_points`` for ``console_scripts``
- run ``python setup.py bdist_launcher``

Done. See result in ``dist/launcher*``.

Documentation
=============
See `documentation/index.rst`_ for more details.

.. _`documentation/index.rst`: documentation/index.rst
