set DIST=dist3-extwhl
set PYTHONPATH=..\..
set PYTHONUSERBASE=%DIST%
if not exist wheelhouse\pyserial-3.0.1-py3-none-any.whl  python -m pip wheel -w wheelhouse -r requirements.txt
py -3 -m launcher_tool -o %DIST%/miniterm_py3.exe -e serial.tools.miniterm:main -p *.whl --wait-on-error
copy wheelhouse\pyserial-3.0.1-py3-none-any.whl %DIST%
if not exist %DIST%\python3-minimal   py -3 -m launcher_tool.download_python3_minimal -d %DIST%
