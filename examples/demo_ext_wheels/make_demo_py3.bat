set DIST=dist3
set PYTHONPATH=..\..
set PYTHONUSERBASE=%DIST%
if not exist wheelhouse\pyserial-3.1.1-py2.py3-none-any.whl  python -m pip wheel -w wheelhouse -r requirements.txt
py -3 -m launcher_tool.copy_launcher -o %DIST%/miniterm_py3.exe
REM ~ py -3 -m launcher_tool.resource_editor %DIST%/miniterm_py3.exe edit_strings --set 1:%%LOCALAPPDATA%%\python3-minimal
py -3 -m launcher_tool.resource_editor %DIST%/miniterm_py3.exe write_icon icon.ico
py -3 -m launcher_tool --append-only %DIST%/miniterm_py3.exe -e serial.tools.miniterm:main --extend-sys-path lib/*.whl
if not exist %DIST%\python3-minimal   py -3 -m launcher_tool.download_python3_minimal -d %DIST%
if not exist %DIST%\lib  mkdir %DIST%\lib
copy wheelhouse\pyserial-3.1.1-py2.py3-none-any.whl %DIST%\lib\
