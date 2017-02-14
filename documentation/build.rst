=======
 Build
=======

.. note::

    The source and wheel releases already contain precompiled exeecutables
    so that this step is usually not needed to use this tool.


Compiling
=========
Compiling requires a mingw gcc compiler (see Requirements_).

Run ``compile_all.bat`` in the ``src`` directory to build all ``launcher.exe``
variants.

The ``python27`` and ``python3`` directories contain the sources and a batch
file. The ``compile_all.bat`` file runs both of them.

The resulting binaries will be placed in the ``launcher_tool`` directory so
that they are available as data files for the Python tool.


Requirements
============

- mingw(-64) GCC compiler, e.g. http://tdm-gcc.tdragon.net/ has one.

The either ``PATH`` must be set so that ``gcc`` can be found or the
``compile*.bat`` files have to be edited (they set ``PATH``).
