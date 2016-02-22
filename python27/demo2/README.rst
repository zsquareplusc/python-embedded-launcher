=================================
 python-embedded-launcher - demo
=================================

This is an exmaple for Python 2.7 with depenencies.

See also make_demo.bat_ for a batch file containing the instructions described
here.

Thoughout this document, ``python`` is expected to run the systems Python 2.7
installation.

.. _make_demo.bat: make_demo.bat


Steps
=====

Python Distribution
-------------------
Create a Python minimal distribution (in a directory called ``dist``)::

    python ../create_python_minimal.py -d dist


Install dependencies
--------------------

Use ``pip`` with custom user site::

    set PYTHONUSERBASE=dist
    python -m pip install --user --ignore-installed -r requirements.txt

Alternatively, download all dependencies as wheels first, so that subsequent
runs to create a distribution do not need to download from the internet.

Fetch dependencies once::

    python -m pip wheel -r requirements.txt

Then use these with ``--find-links`` and ``--no-index`` options::

    set PYTHONUSERBASE=dist
    python -m pip install --user --ignore-installed --find-links=wheelhouse --no-index -r requirements.txt

.. note:: pip will also install scripts in a subdirectory called ``Scripts``.
          this usually not needed for a packaged app, so this can be deleted.


Create exe
----------
Run the laucher tool::

    python ../launcher_tool.py -o dist/demo2.exe --main demo2.py

This copies and renames the launcher, appends a zip file to it containing
the given script as ``__main__.py``

The application should now be read in the ``dist`` directory.
