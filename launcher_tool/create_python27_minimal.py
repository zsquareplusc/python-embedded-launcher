#!python
#
# This file is part of https://github.com/zsquareplusc/python-embedded-launcher
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Create a python-minimal distribution.

Start this tool with Python 2.7. It requires that it is installed to copy the
files from there.

You do not need this for Python 3.5, just download the embedded
distribution from the official site instead!
"""
import argparse
import os
import shutil
import sys
import zipfile


def copy_python(destination):
    """\
    Make a copy of Python 2.7. Including standard library (as zip) excluding
    tcl/tk, tests and site-packages. The Python files in the standard library
    are compiled.
    """
    if sys.version_info.major != 2 or sys.version_info.minor != 7:
        raise ValueError('this tool must be run with Python 2.7 itself!')

    python_source = os.path.dirname(sys.executable)
    if not os.path.exists(destination):
        os.makedirs(destination)

    for name in ('python.exe', 'pythonw.exe', 'w9xpopen.exe', 'README.txt',
                 'NEWS.txt', 'LICENSE.txt'):
        shutil.copy2(os.path.join(python_source, name),
                     os.path.join(destination, name))

    dll_excludes = ('tcl85.dll', 'tclpip85.dll', 'tk85.dll', '_tkinter.pyd')
    for name in os.listdir(os.path.join(python_source, 'DLLs')):
        if name not in dll_excludes:
            shutil.copy2(os.path.join(python_source, 'DLLs', name),
                         os.path.join(destination, name))

    # for some reason, this file is somewhere else...
    shutil.copy2(os.path.expandvars('%WINDIR%\\System32\\python27.dll'),
                 os.path.join(destination, 'python27.dll'))

    # zip the standard libarary (no site-packages and no tcl/tk)
    exclude_dirs = ('lib-tk', 'site-packages', 'test', 'tests')
    with zipfile.PyZipFile(os.path.join(destination, 'python27.zip'), 'w',
                           compression=zipfile.ZIP_DEFLATED) as archive:
        zip_root = os.path.join(python_source, 'Lib')
        for root, dirs, files in os.walk(zip_root):
            for directory in exclude_dirs:
                if directory in dirs:
                    dirs.remove(directory)
            for name in files:
                filename = os.path.join(root, name)
                base, ext = os.path.splitext(name)
                if ext == '.py':
                    try:
                        archive.writepy(
                            filename,
                            os.path.dirname(filename[len(os.path.commonprefix([zip_root, filename])):]))
                    except:
                        archive.write(
                            filename,
                            filename[len(os.path.commonprefix([zip_root, filename])):])
                elif ext in ('.pyc', '.pyo'):
                    pass
                else:
                    archive.write(
                        filename,
                        filename[len(os.path.commonprefix([zip_root, filename])):])


def main():
    """Console application entry point"""
    parser = argparse.ArgumentParser(description='extract a copy of python27-minimal')

    group_out = parser.add_argument_group('output options')
    group_out.add_argument('-d', '--directory', metavar='DIR', default='.',
                           help='set a destination directory, a subdirectory NAME will be creted [default: %(default)s]')
    group_out.add_argument('-n', '--name', metavar='NAME', default='python27-minimal',
                           help='Set a directory name [default: %(default)s]')

    args = parser.parse_args()

    copy_python(os.path.join(args.directory, args.name))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    main()
