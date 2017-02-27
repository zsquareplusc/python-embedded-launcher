set DIST=dist27
set PYTHONPATH=..\..
set PYTHONUSERBASE=%DIST%
if not exist wheelhouse\pyserial-3.1.1-py2.py3-none-any.whl  python -m pip wheel -w wheelhouse -r requirements.txt
python -m launcher_tool -o %DIST%/miniterm_py27.exe -e serial.tools.miniterm:main --icon icon.ico --add-zip wheelhouse\pyserial-3.1.1-py2.py3-none-any.whl
python -m launcher_tool.create_python27_minimal -d %DIST%
