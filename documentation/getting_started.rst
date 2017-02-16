=================
 Getting Started
=================

Installation
============
::

    python -m pip install python-embedded-launcher

The source code is available at github_.

.. _github: https://github.com/zsquareplusc/python-embedded-launcher


Requirements
------------
To build applications:

- ``pip`` and ``wheel``
- ``requests`` (for ``download_python3_minimal``)

Running ``pip install -r requirements.txt`` will install these.


Quick Start
===========
- make a ``setup.py`` for your application, use ``scripts`` and/or
  ``entry_points`` for ``console_scripts``
- run ``python setup.py bdist_launcher``

Done. See result in ``dist/launcher*``. See :ref:`bdist_launcher` for more
details on this way of using the tool.
