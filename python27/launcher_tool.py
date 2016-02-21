"""\
A tool to append files to zip which is in turn appended to an other file.
"""
import sys
import os
import zipfile
import argparse
from StringIO import StringIO
import pkgutil
import shutil

def main():
    parser = argparse.ArgumentParser(description='Launcher assembler')

    parser.add_argument('-o', '--output', metavar='FILE',
                        help='Filename to write the result to')
    parser.add_argument('--launcher', metavar='EXE',
                        help='Launcher executable to use [default: launcher27.exe]')
    parser.add_argument('MAIN', help='Start this script')

    group = parser.add_argument_group('Wheels as dependecies')
    #~ group.add_argument('-i', '--internal-wheel', action='append', default=[],
                       #~ help='Add contents of wheel file to appended zip')
    group.add_argument('-e', '--external-wheel', action='append', default=[],
                       help='Copy wheel file as a whole')
    #~ group.add_argument('-x', '--extract-wheel',  action='append', default=[],
                       #~ help='Extract wheel file (e.g. wheels with binaries)')

    args = parser.parse_args()

    archive_data = StringIO()
    with zipfile.ZipFile(archive_data, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(args.MAIN, arcname='__main__.py')
        archive.writestr('launcher.py', pkgutil.get_data(__name__, 'launcher.py'))
        #~ for wheel in args.internal_wheel:
            

    with open(args.output, 'wb') as exe:
        if args.launcher:
            exe.write(open(args.launcher, 'rb').read())
        else:
            exe.write(pkgutil.get_data(__name__, 'launcher27.exe'))
        exe.write(archive_data.getvalue())

    if args.external_wheel:
        wheel_destination = os.path.join(os.path.dirname(os.path.abspath(args.output)), 'wheels')
        if not os.path.exists(wheel_destination):
            os.mkdir(wheel_destination)
        for wheel in args.external_wheel:
            shutil.copy2(wheel, wheel_destination)
        

if __name__ == '__main__':
    main()
