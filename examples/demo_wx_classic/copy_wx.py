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

# exclude some big libraries, not commonly used in projects
# note: must use backslash here!
exclude_dirs = (
    'tools\\Editra',    # saves ~12MB
    'tools\\XRCed',     # saves ~1.1MB
    #~ 'locale',           # saves ~4.7MB but then it won't translate a lot of strings
    #~ 'lib\\agw',         # saves ~9MB
    'build',            # saves ~80kB
)

for root, dirs, files in os.walk(wx_source):
    for directory in dirs:
        dirname = os.path.join(root, directory)
        dirname_rel = dirname[1+len(os.path.commonprefix([wx_source, dirname])):]
        if dirname_rel in exclude_dirs:
            sys.stderr.write('skipping {!r}\n'.format(dirname_rel))
            dirs.remove(directory)
    for name in files:
        filename = os.path.join(root, name)
        dst = os.path.join(sys.argv[1], 'wx', filename[1+len(os.path.commonprefix([wx_source, filename])):])
        if not os.path.exists(os.path.dirname(dst)):
            os.makedirs(os.path.dirname(dst))
        shutil.copy2(filename, dst)
