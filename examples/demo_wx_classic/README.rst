=========================
 Demo wxPython "classic"
=========================

This demo uses a wxPython "classic" installation to make a small GUI
application. As wxPython "classic" is only available for Python 2 it is
restricted to Python 2.7.

`wx` is copied as package from the system. ``copy_wx.py`` does the copy.

Other dependencies could be installed as wheels (see other examples) but this
demo is reduced to a minimum, just showing wx.

Create the demo using ``make_demo_py27.bat``


Console Window
--------------
A console window is shown at startup of the application. The
``sample_application.py`` uses the launcher API to get rid of that as soon as
the window from wx is shown.


wxPython "Phoenix"
==================
As wxPython "Phoenix" is available as wheels, it should be no problem to build
apps with that by using pip (see other demos for that).
