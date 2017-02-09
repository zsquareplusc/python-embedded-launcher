============================================
 demo_ext_wheels - python-embedded-launcher
============================================

Wheels are copied as-is. While not officially supported by the wheel
standard, the advantage of this setup is, that the wheels can easily be
changed, e.g. updated with newer or custom versions.

This also only works with pure Python modules. Binary extensions (.pyd files)
must still be extracted.


This is an example with dependencies.

- dependencies are cached locally as wheels (``pip wheel -r requirements.txt``)
- the launcher is customized
  - set a different icon
  - (change where Python is located)
- the launcher exe is created
- copy wheel file along the exe

see ``make_demo_py27.bat`` and ``make_demo_py3.bat`` which execute these
steps for the respective Python version.


.. note::

    Note that using zipimport on wheels is not officially supported by the
    wheel standard. It will work with many pure Python modules though.
