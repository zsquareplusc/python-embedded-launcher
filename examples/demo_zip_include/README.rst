=============================================
 demo_zip_include - python-embedded-launcher
=============================================

This is an exmaple with depenencies.

- dependencies are cached locally as wheels (``pip wheel -r requirements.txt``)
- the launcher is customized
  - set a different icon
  - (change where python is located)
- copy wheel file *into* attached zip
- the laucher exe is created

see ``make_demo_py27.bat`` and ``make_demo_py3.bat`` which execute these
steps for the respective Python version.


.. note::

    Note that including ZIP files is not officially supported by the wheel
    standard. It will work with many pure Python modules though.
