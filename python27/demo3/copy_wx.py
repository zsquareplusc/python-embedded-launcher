"""
wxPython does not provide a wheel file, just an exe installer, for "classic"
releases (the Phoenix version is available as wheel).

copy wxPython from an installation on the system.
"""
import sys
import os
import shutil
import zipfile

import wx
wx_source = os.path.dirname(wx.__file__)
wx_name = os.path.basename(os.path.dirname(wx_source))

for root, dirs, files in os.walk(wx_source):
    for name in files:
        filename = os.path.join(root, name)
        dst = os.path.join(wx_name, 'wx', filename[1+len(os.path.commonprefix([wx_source, filename])):])
        if not os.path.exists(os.path.dirname(dst)):
            os.makedirs(os.path.dirname(dst))
        shutil.copy2(filename, dst)
