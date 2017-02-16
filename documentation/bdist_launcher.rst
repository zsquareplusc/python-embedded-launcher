.. _bdist_launcher:

================
 bdist_launcher
================

If setuptools is installed on the development machine, then this command
is automatically registered. It allows to crate executables based on a
``setup.py``.

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

  --icon                  filename of icon to use                           
  --python-minimal        change the location of the python-minimal location
  --extend-sys-path (-p)  add search pattern(s) for files added to sys.path 
                          (separated by ";")                                
  --wait-at-exit          do not close console window automatically         
  --wait-on-error         wait if there is an exception                     
  --bin-dir               put binaries in subdirectory /bin                 

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
``--find-links=wheels --no-index`` when installing (see :ref:`variations`).
