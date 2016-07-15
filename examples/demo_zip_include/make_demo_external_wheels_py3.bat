set DIST=dist3-extwhl
set PYTHONPATH=..\..
set PYTHONUSERBASE=%DIST%
if not exist wheelhouse\pyserial-3.1.1-py2.py3-none-any.whl  python -m pip wheel -w wheelhouse -r requirements.txt
py -3 -m launcher_tool.copy_launcher -o %DIST%/bin/miniterm_py3.exe
py -3 -m launcher_tool.resource_editor %DIST%/bin/miniterm_py3.exe edit_strings --set 1:%%SELF%%\..\python3-minimal
py -3 -m launcher_tool.resource_editor %DIST%/bin/miniterm_py3.exe write_icon icon.ico
py -3 -m launcher_tool --append-only %DIST%/bin/miniterm_py3.exe -e serial.tools.miniterm:main -p ../wheels/*.whl --wait-on-error
mkdir %DIST%\wheels
copy wheelhouse\pyserial-3.1.1-py2.py3-none-any.whl %DIST%\wheels
if not exist %DIST%\python3-minimal   py -3 -m launcher_tool.download_python3_minimal -d %DIST%
