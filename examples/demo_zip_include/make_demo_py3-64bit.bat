set DIST=dist3-64bit
set PYTHONPATH=..\..
set PYTHONUSERBASE=%DIST%
if not exist wheelhouse\pyserial-3.1.1-py2.py3-none-any.whl  python -m pip wheel -w wheelhouse -r requirements.txt
py -3 -m launcher_tool -o %DIST%/miniterm_py3-64.exe --64 -e serial.tools.miniterm:main --icon icon.ico --add-zip wheelhouse\pyserial-3.1.1-py2.py3-none-any.whl
py -3 -m launcher_tool.download_python3_minimal --64 -d %DIST%
