"""\
A tool to append files to zip which is in turn appended to an other file.
"""
import sys
import zipfile
from StringIO import StringIO

archive_data = StringIO()
with zipfile.ZipFile(archive_data, 'w') as archive:
    archive.write(sys.argv[2], arcname='__main__.py', compress_type=zipfile.ZIP_DEFLATED)

with open(sys.argv[1], 'ab') as exe:
    exe.seek(0, 2)
    exe.write(archive_data.getvalue())


