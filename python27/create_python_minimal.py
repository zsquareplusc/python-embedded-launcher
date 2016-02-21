"""\
Create a python-minimal distribution.

Start this tool with Python 2.7. It requires that it is installed to copy the
files from there.

virtualenv could probably also be used to do this job...

You do not need this for Python 3.5, just download the embedded
distribution from the official site instead!
"""
import sys
import os
import shutil
import zipfile

python_source = os.path.dirname(sys.executable)
python_destination = 'python27-minimal'
if not os.path.exists(python_destination):
    os.mkdir(python_destination)

for name in ('python.exe', 'pythonw.exe', 'w9xpopen.exe', 'README.txt', 'NEWS.txt', 'LICENSE.txt'):
    shutil.copy2(os.path.join(python_source, name),
                 os.path.join(python_destination, name))

DLL_EXCLUDES = ('tcl85.dll', 'tclpip85.dll', 'tk85.dll', '_tkinter.pyd')
for name in os.listdir(os.path.join(python_source, 'DLLs')):
    if name not in DLL_EXCLUDES:
        shutil.copy2(os.path.join(python_source, 'DLLs', name),
                     os.path.join(python_destination, name))

# for some reason, this file is somewhere else...
shutil.copy2(os.path.expandvars('%WINDIR%\\System32\\python27.dll'),
             os.path.join(python_destination, 'python27.dll'))

# zip the standard libarary (no site-packages and no tcl/tk)
EXCLUDE_DIRS = ('lib-tk', 'site-packages', 'test')
with zipfile.ZipFile(os.path.join(python_destination, 'python27.zip'), 'w') as archive:
    zip_root = os.path.join(python_source, 'Lib')
    for root, dirs, files in os.walk(zip_root):
        for dir in EXCLUDE_DIRS:
            if dir in dirs:
                dirs.remove(dir)
        for name in files:
            filename = os.path.join(root, name)
            archive.write(
                    filename,
                    filename[len(os.path.commonprefix([zip_root, filename])):],
                    compress_type=zipfile.ZIP_DEFLATED
                    )
