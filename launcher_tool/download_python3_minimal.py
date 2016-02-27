"""
Extract the official python embedded distribution

- download when necessary
- extract a cached version by default
- 32/64 bit selection
- custom URL, force download
"""
import argparse
import platform
import os
import re
import sys
import zipfile
import requests


URL_32 = 'https://www.python.org/ftp/python/3.5.1/python-3.5.1-embed-win32.zip'
URL_64 = 'https://www.python.org/ftp/python/3.5.1/python-3.5.1-embed-amd64.zip'


def main():
    """Console application entry point"""
    parser = argparse.ArgumentParser(description='Launcher assembler')

    parser.add_argument('-d', '--directory', metavar='DIR', default='.',
                        help='Set a destination directory [default: %(default)s]')
    parser.add_argument('-n', '--name', metavar='DIR', default='python3-minimal',
                        help='Set a directory name [default: %(default)s]')
    parser.add_argument('--url', help='override download URL')
    parser.add_argument('--32', dest='bits32', action='store_true', default=False,
                        help='force download of 32 bit version')
    parser.add_argument('--64', dest='bits64', action='store_true', default=False,
                        help='force download of 64 bit version')
    parser.add_argument('-f', '--force-download', action='store_true', default=False,
                        help='force download (ignore/overwrite cached file)')

    args = parser.parse_args()

    #~ print args
    if args.url and (args.bits32 or args.bits64):
        parser.error('--url conflicts with --32 and --64')

    if args.url is None:
        if args.bits32:
            args.url = URL_32
        elif args.bits64:
            args.url = URL_64
        elif platform.architecture()[0] == '64bit':  # autodetect
            args.url = URL_64
        else:
            args.url = URL_32

    python_destination = os.path.join(args.directory, args.name)

    # where to store
    cache_dir = os.path.abspath(os.path.expandvars('%LOCALAPPDATA%/python-embedded-launcher/cache'))  # XXX windows only
    cache_name = os.path.join(cache_dir, re.sub(r'[^\w]', '', args.url))
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    # download
    if not os.path.exists(cache_name) or args.force_download:
        sys.stderr.write('downloading {} to {}\n'.format(args.url, cache_name))
        response = requests.get(args.url, stream=True)
        with open(cache_name, 'wb') as downloaded_data:
            for chunk in response.iter_content(2**20):
                downloaded_data.write(chunk)
    else:
        sys.stderr.write('using cached file {}\n'.format(cache_name))

    if not os.path.exists(cache_name):
        sys.stderr.write('failed to download/lod from cache: file not found: {}\n'.format(cache_name))
        sys.exit(1)

    sys.stderr.write('extracting to {}\n'.format(python_destination))
    with zipfile.ZipFile(cache_name) as archive:
        archive.extractall(python_destination)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    main()
