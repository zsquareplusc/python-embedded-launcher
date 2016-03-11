set DIST=dist3
set PYTHONPATH=..\..
set PYTHONUSERBASE=%DIST%
if not exist wheelhouse\pyserial-3.0.1-py3-none-any.whl  python -m pip wheel -w wheelhouse -r requirements.txt
py -3 -m launcher_tool.copy_launcher -o %DIST%/miniterm_py3.exe
REM ~ py -3 -m launcher_tool.resource_editor %DIST%/miniterm_py3.exe edit_strings --set 1:%%LOCALAPPDATA%%\python3-minimal
py -3 -m launcher_tool.resource_editor %DIST%/miniterm_py3.exe write_icon icon.ico
py -3 -m launcher_tool --append-only %DIST%/miniterm_py3.exe -e serial.tools.miniterm:main --add-zip wheelhouse\pyserial-3.0.1-py3-none-any.whl
if not exist %DIST%\python3-minimal   py -3 -m launcher_tool.download_python3_minimal -d %DIST%
